<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from "vue";

import { holidaySchedulesByYear } from "../utils/time-datasets.js";

defineProps({
  tool: {
    type: Object,
    required: true,
  },
});

const currentMs = ref(Date.now());
const supportedYears = Object.keys(holidaySchedulesByYear)
  .map((value) => Number(value))
  .sort((left, right) => left - right);
const beijingYearFormatter = new Intl.DateTimeFormat("zh-CN", {
  timeZone: "Asia/Shanghai",
  year: "numeric",
});

let refreshTimer = null;

function getBeijingYear(timestamp) {
  const yearPart = beijingYearFormatter.formatToParts(new Date(timestamp)).find((item) => item.type === "year")?.value;
  const year = Number(yearPart);
  if (Number.isFinite(year)) {
    return year;
  }
  return new Date(timestamp + 8 * 3600000).getUTCFullYear();
}

const activeYear = computed(() => getBeijingYear(currentMs.value));
const activeSchedule = computed(() => holidaySchedulesByYear[activeYear.value] || []);
const currentYearSupported = computed(() => activeSchedule.value.length > 0);
const nearestSupportedYear = computed(() => {
  if (!supportedYears.length) {
    return null;
  }
  return supportedYears.reduce((closest, year) => {
    if (closest === null) {
      return year;
    }
    return Math.abs(year - activeYear.value) < Math.abs(closest - activeYear.value) ? year : closest;
  }, null);
});

const cards = computed(() =>
  activeSchedule.value.map((item) => {
    const start = new Date(`${item.start}T00:00:00+08:00`).getTime();
    const end = new Date(`${item.end}T23:59:59+08:00`).getTime();
    let status = "未到";
    let hint = `还有 ${Math.ceil((start - currentMs.value) / 86400000)} 天开始`;
    if (currentMs.value >= start && currentMs.value <= end) {
      status = "进行中";
      hint = `还有 ${Math.max(0, Math.ceil((end - currentMs.value) / 86400000))} 天结束`;
    } else if (currentMs.value > end) {
      status = "已过";
      hint = `已过去 ${Math.floor((currentMs.value - end) / 86400000)} 天`;
    }
    return {
      ...item,
      range: `${item.start.slice(5).replace("-", "/")} - ${item.end.slice(5).replace("-", "/")}`,
      workdayText: item.workdays.length ? `调休上班：${item.workdays.map((value) => value.slice(5).replace("-", "/")).join("、")}` : "无调休上班",
      status,
      hint,
    };
  }),
);

onMounted(() => {
  refreshTimer = window.setInterval(() => {
    currentMs.value = Date.now();
  }, 60_000);
});

onBeforeUnmount(() => {
  if (refreshTimer) {
    window.clearInterval(refreshTimer);
  }
});
</script>

<template>
  <section class="tool-form time-tool-shell">
    <section class="time-tool-note">
      <strong>{{ activeYear }} 年放假安排</strong>
      <p>会按当前公历年份自动识别；如果该年份的官方节假日安排还没收录，就会直接提示等待更新。</p>
    </section>

    <section v-if="!currentYearSupported" class="time-tool-note">
      <strong>{{ activeYear }} 年安排暂未收录</strong>
      <p>
        当前页面已经自动识别到公历 {{ activeYear }} 年，但这年的国务院节假日安排还没有加入本站数据。
        <span v-if="nearestSupportedYear">当前最近可查看的是 {{ nearestSupportedYear }} 年。</span>
      </p>
    </section>

    <section v-else class="time-tool-list">
      <article v-for="item in cards" :key="item.name" class="time-tool-list-item">
        <div class="time-tool-list-head">
          <strong>{{ item.name }}</strong>
          <span class="time-tool-pill" :class="{ active: item.status === '进行中', muted: item.status === '已过' }">
            {{ item.status }}
          </span>
        </div>
        <small>{{ item.range }} · {{ item.totalDays }} 天</small>
        <small>{{ item.summary }}</small>
        <small>{{ item.workdayText }}</small>
        <small>{{ item.hint }}</small>
      </article>
    </section>
  </section>
</template>
