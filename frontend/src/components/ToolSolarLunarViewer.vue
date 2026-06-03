<script setup>
import { computed, ref, watch } from "vue";

import {
  formatReadableDate,
  getDayOfYear,
  getLunarDayLabel,
  getLunarMonthDays,
  getLunarMonthOptions,
  getSupportedLunarYearRange,
  getWeekOfYear,
  lunarToSolar,
  parseDateInputValue,
  solarToLunar,
  toDateInputValue,
} from "../utils/time-tools.js";
import GlassSelect from "./GlassSelect.vue";

defineProps({
  tool: {
    type: Object,
    required: true,
  },
});

const mode = ref("solar");
const selectedDate = ref(toDateInputValue(new Date()));
const supportedRange = getSupportedLunarYearRange();
const todayLunar = solarToLunar(new Date()) || { year: 2026, month: 1, day: 1, isLeap: false };
const lunarYear = ref(todayLunar.year);
const lunarMonthValue = ref(`${todayLunar.month}:${todayLunar.isLeap ? 1 : 0}`);
const lunarDayValue = ref(String(todayLunar.day));
const modeItems = [
  { key: "solar", label: "依据公历看农历" },
  { key: "lunar", label: "依据农历看公历" },
];

const lunarMonthOptions = computed(() =>
  getLunarMonthOptions(lunarYear.value).map((item) => ({
    value: item.value,
    label: item.label,
    description: item.isLeap ? "闰月" : "农历月份",
  })),
);

const selectedLunarMonth = computed(() => {
  const [monthValue, leapValue] = String(lunarMonthValue.value || "1:0").split(":");
  return {
    month: Number(monthValue) || 1,
    isLeap: leapValue === "1",
  };
});

const lunarDayOptions = computed(() => {
  const days = getLunarMonthDays(lunarYear.value, selectedLunarMonth.value.month, selectedLunarMonth.value.isLeap);
  return Array.from({ length: days }, (_, index) => {
    const day = index + 1;
    return {
      value: String(day),
      label: getLunarDayLabel(day),
    };
  });
});

watch(lunarMonthOptions, (options) => {
  if (!options.some((item) => item.value === lunarMonthValue.value)) {
    lunarMonthValue.value = options[0]?.value || "1:0";
  }
});

watch([lunarYear, lunarMonthValue, lunarDayOptions], () => {
  const maxDay = lunarDayOptions.value.length;
  const currentDay = Number(lunarDayValue.value);
  if (!maxDay) {
    lunarDayValue.value = "1";
    return;
  }
  if (!currentDay || currentDay > maxDay) {
    lunarDayValue.value = String(maxDay);
  }
});

function buildResultFromSolar(date) {
  const lunar = solarToLunar(date);
  if (!lunar) {
    return { error: `当前仅支持 ${supportedRange.min} - ${supportedRange.max} 年之间的日期` };
  }
  return {
    sourceLabel: "公历日期",
    targetLabel: "农历日期",
    source: formatReadableDate(date),
    sourceSub: toDateInputValue(date),
    target: lunar.full,
    targetSub: lunar.yearLabel,
    stemBranch: `${lunar.stemBranch}年`,
    zodiac: `${lunar.zodiac}年`,
    quarter: `第 ${Math.floor(date.getMonth() / 3) + 1} 季度`,
    dayOfYear: getDayOfYear(date),
    weekOfYear: getWeekOfYear(date),
  };
}

function buildResultFromLunar() {
  const year = Number(lunarYear.value);
  const day = Number(lunarDayValue.value);
  const { month, isLeap } = selectedLunarMonth.value;
  const solarDate = lunarToSolar(year, month, day, isLeap);
  if (!solarDate) {
    return { error: `请输入 ${supportedRange.min} - ${supportedRange.max} 年之间有效的农历日期` };
  }
  const lunar = solarToLunar(solarDate);
  return {
    sourceLabel: "农历日期",
    targetLabel: "对应公历",
    source: lunar?.full || `农历${year}年${isLeap ? "闰" : ""}${month}月${day}日`,
    sourceSub: lunar?.yearLabel || "",
    target: formatReadableDate(solarDate),
    targetSub: toDateInputValue(solarDate),
    stemBranch: lunar?.stemBranch ? `${lunar.stemBranch}年` : "待识别",
    zodiac: lunar?.zodiac ? `${lunar.zodiac}年` : "待识别",
    quarter: `第 ${Math.floor(solarDate.getMonth() / 3) + 1} 季度`,
    dayOfYear: getDayOfYear(solarDate),
    weekOfYear: getWeekOfYear(solarDate),
  };
}

const result = computed(() => {
  if (mode.value === "lunar") {
    return buildResultFromLunar();
  }
  const date = parseDateInputValue(selectedDate.value);
  if (!date) {
    return { error: "请选择一个日期" };
  }
  return buildResultFromSolar(date);
});
</script>

<template>
  <section class="tool-form time-tool-shell">
    <div class="solar-lunar-mode" role="group" aria-label="转换方向">
      <button v-for="item in modeItems" :key="item.key" type="button" :class="{ active: mode === item.key }" @click="mode = item.key">
        {{ item.label }}
      </button>
    </div>

    <label v-if="mode === 'solar'" class="time-tool-label">
      <span>公历日期</span>
      <input v-model="selectedDate" type="date" />
    </label>

    <section v-else class="solar-lunar-lunar-inputs">
      <label class="time-tool-label">
        <span>农历年份</span>
        <input v-model.number="lunarYear" type="number" :min="supportedRange.min" :max="supportedRange.max" />
      </label>
      <label class="time-tool-label">
        <span>农历月份</span>
        <GlassSelect v-model="lunarMonthValue" :options="lunarMonthOptions" placeholder="选择农历月份" />
      </label>
      <label class="time-tool-label">
        <span>农历日期</span>
        <GlassSelect v-model="lunarDayValue" :options="lunarDayOptions" :disabled="!lunarDayOptions.length" placeholder="选择农历日期" />
      </label>
    </section>

    <section v-if="result.error" class="time-tool-empty">{{ result.error }}</section>
    <section v-else class="time-tool-grid">
      <article class="time-tool-card wide">
        <span>{{ result.sourceLabel }}</span>
        <strong>{{ result.source }}</strong>
        <small>{{ result.sourceSub }}</small>
      </article>
      <article class="time-tool-card wide">
        <span>{{ result.targetLabel }}</span>
        <strong>{{ result.target }}</strong>
        <small>{{ result.targetSub }}</small>
      </article>
      <article class="time-tool-card">
        <span>干支年</span>
        <strong>{{ result.stemBranch }}</strong>
      </article>
      <article class="time-tool-card">
        <span>生肖</span>
        <strong>{{ result.zodiac }}</strong>
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
