<script setup>
import { computed } from "vue";

import { solarTerms2026 } from "../utils/time-datasets.js";
import { pad } from "../utils/time-tools.js";

defineProps({
  tool: {
    type: Object,
    required: true,
  },
});

const nowMs = Date.now();

const cards = computed(() =>
  solarTerms2026.map((item) => {
    const date = new Date(item.timestamp);
    return {
      ...item,
      date,
      timeLabel: `${pad(date.getMonth() + 1)}/${pad(date.getDate())} ${pad(date.getHours())}:${pad(date.getMinutes())}`,
    };
  }),
);

const currentTerm = computed(() => [...cards.value].reverse().find((item) => item.date.getTime() <= nowMs) || cards.value[0]);
const nextTerm = computed(() => cards.value.find((item) => item.date.getTime() > nowMs) || null);
</script>

<template>
  <section class="tool-form time-tool-shell">
    <section class="time-tool-grid">
      <article class="time-tool-card wide">
        <span>当前节气</span>
        <strong>{{ currentTerm?.name }}</strong>
        <small>{{ currentTerm?.timeLabel }} · {{ currentTerm?.note }}</small>
      </article>
      <article v-if="nextTerm" class="time-tool-card wide">
        <span>下一个节气</span>
        <strong>{{ nextTerm.name }}</strong>
        <small>{{ nextTerm.timeLabel }} · {{ nextTerm.note }}</small>
      </article>
    </section>

    <section class="time-tool-list">
      <article v-for="item in cards" :key="item.name" class="time-tool-list-item">
        <div class="time-tool-list-head">
          <strong>{{ item.name }}</strong>
          <span class="time-tool-pill" :class="{ active: currentTerm?.name === item.name }">{{ item.season }}</span>
        </div>
        <small>{{ item.timeLabel }}</small>
        <small>{{ item.lunar }}</small>
        <small>{{ item.note }}</small>
      </article>
    </section>
  </section>
</template>
