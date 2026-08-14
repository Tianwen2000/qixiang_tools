<script setup>
// 文件说明：定义 ToolTimeConverter 前端组件。
import { computed, ref } from "vue";

import GlassSelect from "./GlassSelect.vue";
import {
  beijingDateTimeFormatter,
  formatZoneDateTime,
  parseDateTimeValue,
  toDateTimeInputValue,
  utcDateTimeFormatter,
} from "../utils/time-tools.js";

defineProps({
  tool: {
    type: Object,
    required: true,
  },
});

const timeInput = ref(toDateTimeInputValue(new Date()));
const timeSource = ref("local");
const mode = ref("datetime");
const timestampInput = ref(String(Date.now()));

const timeSourceOptions = [
  { value: "local", label: "当前设备本地时区" },
  { value: "beijing", label: "北京时间 UTC+8" },
  { value: "utc", label: "UTC 时间" },
];

const timeResult = computed(() => {
  const timestamp = parseDateTimeValue(timeInput.value, timeSource.value);
  if (!Number.isFinite(timestamp)) {
    return { error: "请输入有效的日期和时间" };
  }
  const localZone = Intl.DateTimeFormat().resolvedOptions().timeZone || "Asia/Shanghai";
  return {
    local: formatZoneDateTime(timestamp, localZone),
    beijing: beijingDateTimeFormatter.format(new Date(timestamp)),
    utc: utcDateTimeFormatter.format(new Date(timestamp)),
    iso: new Date(timestamp).toISOString(),
    unixSeconds: String(Math.floor(timestamp / 1000)),
    unixMs: String(timestamp),
  };
});

const timestampResult = computed(() => {
  const raw = timestampInput.value.trim();
  const numeric = Number(raw);
  if (!raw || !Number.isFinite(numeric)) {
    return { error: "请输入秒级或毫秒级时间戳" };
  }

  const isSeconds = Math.abs(numeric) < 1e12;
  const timestamp = isSeconds ? numeric * 1000 : numeric;
  const date = new Date(timestamp);
  if (!Number.isFinite(date.getTime())) {
    return { error: "请输入有效范围内的时间戳" };
  }

  const localZone = Intl.DateTimeFormat().resolvedOptions().timeZone || "Asia/Shanghai";
  return {
    detected: isSeconds ? "秒级时间戳" : "毫秒级时间戳",
    local: formatZoneDateTime(timestamp, localZone),
    beijing: beijingDateTimeFormatter.format(date),
    utc: utcDateTimeFormatter.format(date),
    iso: date.toISOString(),
  };
});
</script>

<template>
  <section class="tool-form time-tool-shell">
    <div class="time-tool-actions" role="group" aria-label="转换方向">
      <button
        type="button"
        :class="{ 'secondary-button': mode !== 'datetime' }"
        :aria-pressed="mode === 'datetime'"
        @click="mode = 'datetime'"
      >
        时间转时间戳
      </button>
      <button
        type="button"
        :class="{ 'secondary-button': mode !== 'timestamp' }"
        :aria-pressed="mode === 'timestamp'"
        @click="mode = 'timestamp'"
      >
        时间戳转时间
      </button>
    </div>

    <template v-if="mode === 'datetime'">
      <label class="time-tool-label">
        <span>输入时间</span>
        <input v-model="timeInput" type="datetime-local" />
      </label>

      <label class="time-tool-label">
        <span>输入时区基准</span>
        <GlassSelect v-model="timeSource" :options="timeSourceOptions" placeholder="请选择时区基准" />
      </label>

      <div class="time-tool-actions">
        <button type="button" @click="timeInput = toDateTimeInputValue(new Date())">使用当前时间</button>
      </div>

      <section v-if="timeResult.error" class="time-tool-empty">{{ timeResult.error }}</section>
      <section v-else class="time-tool-grid">
        <article class="time-tool-card">
          <span>本地时间</span>
          <strong>{{ timeResult.local }}</strong>
        </article>
        <article class="time-tool-card">
          <span>北京时间</span>
          <strong>{{ timeResult.beijing }}</strong>
        </article>
        <article class="time-tool-card">
          <span>UTC</span>
          <strong>{{ timeResult.utc }}</strong>
        </article>
        <article class="time-tool-card">
          <span>ISO 8601</span>
          <strong>{{ timeResult.iso }}</strong>
        </article>
        <article class="time-tool-card">
          <span>Unix 秒</span>
          <strong>{{ timeResult.unixSeconds }}</strong>
        </article>
        <article class="time-tool-card">
          <span>Unix 毫秒</span>
          <strong>{{ timeResult.unixMs }}</strong>
        </article>
      </section>
    </template>

    <template v-else>
      <label class="time-tool-label">
        <span>时间戳</span>
        <input v-model="timestampInput" type="text" inputmode="numeric" placeholder="例如 1712649600 或 1712649600000" />
      </label>

      <div class="time-tool-actions">
        <button type="button" @click="timestampInput = String(Date.now())">当前毫秒时间戳</button>
        <button type="button" class="secondary-button" @click="timestampInput = String(Math.floor(Date.now() / 1000))">
          当前秒级时间戳
        </button>
      </div>

      <section v-if="timestampResult.error" class="time-tool-empty">{{ timestampResult.error }}</section>
      <section v-else class="time-tool-grid">
        <article class="time-tool-card wide">
          <span>识别结果</span>
          <strong>{{ timestampResult.detected }}</strong>
          <small>{{ timestampResult.iso }}</small>
        </article>
        <article class="time-tool-card">
          <span>本地时间</span>
          <strong>{{ timestampResult.local }}</strong>
        </article>
        <article class="time-tool-card">
          <span>北京时间</span>
          <strong>{{ timestampResult.beijing }}</strong>
        </article>
        <article class="time-tool-card wide">
          <span>UTC</span>
          <strong>{{ timestampResult.utc }}</strong>
        </article>
      </section>
    </template>
  </section>
</template>
