<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from "vue";

import { showToast } from "../utils/toast.js";

const now = ref(Date.now());
const outputVisible = ref(true);

function touchSupport() {
  return "ontouchstart" in window || navigator.maxTouchPoints > 0;
}

function collectInfo() {
  return {
    language: navigator.language || "unknown",
    platform: navigator.userAgentData?.platform || navigator.platform || "unknown",
    userAgent: navigator.userAgent || "unknown",
    cookieEnabled: navigator.cookieEnabled ? "已启用" : "已禁用",
    online: navigator.onLine ? "在线" : "离线",
    cores: navigator.hardwareConcurrency || "unknown",
    memory: navigator.deviceMemory ? `${navigator.deviceMemory} GB` : "unknown",
    timezone: Intl.DateTimeFormat().resolvedOptions().timeZone || "unknown",
    viewport: `${window.innerWidth} × ${window.innerHeight}`,
    screen: `${window.screen.width} × ${window.screen.height}`,
    pixelRatio: window.devicePixelRatio || 1,
    touch: touchSupport() ? "支持" : "不支持",
    url: window.location.href,
  };
}

function handleUpdate() {
  now.value = Date.now();
}

function clearOutput() {
  outputVisible.value = false;
  showToast({
    type: "info",
    title: "已清空输出",
    message: "浏览器环境信息已从当前页面隐藏。",
    duration: 1800,
  });
}

function refreshOutput() {
  outputVisible.value = true;
  handleUpdate();
  showToast({
    type: "success",
    title: "已重新读取",
    message: "浏览器环境信息已刷新。",
    duration: 1800,
  });
}

const info = computed(() => {
  void now.value;
  return collectInfo();
});

const entries = computed(() => {
  return [
    ["系统平台", info.value.platform],
    ["浏览器语言", info.value.language],
    ["网络状态", info.value.online],
    ["Cookie", info.value.cookieEnabled],
    ["逻辑核心数", info.value.cores],
    ["设备内存", info.value.memory],
    ["时区", info.value.timezone],
    ["视口尺寸", info.value.viewport],
    ["屏幕尺寸", info.value.screen],
    ["像素比", info.value.pixelRatio],
    ["触控支持", info.value.touch],
  ];
});

onMounted(() => {
  window.addEventListener("resize", handleUpdate);
  window.addEventListener("online", handleUpdate);
  window.addEventListener("offline", handleUpdate);
});

onBeforeUnmount(() => {
  window.removeEventListener("resize", handleUpdate);
  window.removeEventListener("online", handleUpdate);
  window.removeEventListener("offline", handleUpdate);
});
</script>

<template>
  <section class="tool-form local-tool-panel">
    <div class="local-tool-header">
      <div class="local-tool-header-bar">
        <div>
          <h3>当前浏览器环境</h3>
          <p>以下信息直接从你当前浏览器读取，不会提交到后端。</p>
        </div>
        <div class="result-actions">
          <button type="button" class="secondary-button" @click="refreshOutput">重新读取</button>
          <button type="button" class="secondary-button" @click="clearOutput">清空输出</button>
        </div>
      </div>
    </div>

    <template v-if="outputVisible">
      <div class="insight-grid">
        <article v-for="[label, value] in entries" :key="label" class="insight-card">
          <span class="insight-label">{{ label }}</span>
          <strong class="insight-value">{{ value }}</strong>
        </article>
      </div>

      <section class="result-panel">
        <div class="result-panel-head">
          <h3>用户代理</h3>
        </div>
        <pre>{{ info.userAgent }}</pre>
      </section>

      <section class="result-panel">
        <div class="result-panel-head">
          <h3>当前页面地址</h3>
        </div>
        <pre>{{ info.url }}</pre>
      </section>
    </template>
    <section v-else class="result-panel">
      <div class="result-panel-head">
        <h3>结果</h3>
      </div>
      <p class="empty-hint">输出已清空，可点击“重新读取”再次获取当前浏览器信息。</p>
    </section>
  </section>
</template>
