<script setup>
import { computed } from "vue";

import { getCategoryTheme, getToolModeLabel } from "../data/ui-mapping.js";

const props = defineProps({
  tool: {
    type: Object,
    required: true,
  },
  query: {
    type: Object,
    default: () => ({}),
  },
});

const theme = computed(() => getCategoryTheme(props.tool.category));
</script>

<template>
  <router-link
    class="tool-card"
    :to="{ name: 'tool', params: { slug: tool.slug }, query }"
    :style="{ '--tool-accent': theme.accent, '--tool-soft': theme.soft }"
  >
    <div class="tool-card-body">
      <div class="tool-card-top">
        <span class="tool-chip">{{ getToolModeLabel(tool) }}</span>
        <span class="tool-chip muted">{{ theme.label }}</span>
      </div>
      <h3>{{ tool.name }}</h3>
      <p>{{ tool.summary }}</p>
    </div>
  </router-link>
</template>
