<script setup>
import { computed } from "vue";

const props = defineProps({
  size: {
    type: [Number, String],
    default: 32,
  },
});

const logoSize = computed(() => (typeof props.size === "number" ? `${props.size}px` : props.size));
</script>

<template>
  <span class="qxai-logo" :style="{ '--qxai-logo-size': logoSize }" aria-hidden="true">
    <img src="/ai-robot-logo.png" alt="" />
  </span>
</template>

<style scoped>
.qxai-logo {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: var(--qxai-logo-size);
  height: var(--qxai-logo-size);
  flex-shrink: 0;
}

.qxai-logo img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  display: block;
  pointer-events: none;
}
</style>
