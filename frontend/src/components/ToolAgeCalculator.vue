<script setup>
import { computed, ref } from "vue";

import {
  addYears,
  computeCalendarDiff,
  formatReadableDate,
  parseDateInputValue,
  toDateInputValue,
} from "../utils/time-tools.js";

defineProps({
  tool: {
    type: Object,
    required: true,
  },
});

const today = new Date();
const birthDate = ref("1998-06-15");
const referenceDate = ref(toDateInputValue(today));

const result = computed(() => {
  const birth = parseDateInputValue(birthDate.value);
  const reference = parseDateInputValue(referenceDate.value);
  if (!birth || !reference) {
    return { error: "请先选择出生日期和参考日期" };
  }
  const diff = computeCalendarDiff(birth, reference);
  const totalDays = Math.max(0, Math.round((reference - birth) / 86400000));
  let nextBirthday = new Date(reference.getFullYear(), birth.getMonth(), birth.getDate());
  if (nextBirthday < reference) {
    nextBirthday = addYears(nextBirthday, 1);
  }
  return {
    totalDays,
    ageLabel: `${diff.years} 岁 ${diff.months} 月 ${diff.days} 天`,
    nextBirthday: formatReadableDate(nextBirthday),
    daysUntilBirthday: Math.round((nextBirthday - reference) / 86400000),
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
        <span>当前年龄</span>
        <strong>{{ result.ageLabel }}</strong>
        <small>共经历 {{ result.totalDays }} 天</small>
      </article>
      <article class="time-tool-card">
        <span>下次生日</span>
        <strong>{{ result.nextBirthday }}</strong>
      </article>
      <article class="time-tool-card">
        <span>距离生日</span>
        <strong>{{ result.daysUntilBirthday }} 天</strong>
      </article>
    </section>
  </section>
</template>
