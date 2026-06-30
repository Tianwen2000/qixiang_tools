<script setup>
// 文件说明：定义键盘测试可视化的 KeyboardStatusBar 子组件。
import { computed } from "vue";

const props = defineProps({
  lastKey: {
    type: Object,
    default: () => ({}),
  },
});

const displayKeyCode = computed(() => props.lastKey?.keyCode ?? "--");
</script>

<template>
  <div class="kb-status-bar">
    <span class="kb-status-text">键码：{{ displayKeyCode }}</span>
  </div>
</template>

<style scoped>
.kb-status-bar {
  display: inline-flex;
  align-items: center;
  justify-content: flex-start;
  min-height: var(--kb-key-height);
  white-space: nowrap;
  flex: 0 0 auto;
}

.kb-status-text {
  display: inline-block;
  min-width: 56px;
  text-align: left;
  font-size: 11px;
  font-weight: 600;
  color: #ffffff;
  font-variant-numeric: tabular-nums;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas,
    "Liberation Mono", "Courier New", monospace;
}
</style>