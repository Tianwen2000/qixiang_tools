<script setup>
import { computed, ref } from "vue";

import { dynastyTimeline } from "../utils/time-datasets.js";

defineProps({
  tool: {
    type: Object,
    required: true,
  },
});

const keyword = ref("");

const results = computed(() => {
  const query = keyword.value.trim().toLowerCase();
  if (!query) {
    return dynastyTimeline;
  }
  return dynastyTimeline.filter((item) => {
    return [item.name, item.years, item.tag, item.note].some((value) => value.toLowerCase().includes(query));
  });
});
</script>

<template>
  <section class="tool-form time-tool-shell">
    <label class="time-tool-label">
      <span>检索朝代</span>
      <input v-model="keyword" type="search" placeholder="输入朝代名、时期或关键词" />
    </label>

    <section v-if="!results.length" class="time-tool-empty">没有找到匹配的朝代记录。</section>
    <section v-else class="time-tool-list">
      <article v-for="item in results" :key="item.name" class="time-tool-list-item">
        <div class="time-tool-list-head">
          <strong>{{ item.name }}</strong>
          <span class="time-tool-pill">{{ item.tag }}</span>
        </div>
        <small>{{ item.years }}</small>
        <small>{{ item.note }}</small>
      </article>
    </section>
  </section>
</template>
