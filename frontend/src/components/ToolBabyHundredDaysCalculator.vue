<script setup>
// 文件说明：定义 ToolBabyHundredDaysCalculator 前端组件。
import { computed, ref } from "vue";

import { addDays, addYears, computeCalendarDiff, formatReadableDate, parseDateInputValue, toDateInputValue } from "../utils/time-tools.js";

defineProps({
  tool: {
    type: Object,
    required: true,
  },
});

const today = new Date();
const birthDate = ref(toDateInputValue(addDays(today, -36)));
const referenceDate = ref(toDateInputValue(today));

const result = computed(() => {
  const birth = parseDateInputValue(birthDate.value);
  const reference = parseDateInputValue(referenceDate.value);
  if (!birth || !reference) {
    return { error: "请先填写出生日期和参考日期" };
  }
  const livedDays = Math.round((reference - birth) / 86400000);
  if (livedDays < 0) {
    return { error: "参考日期不能早于出生日期" };
  }
  const diff = computeCalendarDiff(birth, reference);
  return {
    livedDays,
    ageLabel: `${diff.years * 12 + diff.months} 月 ${diff.days} 天`,
    fullMonthDate: formatReadableDate(addDays(birth, 30)),
    hundredDaysDate: formatReadableDate(addDays(birth, 100)),
    firstBirthday: formatReadableDate(addYears(birth, 1)),
    untilHundredDays: Math.max(0, Math.round((addDays(birth, 100) - reference) / 86400000)),
  };
});
</script>

<template>
  <section class="tool-form time-tool-shell">
    <label class="time-tool-label">
      <span>出生日期</span>
      <input v-model="birthDate" type="date" />
    </label>

    <label class="time-tool-label">
      <span>参考日期</span>
      <input v-model="referenceDate" type="date" />
    </label>

    <section v-if="result.error" class="time-tool-empty">{{ result.error }}</section>
    <section v-else class="time-tool-grid">
      <article class="time-tool-card wide">
        <span>当前成长</span>
        <strong>已出生 {{ result.livedDays }} 天</strong>
        <small>{{ result.ageLabel }}</small>
      </article>
      <article class="time-tool-card">
        <span>满月</span>
        <strong>{{ result.fullMonthDate }}</strong>
      </article>
      <article class="time-tool-card">
        <span>百日</span>
        <strong>{{ result.hundredDaysDate }}</strong>
      </article>
      <article class="time-tool-card">
        <span>周岁</span>
        <strong>{{ result.firstBirthday }}</strong>
      </article>
      <article class="time-tool-card">
        <span>距百日</span>
        <strong>{{ result.untilHundredDays }} 天</strong>
      </article>
    </section>
  </section>
</template>
