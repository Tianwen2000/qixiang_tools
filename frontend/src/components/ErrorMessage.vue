<script setup>
// 文件说明：定义 ErrorMessage 前端组件。
defineProps({
  message: {
    type: String,
    required: true,
  },
});
</script>

<template>
  <div class="error-box">
    <strong>操作失败</strong>
    <p class="error-text">{{ message }}</p>
  </div>
</template>
