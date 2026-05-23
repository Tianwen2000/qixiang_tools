<script setup>
import { computed, ref } from "vue";

import {
  formatReadableDate,
  getChineseYearName,
  getChineseZodiac,
  getLunarInfo,
  getWesternZodiac,
  parseDateInputValue,
  toDateInputValue,
} from "../utils/time-tools.js";

defineProps({
  tool: {
    type: Object,
    required: true,
  },
});

const birthDate = ref(toDateInputValue(new Date(1998, 5, 15)));

const result = computed(() => {
  const date = parseDateInputValue(birthDate.value);
  if (!date) {
    return { error: "请选择生日" };
  }
  return {
    solar: formatReadableDate(date),
    lunar: getLunarInfo(date).full,
    zodiac: getChineseZodiac(date),
    stemBranch: getChineseYearName(date),
    western: getWesternZodiac(date),
    weekday: new Intl.DateTimeFormat("zh-CN", { weekday: "long" }).format(date),
  };
});
</script>

<template>
  <section class="tool-form time-tool-shell">
    <label class="time-tool-label">
      <span>生日</span>
      <input v-model="birthDate" type="date" />
    </label>

    <section v-if="result.error" class="time-tool-empty">{{ result.error }}</section>
    <section v-else class="time-tool-grid">
      <article class="time-tool-card wide">
        <span>生日</span>
        <strong>{{ result.solar }}</strong>
        <small>{{ result.lunar }}</small>
      </article>
      <article class="time-tool-card">
        <span>生肖</span>
        <strong>{{ result.zodiac ? `${result.zodiac}年` : "待识别" }}</strong>
      </article>
      <article class="time-tool-card">
        <span>星座</span>
        <strong>{{ result.western || "待识别" }}</strong>
      </article>
      <article class="time-tool-card">
        <span>干支年</span>
        <strong>{{ result.stemBranch ? `${result.stemBranch}年` : "待识别" }}</strong>
      </article>
      <article class="time-tool-card">
        <span>星期</span>
        <strong>{{ result.weekday }}</strong>
      </article>
    </section>
  </section>
</template>
