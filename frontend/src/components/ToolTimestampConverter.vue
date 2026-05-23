<script setup>
import { computed, ref } from "vue";

import { beijingDateTimeFormatter, formatZoneDateTime, utcDateTimeFormatter } from "../utils/time-tools.js";

defineProps({
  tool: {
    type: Object,
    required: true,
  },
});

const timestampInput = ref(String(Date.now()));

const result = computed(() => {
  const raw = timestampInput.value.trim();
  const numeric = Number(raw);
  if (!raw || !Number.isFinite(numeric)) {
    return { error: "请输入秒级或毫秒级时间戳" };
  }
  const timestamp = Math.abs(numeric) < 1e12 ? numeric * 1000 : numeric;
  const localZone = Intl.DateTimeFormat().resolvedOptions().timeZone || "Asia/Shanghai";
  return {
    detected: Math.abs(numeric) < 1e12 ? "秒级时间戳" : "毫秒级时间戳",
    local: formatZoneDateTime(timestamp, localZone),
    beijing: beijingDateTimeFormatter.format(new Date(timestamp)),
    utc: utcDateTimeFormatter.format(new Date(timestamp)),
    iso: new Date(timestamp).toISOString(),
  };
});
</script>

<template>
  <section class="tool-form time-tool-shell">
    <label class="time-tool-label">
      <span>时间戳</span>
      <input v-model="timestampInput" type="text" placeholder="例如 1712649600 或 1712649600000" />
    </label>

    <div class="time-tool-actions">
      <button type="button" @click="timestampInput = String(Date.now())">当前毫秒时间戳</button>
      <button type="button" class="secondary-button" @click="timestampInput = String(Math.floor(Date.now() / 1000))">
        当前秒级时间戳
      </button>
    </div>

    <section v-if="result.error" class="time-tool-empty">{{ result.error }}</section>
    <section v-else class="time-tool-grid">
      <article class="time-tool-card wide">
        <span>识别结果</span>
        <strong>{{ result.detected }}</strong>
        <small>{{ result.iso }}</small>
      </article>
      <article class="time-tool-card">
        <span>本地时间</span>
        <strong>{{ result.local }}</strong>
      </article>
      <article class="time-tool-card">
        <span>北京时间</span>
        <strong>{{ result.beijing }}</strong>
      </article>
      <article class="time-tool-card wide">
        <span>UTC</span>
        <strong>{{ result.utc }}</strong>
      </article>
    </section>
  </section>
</template>
