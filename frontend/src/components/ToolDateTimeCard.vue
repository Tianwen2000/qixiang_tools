<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from "vue";

import { getBeijingTime } from "../api/tools.js";

const props = defineProps({
  compact: {
    type: Boolean,
    default: false,
  },
});

const timeSnapshot = ref(null);
const nowMs = ref(0);
const loading = ref(true);
const error = ref("");

let baseServerMs = 0;
let basePerfMs = 0;
let tickTimer = null;
let syncTimer = null;
let lastDateKey = "";
const lunarDayLabels = [
  "",
  "初一",
  "初二",
  "初三",
  "初四",
  "初五",
  "初六",
  "初七",
  "初八",
  "初九",
  "初十",
  "十一",
  "十二",
  "十三",
  "十四",
  "十五",
  "十六",
  "十七",
  "十八",
  "十九",
  "二十",
  "廿一",
  "廿二",
  "廿三",
  "廿四",
  "廿五",
  "廿六",
  "廿七",
  "廿八",
  "廿九",
  "三十",
];

const dateFormatter = new Intl.DateTimeFormat("zh-CN", {
  timeZone: "Asia/Shanghai",
  year: "numeric",
  month: "numeric",
  day: "numeric",
  weekday: "long",
});

const timeFormatter = new Intl.DateTimeFormat("zh-CN", {
  timeZone: "Asia/Shanghai",
  hour: "2-digit",
  minute: "2-digit",
  second: "2-digit",
  hour12: false,
});

const lunarFormatter = (() => {
  try {
    return new Intl.DateTimeFormat("zh-CN-u-ca-chinese", {
      timeZone: "Asia/Shanghai",
      month: "long",
      day: "numeric",
    });
  } catch {
    return null;
  }
})();

function getDateKey(timestamp) {
  const parts = dateFormatter.formatToParts(new Date(timestamp));
  const year = parts.find((item) => item.type === "year")?.value || "";
  const month = parts.find((item) => item.type === "month")?.value || "";
  const day = parts.find((item) => item.type === "day")?.value || "";
  return `${year}-${month}-${day}`;
}

function buildLocalLunarLine(timestamp) {
  if (!lunarFormatter) {
    return "农历信息暂不可用";
  }

  try {
    const raw = lunarFormatter.format(new Date(timestamp));
    const monthMatch = raw.match(/^(.+?月)/);
    const dayMatch = raw.match(/(\d+)日?/);
    const monthText = monthMatch?.[1] || "";
    const dayNumber = Number(dayMatch?.[1] || 0);
    const dayText = lunarDayLabels[dayNumber] || dayMatch?.[1] || "";
    return monthText && dayText ? `农历${monthText}${dayText}` : `农历${raw}`;
  } catch {
    return "农历信息暂不可用";
  }
}

function primeLocalClock() {
  const localNow = Date.now();
  nowMs.value = localNow;
  lastDateKey = getDateKey(localNow);
  loading.value = false;
}

function syncNowFromServerBase() {
  if (!baseServerMs) {
    nowMs.value = Date.now();
    return;
  }
  nowMs.value = Math.round(baseServerMs + (performance.now() - basePerfMs));
  const currentDateKey = getDateKey(nowMs.value);
  if (currentDateKey !== lastDateKey) {
    lastDateKey = currentDateKey;
    void syncClock();
  }
}

async function syncClock() {
  try {
    const snapshot = await Promise.race([
      getBeijingTime(),
      new Promise((_, reject) => {
        window.setTimeout(() => reject(new Error("北京时间同步超时")), 3500);
      }),
    ]);
    timeSnapshot.value = snapshot;
    baseServerMs = snapshot.unix_ms;
    basePerfMs = performance.now();
    nowMs.value = snapshot.unix_ms;
    lastDateKey = getDateKey(snapshot.unix_ms);
    error.value = "";
  } catch (err) {
    if (!nowMs.value) {
      primeLocalClock();
    }
    error.value = "已切换为本地北京时间显示";
  } finally {
    loading.value = false;
  }
}

function handleVisibilityChange() {
  if (!document.hidden) {
    void syncClock();
  }
}

const dateLine = computed(() => {
  if (!nowMs.value) {
    return timeSnapshot.value?.date_text || "北京时间同步中";
  }
  const parts = dateFormatter.formatToParts(new Date(nowMs.value));
  const year = parts.find((item) => item.type === "year")?.value || "";
  const month = parts.find((item) => item.type === "month")?.value || "";
  const day = parts.find((item) => item.type === "day")?.value || "";
  const weekday = parts.find((item) => item.type === "weekday")?.value || timeSnapshot.value?.weekday_cn || "";
  if (props.compact) {
    return `${year}年${month}月${day}日 ${weekday}`;
  }
  return `今天是${year}年${month}月${day}日 ${weekday}`;
});

const timeLine = computed(() => {
  if (!nowMs.value) {
    return timeSnapshot.value?.time_text ? `北京时间 ${timeSnapshot.value.time_text}` : "北京时间同步中";
  }
  return `北京时间 ${timeFormatter.format(new Date(nowMs.value))}`;
});

const lunarLine = computed(() => {
  if (timeSnapshot.value?.lunar_full_text) {
    return timeSnapshot.value.lunar_full_text;
  }
  if (nowMs.value) {
    return buildLocalLunarLine(nowMs.value);
  }
  return "农历信息准备中";
});

const statusLine = computed(() => {
  if (props.compact) {
    return error.value ? "本地北京时间" : "UTC+8";
  }
  return error.value ? error.value : "以中国标准时间 UTC+8 显示";
});

const timeSubtitle = computed(() => {
  if (loading.value) {
    return props.compact ? "校准北京时间" : "正在校准北京时间";
  }
  return timeLine.value;
});

onMounted(() => {
  primeLocalClock();
  void syncClock();
  tickTimer = window.setInterval(syncNowFromServerBase, 1000);
  syncTimer = window.setInterval(() => {
    void syncClock();
  }, 60_000);
  document.addEventListener("visibilitychange", handleVisibilityChange);
});

onBeforeUnmount(() => {
  if (tickTimer) {
    window.clearInterval(tickTimer);
  }
  if (syncTimer) {
    window.clearInterval(syncTimer);
  }
  document.removeEventListener("visibilitychange", handleVisibilityChange);
});
</script>

<template>
  <aside class="tool-datetime-card" :class="{ compact: compact }" aria-live="polite">
    <div class="tool-datetime-row">
      <span class="tool-datetime-icon">日</span>
      <div class="tool-datetime-copy">
        <p class="tool-datetime-title">{{ dateLine }}</p>
        <p class="tool-datetime-subtitle">{{ timeSubtitle }}</p>
      </div>
    </div>
    <div class="tool-datetime-row secondary">
      <span class="tool-datetime-icon lunar">农</span>
      <div class="tool-datetime-copy">
        <p class="tool-datetime-title">{{ lunarLine }}</p>
        <p class="tool-datetime-subtitle">{{ statusLine }}</p>
      </div>
    </div>
  </aside>
</template>
