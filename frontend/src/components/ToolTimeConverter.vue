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

const timeSourceOptions = [
  { value: "local", label: "当前设备本地时区" },
  { value: "beijing", label: "北京时间 UTC+8" },
  { value: "utc", label: "UTC 时间" },
];

const result = computed(() => {
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
</script>

<template>
  <section class="tool-form time-tool-shell">
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

    <section v-if="result.error" class="time-tool-empty">{{ result.error }}</section>
    <section v-else class="time-tool-grid">
      <article class="time-tool-card">
        <span>本地时间</span>
        <strong>{{ result.local }}</strong>
      </article>
      <article class="time-tool-card">
        <span>北京时间</span>
        <strong>{{ result.beijing }}</strong>
      </article>
      <article class="time-tool-card">
        <span>UTC</span>
        <strong>{{ result.utc }}</strong>
      </article>
      <article class="time-tool-card">
        <span>ISO 8601</span>
        <strong>{{ result.iso }}</strong>
      </article>
      <article class="time-tool-card">
        <span>Unix 秒</span>
        <strong>{{ result.unixSeconds }}</strong>
      </article>
      <article class="time-tool-card">
        <span>Unix 毫秒</span>
        <strong>{{ result.unixMs }}</strong>
      </article>
    </section>
  </section>
</template>
