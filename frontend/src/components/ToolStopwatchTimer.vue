<script setup>
import { computed, onBeforeUnmount, ref } from "vue";

import { formatDurationParts } from "../utils/time-tools.js";

defineProps({
  tool: {
    type: Object,
    required: true,
  },
});

const elapsedMs = ref(0);
const running = ref(false);
const startedAt = ref(0);
const renderTick = ref(Date.now());
const laps = ref([]);
let timer = null;

const displayMs = computed(() => {
  if (!running.value) {
    return elapsedMs.value;
  }
  return elapsedMs.value + (renderTick.value - startedAt.value);
});

const display = computed(() => formatDurationParts(displayMs.value, true).label);

function startTicker() {
  if (timer) {
    window.clearInterval(timer);
  }
  timer = window.setInterval(() => {
    renderTick.value = Date.now();
  }, 40);
}

function stopTicker() {
  if (timer) {
    window.clearInterval(timer);
    timer = null;
  }
}

function toggle() {
  if (running.value) {
    elapsedMs.value += Date.now() - startedAt.value;
    running.value = false;
    stopTicker();
    return;
  }
  startedAt.value = Date.now();
  running.value = true;
  renderTick.value = startedAt.value;
  startTicker();
}

function reset() {
  elapsedMs.value = 0;
  startedAt.value = 0;
  running.value = false;
  renderTick.value = Date.now();
  laps.value = [];
  stopTicker();
}

function addLap() {
  if (displayMs.value <= 0) {
    return;
  }
  laps.value = [
    { label: `第 ${laps.value.length + 1} 圈`, value: formatDurationParts(displayMs.value, true).label },
    ...laps.value,
  ].slice(0, 8);
}

onBeforeUnmount(stopTicker);
</script>

<template>
  <section class="tool-form time-tool-shell">
    <section class="time-tool-stopwatch">
      <strong>{{ display }}</strong>
      <div class="time-tool-actions">
        <button type="button" @click="toggle">{{ running ? "暂停" : "开始" }}</button>
        <button type="button" class="secondary-button" @click="addLap">记录分段</button>
        <button type="button" class="secondary-button" @click="reset">重置</button>
      </div>

      <div v-if="laps.length" class="time-tool-laps">
        <div v-for="lap in laps" :key="lap.label" class="time-tool-lap">
          <span>{{ lap.label }}</span>
          <strong>{{ lap.value }}</strong>
        </div>
      </div>
    </section>
  </section>
</template>
