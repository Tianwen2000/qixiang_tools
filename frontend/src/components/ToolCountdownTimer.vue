<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from "vue";

import { addDays, formatDurationParts, formatReadableDate, parseDateTimeValue, toDateTimeInputValue } from "../utils/time-tools.js";

defineProps({
  tool: {
    type: Object,
    required: true,
  },
});

const nowMs = ref(Date.now());
const targetInput = ref(toDateTimeInputValue(addDays(new Date(), 1)));
let timer = null;

const result = computed(() => {
  const targetMs = parseDateTimeValue(targetInput.value, "local");
  if (!Number.isFinite(targetMs)) {
    return { error: "请先设置目标时间" };
  }
  const remainingMs = targetMs - nowMs.value;
  if (remainingMs <= 0) {
    return { complete: true, label: "目标时间已到", parts: formatDurationParts(0) };
  }
  return {
    complete: false,
    label: "距离目标时间",
    parts: formatDurationParts(remainingMs),
    targetDate: formatReadableDate(new Date(targetMs)),
    targetTime: new Intl.DateTimeFormat("zh-CN", {
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
      hour12: false,
    }).format(new Date(targetMs)),
  };
});

function preset(hours) {
  targetInput.value = toDateTimeInputValue(new Date(nowMs.value + hours * 3600000));
}

onMounted(() => {
  timer = window.setInterval(() => {
    nowMs.value = Date.now();
  }, 1000);
});

onBeforeUnmount(() => {
  if (timer) {
    window.clearInterval(timer);
  }
});
</script>

<template>
  <section class="tool-form time-tool-shell">
    <label class="time-tool-label">
      <span>目标时间</span>
      <input v-model="targetInput" type="datetime-local" />
    </label>

    <div class="time-tool-actions">
      <button type="button" @click="preset(1)">1 小时后</button>
      <button type="button" class="secondary-button" @click="preset(8)">8 小时后</button>
      <button type="button" class="secondary-button" @click="preset(24)">24 小时后</button>
    </div>

    <section v-if="result.error" class="time-tool-empty">{{ result.error }}</section>
    <section v-else class="time-tool-hero">
      <span>{{ result.label }}</span>
      <strong>{{ result.parts.label }}</strong>
      <small v-if="!result.complete">目标时间：{{ result.targetDate }} {{ result.targetTime }}</small>
    </section>
  </section>
</template>
