import { reactive, readonly } from "vue";

const state = reactive({
  toasts: [],
});

const timers = new Map();
let toastSeed = 0;

function findToastIndex(id) {
  return state.toasts.findIndex((item) => item.id === id);
}

function clearToastTimer(id) {
  const timer = timers.get(id);
  if (timer) {
    window.clearTimeout(timer);
    timers.delete(id);
  }
}

function scheduleDismiss(id, duration) {
  clearToastTimer(id);
  if (!duration || duration <= 0) {
    return;
  }
  const timer = window.setTimeout(() => {
    dismissToast(id);
  }, duration);
  timers.set(id, timer);
}

export function showToast(options = {}) {
  const id = `toast-${Date.now()}-${toastSeed++}`;
  const toast = {
    id,
    type: options.type || "info",
    title: options.title || "提示",
    message: options.message || "",
    duration: options.duration ?? 2600,
  };
  state.toasts.push(toast);
  scheduleDismiss(id, toast.duration);
  return id;
}

export function updateToast(id, patch = {}) {
  const index = findToastIndex(id);
  if (index === -1) {
    return null;
  }

  const nextToast = {
    ...state.toasts[index],
    ...patch,
    id,
  };
  state.toasts.splice(index, 1, nextToast);
  scheduleDismiss(id, nextToast.duration);
  return id;
}

export function dismissToast(id) {
  clearToastTimer(id);
  const index = findToastIndex(id);
  if (index !== -1) {
    state.toasts.splice(index, 1);
  }
}

export function clearToasts() {
  state.toasts.forEach((item) => clearToastTimer(item.id));
  state.toasts.splice(0, state.toasts.length);
}

export function useToast() {
  return {
    toasts: readonly(state.toasts),
    showToast,
    updateToast,
    dismissToast,
    clearToasts,
  };
}
