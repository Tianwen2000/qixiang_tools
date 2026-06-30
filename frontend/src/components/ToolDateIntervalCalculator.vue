<script setup>
// 文件说明：定义 ToolDateIntervalCalculator 前端组件。
import { computed, ref } from "vue";

import {
  addDays,
  computeCalendarDiff,
  countWeekdays,
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
const startDate = ref(toDateInputValue(today));
const endDate = ref(toDateInputValue(addDays(today, 30)));
const inclusive = ref(false);

const result = computed(() => {
  const start = parseDateInputValue(startDate.value);
  const end = parseDateInputValue(endDate.value);
  if (!start || !end) {
    return { error: "请先选择开始和结束日期" };
  }
  const dayDiff = Math.abs(Math.round((end.getTime() - start.getTime()) / 86400000));
  const totalDays = dayDiff + (inclusive.value ? 1 : 0);
  const calendar = computeCalendarDiff(start, end);
  return {
    totalDays,
    totalWeeks: (totalDays / 7).toFixed(2),
    weekdays: countWeekdays(start, end, inclusive.value),
    calendar,
  };
});
</script>

<template>
  <section class="tool-form time-tool-shell">
    <label class="time-tool-label">
      <span>开始日期</span>
      <input v-model="startDate" type="date" />
    </label>

    <label class="time-tool-label">
      <span>结束日期</span>
      <input v-model="endDate" type="date" />
    </label>

    <label class="time-tool-toggle">
      <input v-model="inclusive" type="checkbox" />
      <span>包含结束日期一起计算</span>
    </label>

    <section v-if="result.error" class="time-tool-empty">{{ result.error }}</section>
    <section v-else class="time-tool-grid">
      <article class="time-tool-card">
        <span>相差天数</span>
        <strong>{{ result.totalDays }}</strong>
      </article>
      <article class="time-tool-card">
        <span>相差周数</span>
        <strong>{{ result.totalWeeks }}</strong>
      </article>
      <article class="time-tool-card">
        <span>工作日</span>
        <strong>{{ result.weekdays }}</strong>
      </article>
      <article class="time-tool-card wide">
        <span>自然历差</span>
        <strong>{{ result.calendar.years }} 年 {{ result.calendar.months }} 月 {{ result.calendar.days }} 天</strong>
      </article>
    </section>
  </section>
</template>
