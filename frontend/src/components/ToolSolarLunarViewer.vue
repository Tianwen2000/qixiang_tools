<script setup>
import { computed, ref } from "vue";

import { formatReadableDate, getDayOfYear, getLunarInfo, getWeekOfYear, parseDateInputValue, toDateInputValue } from "../utils/time-tools.js";

defineProps({
  tool: {
    type: Object,
    required: true,
  },
});

const selectedDate = ref(toDateInputValue(new Date()));

const result = computed(() => {
  const date = parseDateInputValue(selectedDate.value);
  if (!date) {
    return { error: "请选择一个日期" };
  }
  return {
    solar: formatReadableDate(date),
    lunar: getLunarInfo(date).full,
    quarter: `第 ${Math.floor(date.getMonth() / 3) + 1} 季度`,
    dayOfYear: getDayOfYear(date),
    weekOfYear: getWeekOfYear(date),
    iso: date.toISOString().slice(0, 10),
  };
});
</script>

<template>
  <section class="tool-form time-tool-shell">
    <label class="time-tool-label">
      <span>公历日期</span>
      <input v-model="selectedDate" type="date" />
    </label>

    <section v-if="result.error" class="time-tool-empty">{{ result.error }}</section>
    <section v-else class="time-tool-grid">
      <article class="time-tool-card wide">
        <span>公历日期</span>
        <strong>{{ result.solar }}</strong>
        <small>{{ result.iso }}</small>
      </article>
      <article class="time-tool-card wide">
        <span>农历日期</span>
        <strong>{{ result.lunar }}</strong>
        <small>{{ result.quarter }}</small>
      </article>
      <article class="time-tool-card">
        <span>年内天数</span>
        <strong>{{ result.dayOfYear }}</strong>
      </article>
      <article class="time-tool-card">
        <span>周序号</span>
        <strong>第 {{ result.weekOfYear }} 周</strong>
      </article>
    </section>
  </section>
</template>
