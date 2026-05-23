<script setup>
import KeyboardKeyCap from "./KeyboardKeyCap.vue";

defineProps({
  keys: {
    type: Array,
    required: true,
  },
  resolveState: {
    type: Function,
    required: true,
  },
  layoutMode: {
    type: String,
    default: "flex",
  },
});
</script>

<template>
  <div class="kb-row" :class="{ 'is-grid-row': layoutMode === 'grid' }">
    <KeyboardKeyCap
      v-for="keyItem in keys"
      :key="keyItem.id"
      :key-item="keyItem"
      :state="resolveState(keyItem)"
      :layout-mode="layoutMode"
    />
  </div>
</template>

<style scoped>
.kb-row {
  display: flex;
  align-items: stretch;
  gap: var(--kb-gap);
  flex: 0 0 auto;
}

.kb-row.is-grid-row {
  display: grid;
}
</style>