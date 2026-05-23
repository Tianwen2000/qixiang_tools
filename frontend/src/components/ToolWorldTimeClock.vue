<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from "vue";

import { formatZoneDate, formatZoneTime, getZoneOffsetLabel, worldClockZones } from "../utils/time-tools.js";

defineProps({
  tool: {
    type: Object,
    required: true,
  },
});

const nowMs = ref(Date.now());
let timer = null;

const clockCards = computed(() =>
  worldClockZones.map((item) => ({
    ...item,
    time: formatZoneTime(nowMs.value, item.zone),
    date: formatZoneDate(nowMs.value, item.zone),
    offset: getZoneOffsetLabel(item.zone, nowMs.value),
  })),
);

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
    <section class="time-tool-note">
      <strong>常用世界时钟</strong>
      <p>这版先放常用协作城市，后面如果你要，我可以继续做自定义城市、会议时段重叠和最佳会议时间推荐。</p>
    </section>

    <section class="time-tool-grid">
      <article v-for="item in clockCards" :key="item.city" class="time-tool-card">
        <span>{{ item.city }}</span>
        <strong>{{ item.time }}</strong>
        <small>{{ item.date }} · {{ item.offset }} · {{ item.note }}</small>
      </article>
    </section>
  </section>
</template>
