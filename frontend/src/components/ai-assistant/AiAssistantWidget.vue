<script setup>
import { nextTick, onMounted, ref } from "vue";

import AiChatPanel from "./AiChatPanel.vue";
import AuthDialog from "./AuthDialog.vue";
import { refreshCurrentUser } from "./service.js";

const panelOpen = ref(false);
const authOpen = ref(false);
const authMode = ref("login");
const panelRef = ref(null);

function togglePanel() {
  panelOpen.value = !panelOpen.value;
}

function closePanel() {
  panelOpen.value = false;
}

function openAuth() {
  authMode.value = "login";
  authOpen.value = true;
}

function closeAuth() {
  authOpen.value = false;
}

function onAuthSuccess() {
  authOpen.value = false;
  // 登录成功后，若对话框里还留着待发送内容则自动补发。
  nextTick(() => panelRef.value?.resumeSend?.());
}

onMounted(() => {
  // 还原本地登录态：顺带校验 token 是否仍有效，失效会被自动清除。
  refreshCurrentUser();
});
</script>

<template>
  <div class="qxai-widget">
    <button
      type="button"
      class="qxai-robot"
      :class="{ 'is-active': panelOpen }"
      :aria-label="panelOpen ? '关闭 AI 助手' : '打开 AI 助手'"
      :aria-expanded="panelOpen"
      @click="togglePanel"
    >
      <img
        class="qxai-robot-image"
        src="/ai-robot-tianwen-smooth-animation.gif"
        alt=""
        aria-hidden="true"
      />
    </button>

    <AiChatPanel
      v-if="panelOpen"
      ref="panelRef"
      @close="closePanel"
      @need-auth="openAuth"
    />

    <AuthDialog
      v-if="authOpen"
      :initial-mode="authMode"
      @close="closeAuth"
      @success="onAuthSuccess"
    />
  </div>
</template>

<style scoped>
.qxai-widget {
  position: fixed;
  top: 50%;
  right: 0;
  transform: translateY(-50%);
  z-index: 950;
}

.qxai-robot {
  position: relative;
  width: 152px;
  height: 152px;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
  background: transparent;
  animation: qxai-bob 3.4s ease-in-out infinite;
  transition: transform 0.18s;
}

.qxai-robot:hover {
  transform: translateY(-2px) scale(1.04);
}

/* 待机：缓慢上下浮动 */
@keyframes qxai-bob {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-5px);
  }
}

.qxai-robot-image {
  position: relative;
  z-index: 1;
  width: 100%;
  height: 100%;
  object-fit: contain;
  pointer-events: none;
}

/* ---- 运行态：点击打开后切换 ---- */
.qxai-robot.is-active {
  animation: none;
  transform: scale(1.05);
}

@media (prefers-reduced-motion: reduce) {
  .qxai-robot {
    animation: none;
  }
}

@media (max-width: 720px) {
  .qxai-widget {
    right: 0;
  }

  .qxai-robot {
    width: 124px;
    height: 124px;
  }
}
</style>
