<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from "vue";

import { showToast } from "../utils/toast.js";

const viewport = ref({
  width: 0,
  height: 0,
  pixelRatio: 1,
});
const outputVisible = ref(true);

function detectBreakpoint(width) {
  if (width < 576) {
    return { key: "xs", label: "手机", range: "< 576px" };
  }
  if (width < 768) {
    return { key: "sm", label: "大屏手机", range: "576 - 767px" };
  }
  if (width < 992) {
    return { key: "md", label: "平板", range: "768 - 991px" };
  }
  if (width < 1280) {
    return { key: "lg", label: "笔记本", range: "992 - 1279px" };
  }
  return { key: "xl", label: "桌面大屏", range: ">= 1280px" };
}

function orientationLabel(width, height) {
  return width >= height ? "横向" : "纵向";
}

function updateViewport() {
  viewport.value = {
    width: window.innerWidth,
    height: window.innerHeight,
    pixelRatio: window.devicePixelRatio || 1,
  };
}

function clearOutput() {
  outputVisible.value = false;
  showToast({
    type: "info",
    title: "已清空输出",
    message: "当前检测结果已隐藏。",
    duration: 1800,
  });
}

function refreshOutput() {
  outputVisible.value = true;
  updateViewport();
  showToast({
    type: "success",
    title: "已重新检测",
    message: "响应式信息已刷新。",
    duration: 1800,
  });
}

const currentBreakpoint = computed(() => detectBreakpoint(viewport.value.width));
const previewWidth = computed(() => Math.min(420, Math.max(180, viewport.value.width / 3)));

const breakpointList = [
  { key: "xs", label: "XS", range: "< 576px" },
  { key: "sm", label: "SM", range: "576 - 767px" },
  { key: "md", label: "MD", range: "768 - 991px" },
  { key: "lg", label: "LG", range: "992 - 1279px" },
  { key: "xl", label: "XL", range: ">= 1280px" },
];

onMounted(() => {
  updateViewport();
  window.addEventListener("resize", updateViewport);
});

onBeforeUnmount(() => {
  window.removeEventListener("resize", updateViewport);
});
</script>

<template>
  <section class="tool-form local-tool-panel">
    <div class="local-tool-header">
      <div class="local-tool-header-bar">
        <div>
          <h3>响应式布局检测</h3>
          <p>拖动浏览器窗口时，断点、方向和像素比会实时更新。</p>
        </div>
        <div class="result-actions">
          <button type="button" class="secondary-button" @click="refreshOutput">重新检测</button>
          <button type="button" class="secondary-button" @click="clearOutput">清空输出</button>
        </div>
      </div>
    </div>

    <template v-if="outputVisible">
      <div class="insight-grid">
        <article class="insight-card">
          <span class="insight-label">当前断点</span>
          <strong class="insight-value">{{ currentBreakpoint.label }}</strong>
        </article>
        <article class="insight-card">
          <span class="insight-label">视口尺寸</span>
          <strong class="insight-value">{{ viewport.width }} × {{ viewport.height }}</strong>
        </article>
        <article class="insight-card">
          <span class="insight-label">屏幕方向</span>
          <strong class="insight-value">{{ orientationLabel(viewport.width, viewport.height) }}</strong>
        </article>
        <article class="insight-card">
          <span class="insight-label">设备像素比</span>
          <strong class="insight-value">{{ viewport.pixelRatio }}</strong>
        </article>
      </div>

      <section class="result-panel">
        <div class="result-panel-head">
          <h3>断点命中</h3>
        </div>
        <div class="breakpoint-row">
          <article
            v-for="item in breakpointList"
            :key="item.key"
            class="breakpoint-card"
            :class="{ active: item.key === currentBreakpoint.key }"
          >
            <strong>{{ item.label }}</strong>
            <span>{{ item.range }}</span>
          </article>
        </div>
      </section>

      <section class="result-panel">
        <div class="result-panel-head">
          <h3>预览比例</h3>
        </div>
        <div class="device-preview-shell">
          <div class="device-preview" :style="{ width: `${previewWidth}px` }">
            <div class="device-preview-bar"></div>
            <div class="device-preview-body">
              <span>{{ currentBreakpoint.label }}</span>
              <small>{{ currentBreakpoint.range }}</small>
            </div>
          </div>
        </div>
      </section>
    </template>
    <section v-else class="result-panel">
      <div class="result-panel-head">
        <h3>结果</h3>
      </div>
      <p class="empty-hint">输出已清空，可点击“重新检测”再次读取当前窗口状态。</p>
    </section>
  </section>
</template>
