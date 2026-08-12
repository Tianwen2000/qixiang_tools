<script setup>
// 文件说明：定义 AI 助手的 AiAssistantWidget 组件或辅助逻辑。
import { computed, nextTick, onMounted, onUnmounted, ref } from "vue";

import AiChatPanel from "./AiChatPanel.vue";
import AuthDialog from "./AuthDialog.vue";
import { AUTH_STATE_CHANGED_EVENT, refreshCurrentUser } from "./service.js";
import { showToast } from "../../utils/toast.js";

const panelOpen = ref(false);
const authOpen = ref(false);
const authMode = ref("login");
const panelRef = ref(null);
const widgetRef = ref(null);
const widgetPosition = ref({ x: 0, y: 0 });
const positionReady = ref(false);
const dragging = ref(false);
let authChangeToastShown = false;
let suppressNextClick = false;
let resizeFrame = 0;

const DRAG_THRESHOLD_PX = 5;
const dragState = {
  pointerId: null,
  startX: 0,
  startY: 0,
  originX: 0,
  originY: 0,
  moved: false,
};

const AUTH_CHANGE_MESSAGE = "检测到当前账号已在其他标签页切换，请刷新页面后继续操作。";
const widgetStyle = computed(() =>
  positionReady.value
    ? {
        left: `${widgetPosition.value.x}px`,
        top: `${widgetPosition.value.y}px`,
      }
    : undefined,
);

function togglePanel() {
  panelOpen.value = !panelOpen.value;
}

function clampWidgetPosition(x, y) {
  const node = widgetRef.value;
  const width = node?.offsetWidth || 0;
  const height = node?.offsetHeight || 0;
  const maxX = Math.max(0, window.innerWidth - width);
  const maxY = Math.max(0, window.innerHeight - height);
  return {
    x: Math.round(Math.min(Math.max(0, x), maxX)),
    y: Math.round(Math.min(Math.max(0, y), maxY)),
  };
}

function setWidgetPosition(x, y) {
  widgetPosition.value = clampWidgetPosition(x, y);
}

function initializeWidgetPosition() {
  const node = widgetRef.value;
  if (!node) return;
  const rect = node.getBoundingClientRect();
  setWidgetPosition(rect.left, rect.top);
  positionReady.value = true;
}

function keepWidgetInViewport() {
  if (!positionReady.value) return;
  setWidgetPosition(widgetPosition.value.x, widgetPosition.value.y);
}

function handleViewportResize() {
  window.cancelAnimationFrame(resizeFrame);
  resizeFrame = window.requestAnimationFrame(keepWidgetInViewport);
}

function resetDragState() {
  dragState.pointerId = null;
  dragState.moved = false;
  dragging.value = false;
}

function startRobotDrag(event) {
  if ((event.pointerType === "mouse" && event.button !== 0) || dragState.pointerId !== null) {
    return;
  }
  suppressNextClick = false;
  dragState.pointerId = event.pointerId;
  dragState.startX = event.clientX;
  dragState.startY = event.clientY;
  dragState.originX = widgetPosition.value.x;
  dragState.originY = widgetPosition.value.y;
  dragState.moved = false;
  event.currentTarget.setPointerCapture?.(event.pointerId);
}

function moveRobot(event) {
  if (event.pointerId !== dragState.pointerId) return;
  const deltaX = event.clientX - dragState.startX;
  const deltaY = event.clientY - dragState.startY;
  if (!dragState.moved && Math.hypot(deltaX, deltaY) < DRAG_THRESHOLD_PX) {
    return;
  }
  dragState.moved = true;
  dragging.value = true;
  event.preventDefault();
  setWidgetPosition(dragState.originX + deltaX, dragState.originY + deltaY);
}

function finishRobotDrag(event) {
  if (event.pointerId !== dragState.pointerId) return;
  suppressNextClick = dragState.moved;
  if (event.currentTarget.hasPointerCapture?.(event.pointerId)) {
    event.currentTarget.releasePointerCapture(event.pointerId);
  }
  resetDragState();
}

function cancelRobotDrag(event) {
  if (event?.pointerId != null && event.pointerId !== dragState.pointerId) return;
  resetDragState();
}

function handleRobotClick(event) {
  if (suppressNextClick) {
    suppressNextClick = false;
    event.preventDefault();
    return;
  }
  togglePanel();
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
  window.addEventListener("focus", refreshCurrentUserOnResume);
  document.addEventListener("visibilitychange", handleVisibilityChange);
  window.addEventListener(AUTH_STATE_CHANGED_EVENT, handleAuthStateChanged);
  window.addEventListener("resize", handleViewportResize);
  window.addEventListener("blur", cancelRobotDrag);
  nextTick(initializeWidgetPosition);
});

onUnmounted(() => {
  window.removeEventListener("focus", refreshCurrentUserOnResume);
  document.removeEventListener("visibilitychange", handleVisibilityChange);
  window.removeEventListener(AUTH_STATE_CHANGED_EVENT, handleAuthStateChanged);
  window.removeEventListener("resize", handleViewportResize);
  window.removeEventListener("blur", cancelRobotDrag);
  window.cancelAnimationFrame(resizeFrame);
});

function handleVisibilityChange() {
  if (!document.hidden) {
    refreshCurrentUserOnResume();
  }
}

function refreshCurrentUserOnResume() {
  refreshCurrentUser({ notifyOnChange: true });
}

function handleAuthStateChanged() {
  if (authChangeToastShown) return;
  authChangeToastShown = true;
  showToast({
    type: "warning",
    title: "登录状态已变化",
    message: AUTH_CHANGE_MESSAGE,
    duration: 0,
  });
}
</script>

<template>
  <div
    ref="widgetRef"
    class="qxai-widget"
    :class="{ 'has-position': positionReady, 'is-dragging': dragging }"
    :style="widgetStyle"
  >
    <button
      type="button"
      class="qxai-robot"
      :class="{ 'is-active': panelOpen }"
      :aria-label="panelOpen ? '关闭 AI 助手' : '打开 AI 助手'"
      :aria-expanded="panelOpen"
      @click="handleRobotClick"
      @pointerdown="startRobotDrag"
      @pointermove="moveRobot"
      @pointerup="finishRobotDrag"
      @pointercancel="cancelRobotDrag"
      @lostpointercapture="cancelRobotDrag"
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

.qxai-widget.has-position {
  right: auto;
  transform: none;
}

.qxai-robot {
  position: relative;
  width: 152px;
  height: 152px;
  border: none;
  cursor: grab;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
  background: transparent;
  touch-action: none;
  user-select: none;
  -webkit-user-select: none;
  animation: qxai-bob 3.4s ease-in-out infinite;
  transition: transform 0.18s;
}

.qxai-widget:not(.is-dragging) .qxai-robot:hover {
  transform: translateY(-2px) scale(1.04);
}

.qxai-widget.is-dragging .qxai-robot {
  cursor: grabbing;
  animation: none;
  transition: none;
  transform: none;
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
