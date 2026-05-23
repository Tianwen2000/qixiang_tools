<script setup>
import { computed, ref } from "vue";

import {
  addDays,
  formatReadableDate,
  getDayOfYear,
  getLunarInfo,
  getWeekOfYear,
  startOfMonth,
  toDateInputValue,
} from "../utils/time-tools.js";

defineProps({
  tool: {
    type: Object,
    required: true,
  },
});

const now = new Date();
const cursor = ref(startOfMonth(now));
const selectedDate = ref(toDateInputValue(now));
const weekLabels = ["一", "二", "三", "四", "五", "六", "日"];

function buildCalendarGrid(monthDate, selectedValue) {
  const firstDay = startOfMonth(monthDate);
  const weekStart = (firstDay.getDay() + 6) % 7;
  const gridStart = addDays(firstDay, -weekStart);
  const todayKey = toDateInputValue(new Date());
  return Array.from({ length: 42 }, (_, index) => {
    const date = addDays(gridStart, index);
    const key = toDateInputValue(date);
    return {
      key,
      date,
      day: date.getDate(),
      lunar: getLunarInfo(date).short,
      isCurrentMonth: date.getMonth() === monthDate.getMonth(),
      isToday: key === todayKey,
      isSelected: key === selectedValue,
    };
  });
}

const calendarTitle = computed(() => `${cursor.value.getFullYear()} 年 ${cursor.value.getMonth() + 1} 月`);
const calendarCells = computed(() => buildCalendarGrid(cursor.value, selectedDate.value));
const selectedInfo = computed(() => {
  const target = calendarCells.value.find((item) => item.key === selectedDate.value)?.date;
  if (!target) {
    return null;
  }
  return {
    solar: formatReadableDate(target),
    lunar: getLunarInfo(target).full,
    dayOfYear: getDayOfYear(target),
    weekOfYear: getWeekOfYear(target),
  };
});

function shiftMonth(offset) {
  cursor.value = new Date(cursor.value.getFullYear(), cursor.value.getMonth() + offset, 1);
}

function jumpToToday() {
  const today = new Date();
  cursor.value = startOfMonth(today);
  selectedDate.value = toDateInputValue(today);
}
</script>

<template>
  <section class="tool-form time-tool-shell">
    <div class="time-tool-actions">
      <button type="button" class="secondary-button" @click="shiftMonth(-1)">上个月</button>
      <button type="button" @click="jumpToToday">回到本月</button>
      <button type="button" class="secondary-button" @click="shiftMonth(1)">下个月</button>
    </div>

    <label class="time-tool-label">
      <span>选中日期</span>
      <input v-model="selectedDate" type="date" />
    </label>

    <section class="time-tool-calendar">
      <div class="time-tool-calendar-head">
        <h4>{{ calendarTitle }}</h4>
        <span>{{ selectedInfo?.lunar || "点击日期查看详情" }}</span>
      </div>
      <div class="time-tool-calendar-week">
        <span v-for="label in weekLabels" :key="label">{{ label }}</span>
      </div>
      <div class="time-tool-calendar-grid">
        <button
          v-for="cell in calendarCells"
          :key="cell.key"
          type="button"
          class="time-tool-calendar-cell"
          :class="{ muted: !cell.isCurrentMonth, today: cell.isToday, active: cell.isSelected }"
          @click="selectedDate = cell.key"
        >
          <strong>{{ cell.day }}</strong>
          <small>{{ cell.lunar }}</small>
        </button>
      </div>
    </section>

    <section v-if="selectedInfo" class="time-tool-grid">
      <article class="time-tool-card wide">
        <span>选中日期</span>
        <strong>{{ selectedInfo.solar }}</strong>
        <small>{{ selectedInfo.lunar }}</small>
      </article>
      <article class="time-tool-card">
        <span>年内天数</span>
        <strong>{{ selectedInfo.dayOfYear }}</strong>
      </article>
      <article class="time-tool-card">
        <span>周序号</span>
        <strong>第 {{ selectedInfo.weekOfYear }} 周</strong>
      </article>
    </section>
  </section>
</template>
