<script setup>
// 文件说明：定义 ToolPregnancyDueCalculator 前端组件。
import { computed, ref } from "vue";

import { addDays, formatReadableDate, parseDateInputValue, toDateInputValue } from "../utils/time-tools.js";

defineProps({
  tool: {
    type: Object,
    required: true,
  },
});

const today = new Date();
const lmpDate = ref(toDateInputValue(addDays(today, -84)));
const cycleLength = ref(28);
const referenceDate = ref(toDateInputValue(today));

const result = computed(() => {
  const lmp = parseDateInputValue(lmpDate.value);
  const reference = parseDateInputValue(referenceDate.value);
  const cycle = Number(cycleLength.value);
  if (!lmp || !reference) {
    return { error: "请先填写末次月经和参考日期" };
  }
  if (!Number.isFinite(cycle) || cycle < 21 || cycle > 45) {
    return { error: "月经周期建议填写在 21 到 45 天之间" };
  }
  const elapsedDays = Math.round((reference - lmp) / 86400000);
  if (elapsedDays < 0) {
    return { error: "参考日期不能早于末次月经日期" };
  }
  const dueDate = addDays(lmp, 280 + (cycle - 28));
  const weeks = Math.floor(elapsedDays / 7);
  const days = elapsedDays % 7;
  let stage = "孕早期";
  if (weeks >= 13 && weeks < 28) {
    stage = "孕中期";
  } else if (weeks >= 28) {
    stage = "孕晚期";
  }
  const remaining = Math.round((dueDate - reference) / 86400000);
  return {
    dueDate: formatReadableDate(dueDate),
    weeks,
    days,
    stage,
    elapsedDays,
    remaining,
  };
});
</script>

<template>
  <section class="tool-form time-tool-shell">
    <label class="time-tool-label">
      <span>末次月经日期</span>
      <input v-model="lmpDate" type="date" />
    </label>

    <label class="time-tool-label">
      <span>月经周期</span>
      <input v-model="cycleLength" type="number" min="21" max="45" />
    </label>

    <label class="time-tool-label">
      <span>参考日期</span>
      <input v-model="referenceDate" type="date" />
    </label>

    <section v-if="result.error" class="time-tool-empty">{{ result.error }}</section>
    <section v-else class="time-tool-grid">
      <article class="time-tool-card wide">
        <span>当前孕周</span>
        <strong>{{ result.weeks }} 周 {{ result.days }} 天</strong>
        <small>{{ result.stage }} · 已经过 {{ result.elapsedDays }} 天</small>
      </article>
      <article class="time-tool-card">
        <span>预产期</span>
        <strong>{{ result.dueDate }}</strong>
      </article>
      <article class="time-tool-card">
        <span>距离预产期</span>
        <strong>{{ result.remaining >= 0 ? `${result.remaining} 天` : `已超过 ${Math.abs(result.remaining)} 天` }}</strong>
      </article>
    </section>
  </section>
</template>
