<script setup>
// 文件说明：定义 ToolOffWorkCountdown 前端组件。
import { computed, onBeforeUnmount, onMounted, ref } from "vue";

import { holidaySchedulesByYear } from "../utils/time-datasets.js";
import { beijingDateFormatter, beijingTimeFormatter, getChineseYearName, getChineseZodiac, getLunarInfo, pad } from "../utils/time-tools.js";

defineProps({
  tool: {
    type: Object,
    required: true,
  },
});

const DAY_MS = 24 * 60 * 60 * 1000;
const currentMs = ref(Date.now());
let refreshTimer = null;

const beijingPartsFormatter = new Intl.DateTimeFormat("zh-CN", {
  timeZone: "Asia/Shanghai",
  year: "numeric",
  month: "2-digit",
  day: "2-digit",
  hour: "2-digit",
  minute: "2-digit",
  second: "2-digit",
  weekday: "long",
  hour12: false,
});

const festivalDatesByYear = {
  2023: [
    ["元旦", "2023-01-01"],
    ["春节", "2023-01-22"],
    ["清明节", "2023-04-04"],
    ["劳动节", "2023-05-01"],
    ["端午节", "2023-06-22"],
    ["中秋节", "2023-09-29"],
    ["国庆节", "2023-10-01"],
  ],
  2024: [
    ["元旦", "2024-01-01"],
    ["春节", "2024-02-10"],
    ["清明节", "2024-04-04"],
    ["劳动节", "2024-05-01"],
    ["端午节", "2024-06-10"],
    ["中秋节", "2024-09-17"],
    ["国庆节", "2024-10-01"],
  ],
  2025: [
    ["元旦", "2025-01-01"],
    ["春节", "2025-01-29"],
    ["清明节", "2025-04-04"],
    ["劳动节", "2025-05-01"],
    ["端午节", "2025-05-31"],
    ["中秋节", "2025-10-06"],
    ["国庆节", "2025-10-01"],
  ],
  2026: [
    ["元旦", "2026-01-01"],
    ["春节", "2026-02-17"],
    ["清明节", "2026-04-04"],
    ["劳动节", "2026-05-01"],
    ["端午节", "2026-06-19"],
    ["中秋节", "2026-09-25"],
    ["国庆节", "2026-10-01"],
  ],
  2027: [
    ["元旦", "2027-01-01"],
    ["春节", "2027-02-06"],
    ["清明节", "2027-04-04"],
    ["劳动节", "2027-05-01"],
    ["端午节", "2027-06-09"],
    ["中秋节", "2027-09-15"],
    ["国庆节", "2027-10-01"],
  ],
  2028: [
    ["元旦", "2028-01-01"],
    ["春节", "2028-01-26"],
    ["清明节", "2028-04-04"],
    ["劳动节", "2028-05-01"],
    ["端午节", "2028-05-28"],
    ["中秋节", "2028-10-03"],
    ["国庆节", "2028-10-01"],
  ],
  2029: [
    ["元旦", "2029-01-01"],
    ["春节", "2029-02-13"],
    ["清明节", "2029-04-04"],
    ["劳动节", "2029-05-01"],
    ["端午节", "2029-06-16"],
    ["中秋节", "2029-09-24"],
    ["国庆节", "2029-10-01"],
  ],
  2030: [
    ["元旦", "2030-01-01"],
    ["春节", "2030-02-03"],
    ["清明节", "2030-04-04"],
    ["劳动节", "2030-05-01"],
    ["端午节", "2030-06-05"],
    ["中秋节", "2030-09-13"],
    ["国庆节", "2030-10-01"],
  ],
};

const chuxiDates = {
  2023: "2023-01-21",
  2024: "2024-02-09",
  2025: "2025-01-28",
  2026: "2026-02-16",
  2027: "2027-02-05",
  2028: "2028-01-25",
  2029: "2029-02-12",
  2030: "2030-02-02",
};

function getBeijingParts(timestamp) {
  const parts = Object.fromEntries(beijingPartsFormatter.formatToParts(new Date(timestamp)).map((item) => [item.type, item.value]));
  return {
    year: Number(parts.year),
    month: Number(parts.month),
    day: Number(parts.day),
    hour: Number(parts.hour),
    minute: Number(parts.minute),
    second: Number(parts.second),
    weekday: parts.weekday,
  };
}

function dateKey(year, month, day) {
  return `${year}-${pad(month)}-${pad(day)}`;
}

function keyFromParts(parts) {
  return dateKey(parts.year, parts.month, parts.day);
}

function keyFromUtcMs(timestamp) {
  const date = new Date(timestamp);
  return dateKey(date.getUTCFullYear(), date.getUTCMonth() + 1, date.getUTCDate());
}

function keyToUtcMs(key) {
  const [year, month, day] = key.split("-").map(Number);
  return Date.UTC(year, month - 1, day);
}

function addDaysToKey(key, amount) {
  return keyFromUtcMs(keyToUtcMs(key) + amount * DAY_MS);
}

function diffDays(targetKey, baseKey) {
  return Math.round((keyToUtcMs(targetKey) - keyToUtcMs(baseKey)) / DAY_MS);
}

function getYearFromKey(key) {
  return Number(key.slice(0, 4));
}

function formatShortKey(key) {
  const [, month, day] = key.split("-");
  return `${Number(month)}月${Number(day)}日`;
}

function beijingClockToTimestamp(key, hour, minute, second = 0) {
  const [year, month, day] = key.split("-").map(Number);
  return Date.UTC(year, month - 1, day, hour - 8, minute, second);
}

function formatClockDuration(milliseconds) {
  const totalSeconds = Math.max(0, Math.floor(milliseconds / 1000));
  const hours = Math.floor(totalSeconds / 3600);
  const minutes = Math.floor((totalSeconds % 3600) / 60);
  const seconds = totalSeconds % 60;
  return `${pad(hours)}小时 ${pad(minutes)}分钟 ${pad(seconds)}秒`;
}

function getClockTarget(parts, timestamp, hour, minute) {
  const today = keyFromParts(parts);
  let targetKey = today;
  let targetMs = beijingClockToTimestamp(targetKey, hour, minute);
  if (timestamp > targetMs) {
    targetKey = addDaysToKey(today, 1);
    targetMs = beijingClockToTimestamp(targetKey, hour, minute);
  }
  return {
    targetKey,
    targetMs,
    dayLabel: targetKey === today ? "今天" : "明天",
    remainingLabel: formatClockDuration(targetMs - timestamp),
  };
}

function buildHolidayCandidates(year) {
  const schedule = holidaySchedulesByYear[year];
  if (schedule?.length) {
    return schedule.map((item) => ({
      name: item.name,
      start: item.start,
      end: item.end,
      totalDays: item.totalDays,
      summary: item.summary,
      source: "schedule",
    }));
  }
  return (festivalDatesByYear[year] || []).map(([name, key]) => ({
    name,
    start: key,
    end: key,
    totalDays: 1,
    summary: `${formatShortKey(key)} 当天`,
    source: "fallback",
  }));
}

function getNextHoliday(todayKey) {
  const year = getYearFromKey(todayKey);
  const candidates = [year, year + 1]
    .flatMap((itemYear) => buildHolidayCandidates(itemYear))
    .filter((item) => item.end >= todayKey)
    .sort((left, right) => left.start.localeCompare(right.start));
  const holiday = candidates[0];
  if (!holiday) {
    return {
      name: "暂未收录",
      days: null,
      detail: "当前年份之后的节假日数据还没有加入。",
    };
  }
  const active = holiday.start <= todayKey && todayKey <= holiday.end;
  return {
    name: holiday.name,
    days: active ? 0 : diffDays(holiday.start, todayKey),
    detail:
      holiday.source === "schedule"
        ? `${formatShortKey(holiday.start)} - ${formatShortKey(holiday.end)} · ${holiday.totalDays}天`
        : `${formatShortKey(holiday.start)} · 单日节日`,
    active,
  };
}

function getNextChuxi(todayKey) {
  let year = getYearFromKey(todayKey);
  let targetKey = chuxiDates[year] || `${year}-01-22`;
  if (targetKey < todayKey) {
    year += 1;
    targetKey = chuxiDates[year] || `${year}-01-22`;
  }
  return {
    key: targetKey,
    days: diffDays(targetKey, todayKey),
  };
}

function getNextPayday(parts, todayKey, paydayDay) {
  let year = parts.year;
  let month = parts.month;
  if (parts.day > paydayDay) {
    month += 1;
    if (month > 12) {
      month = 1;
      year += 1;
    }
  }
  const targetKey = dateKey(year, month, paydayDay);
  return {
    day: paydayDay,
    key: targetKey,
    month,
    days: diffDays(targetKey, todayKey),
  };
}

function getDaysToSaturday(todayKey) {
  const weekday = new Date(keyToUtcMs(todayKey)).getUTCDay();
  const days = (6 - weekday + 7) % 7;
  return {
    days,
    label: days === 0 ? "今天就是周六" : `${days} 天`,
  };
}

function getRestDaySummary(year, todayKey) {
  const restDays = new Set();
  const start = Date.UTC(year, 0, 1);
  const end = Date.UTC(year, 11, 31);
  for (let timestamp = start; timestamp <= end; timestamp += DAY_MS) {
    const weekday = new Date(timestamp).getUTCDay();
    if (weekday === 0 || weekday === 6) {
      restDays.add(keyFromUtcMs(timestamp));
    }
  }

  const schedule = holidaySchedulesByYear[year] || [];
  schedule.forEach((item) => {
    for (let timestamp = keyToUtcMs(item.start); timestamp <= keyToUtcMs(item.end); timestamp += DAY_MS) {
      restDays.add(keyFromUtcMs(timestamp));
    }
    item.workdays.forEach((workday) => restDays.delete(workday));
  });

  if (!schedule.length) {
    (festivalDatesByYear[year] || []).forEach(([, key]) => restDays.add(key));
  }

  const days = [...restDays];
  return {
    past: days.filter((key) => key < todayKey).length,
    future: days.filter((key) => key >= todayKey).length,
    total: days.length,
    isTodayRest: restDays.has(todayKey),
    hasOfficialSchedule: schedule.length > 0,
  };
}

function getTodayState(todayKey, restSummary) {
  const schedule = holidaySchedulesByYear[getYearFromKey(todayKey)] || [];
  if (schedule.some((item) => item.workdays.includes(todayKey))) {
    return "调休上班日";
  }
  const activeHoliday = schedule.find((item) => item.start <= todayKey && todayKey <= item.end);
  if (activeHoliday) {
    return `${activeHoliday.name}假期`;
  }
  return restSummary.isTodayRest ? "休息日" : "工作日";
}

function updateNow() {
  currentMs.value = Date.now();
}

const currentDate = computed(() => new Date(currentMs.value));
const currentParts = computed(() => getBeijingParts(currentMs.value));
const todayKey = computed(() => keyFromParts(currentParts.value));
const currentDateText = computed(() => beijingDateFormatter.format(currentDate.value));
const currentTimeText = computed(() => beijingTimeFormatter.format(currentDate.value));
const lunarText = computed(() => getLunarInfo(currentDate.value).full);
const chineseYearText = computed(() => {
  const stemBranch = getChineseYearName(currentDate.value);
  const zodiac = getChineseZodiac(currentDate.value);
  return stemBranch && zodiac ? `${stemBranch}${zodiac}年` : "农历年份暂不可用";
});
const lunchTarget = computed(() => getClockTarget(currentParts.value, currentMs.value, 11, 45));
const offWorkTarget = computed(() => getClockTarget(currentParts.value, currentMs.value, 17, 30));
const saturday = computed(() => getDaysToSaturday(todayKey.value));
const nextHoliday = computed(() => getNextHoliday(todayKey.value));
const nextChuxi = computed(() => getNextChuxi(todayKey.value));
const payday15 = computed(() => getNextPayday(currentParts.value, todayKey.value, 15));
const payday10 = computed(() => getNextPayday(currentParts.value, todayKey.value, 10));
const restSummary = computed(() => getRestDaySummary(currentParts.value.year, todayKey.value));
const todayState = computed(() => getTodayState(todayKey.value, restSummary.value));
const restSummaryNote = computed(
  () => `全年共 ${restSummary.value.total} 天；按周末 + 站内放假安排统计${restSummary.value.hasOfficialSchedule ? "，调休上班日会扣除" : ""}`,
);

onMounted(() => {
  refreshTimer = window.setInterval(updateNow, 1000);
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
      <strong>今天是 {{ currentDateText }} {{ currentTimeText }}</strong>
      <p>农历：{{ lunarText }} | {{ chineseYearText }} | 今天状态：{{ todayState }}</p>
    </section>

    <div class="time-tool-actions">
      <button type="button" @click="updateNow">立即刷新</button>
    </div>

    <section class="time-tool-hero">
      <span>距离下班 17:30 还有</span>
      <strong>{{ offWorkTarget.remainingLabel }}</strong>
      <small>目标时间：{{ offWorkTarget.dayLabel }} 17:30</small>
    </section>

    <section class="time-tool-grid">
      <article class="time-tool-card">
        <span>距离午休 11:45</span>
        <strong>{{ lunchTarget.remainingLabel }}</strong>
        <small>目标时间：{{ lunchTarget.dayLabel }} 11:45</small>
      </article>

      <article class="time-tool-card">
        <span>距离周六</span>
        <strong>{{ saturday.label }}</strong>
        <small>{{ currentParts.weekday }}</small>
      </article>

      <article class="time-tool-card">
        <span>下一个法定节假日</span>
        <strong>{{ nextHoliday.name }}</strong>
        <small v-if="nextHoliday.days === 0">今天就在假期内</small>
        <small v-else-if="nextHoliday.days !== null">还有 {{ nextHoliday.days }} 天</small>
        <small>{{ nextHoliday.detail }}</small>
      </article>

      <article class="time-tool-card">
        <span>距离除夕</span>
        <strong>{{ nextChuxi.days === 0 ? "今天是除夕" : `${nextChuxi.days} 天` }}</strong>
        <small>{{ formatShortKey(nextChuxi.key) }}</small>
      </article>

      <article class="time-tool-card">
        <span>{{ payday15.month }}月15号发工资</span>
        <strong>{{ payday15.days === 0 ? "今天发工资" : `${payday15.days} 天` }}</strong>
        <small>每月 15 号</small>
      </article>

      <article class="time-tool-card">
        <span>{{ payday10.month }}月10号发工资</span>
        <strong>{{ payday10.days === 0 ? "今天发工资" : `${payday10.days} 天` }}</strong>
        <small>每月 10 号</small>
      </article>

      <article class="time-tool-card wide">
        <span>今年休息日</span>
        <strong>已过 {{ restSummary.past }} 天，还剩 {{ restSummary.future }} 天</strong>
        <small>{{ restSummaryNote }}</small>
      </article>
    </section>
  </section>
</template>
