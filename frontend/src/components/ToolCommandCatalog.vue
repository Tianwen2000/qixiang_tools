<script setup>
import { computed, ref } from "vue";

import { getCommandCatalog } from "../data/command-catalogs.js";

const props = defineProps({
  tool: {
    type: Object,
    required: true,
  },
});

const keyword = ref("");
const commands = computed(() => getCommandCatalog(props.tool.slug));
const results = computed(() => {
  const query = keyword.value.trim().toLowerCase();
  if (!query) {
    return commands.value;
  }
  const tokens = query.split(/[\s,，]+/).filter(Boolean);
  return commands.value.filter((item) => {
    const haystack = [item.command, item.summary, ...(item.tags || [])].join(" ").toLowerCase();
    return tokens.every((token) => haystack.includes(token));
  });
});
</script>

<template>
  <section class="tool-form command-catalog-shell">
    <div class="command-catalog-toolbar">
      <label class="command-catalog-search">
        <span>检索命令</span>
        <input v-model="keyword" type="search" placeholder="输入命令、参数或用途关键词" />
      </label>
      <div class="command-catalog-count">
        <strong>{{ results.length }}</strong>
        <span>/ {{ commands.length }} 条</span>
      </div>
    </div>

    <section v-if="!results.length" class="time-tool-empty">没有找到匹配的命令。</section>
    <div v-else class="command-catalog-table-wrap">
      <table class="command-catalog-table">
        <thead>
          <tr>
            <th scope="col">命令</th>
            <th scope="col">说明</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in results" :key="item.command">
            <td><code>{{ item.command }}</code></td>
            <td>{{ item.summary }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>
</template>
