<script setup>
// 文件说明：定义 ToolKeyboardTester 前端组件。
import { onBeforeUnmount, onMounted, ref } from "vue";
import KeyboardVisualizer from "./keyboard-tester-render/KeyboardVisualizer.vue";

defineProps({
  tool: {
    type: Object,
    required: true,
  },
});

function createKey({
  id,
  label,
  code,
  widthRatio = 1,
  secondaryLabel = "",
  secondaryPlacement = "top",
  state = "default",
  activeState = "activeGreen",
  section,
  align = "left",
  colSpan = 1,
  rowSpan = 1,
}) {
  return {
    id,
    label,
    secondaryLabel,
    secondaryPlacement,
    code,
    widthRatio,
    state,
    activeState,
    section,
    align,
    colSpan,
    rowSpan,
  };
}

function createSpacer(widthRatio = 1) {
  return {
    id: `spacer-${Math.random().toString(36).slice(2)}`,
    spacer: true,
    widthRatio,
  };
}

const keyboardLayout = {
  topLeft: [
    createKey({ id: "escape", label: "Esc", code: "Escape", widthRatio: 1.12, section: "top" }),
  ],
  functionGroups: [
    [
      createKey({ id: "f1", label: "F1", code: "F1", section: "top" }),
      createKey({ id: "f2", label: "F2", code: "F2", section: "top" }),
      createKey({ id: "f3", label: "F3", code: "F3", section: "top" }),
      createKey({ id: "f4", label: "F4", code: "F4", section: "top" }),
    ],
    [
      createKey({ id: "f5", label: "F5", code: "F5", section: "top" }),
      createKey({ id: "f6", label: "F6", code: "F6", section: "top" }),
      createKey({ id: "f7", label: "F7", code: "F7", section: "top" }),
      createKey({ id: "f8", label: "F8", code: "F8", section: "top" }),
    ],
    [
      createKey({ id: "f9", label: "F9", code: "F9", section: "top" }),
      createKey({ id: "f10", label: "F10", code: "F10", section: "top" }),
      createKey({ id: "f11", label: "F11", code: "F11", section: "top" }),
      createKey({ id: "f12", label: "F12", code: "F12", section: "top" }),
    ],
  ],
  editorTopRow: [
    createKey({
      id: "print-screen",
      label: "Print",
      secondaryLabel: "Screen",
      secondaryPlacement: "bottom",
      code: "PrintScreen",
      section: "top",
    }),
    createKey({
      id: "scroll-lock",
      label: "Scroll",
      secondaryLabel: "Lock",
      secondaryPlacement: "bottom",
      code: "ScrollLock",
      section: "top",
    }),
    createKey({
      id: "pause-break",
      label: "Pause",
      secondaryLabel: "Break",
      secondaryPlacement: "bottom",
      code: "Pause",
      section: "top",
    }),
  ],
  mainRows: [
    [
      createKey({ id: "backquote", label: "`", secondaryLabel: "~", code: "Backquote", section: "main" }),
      createKey({ id: "digit-1", label: "1", secondaryLabel: "!", code: "Digit1", section: "main" }),
      createKey({ id: "digit-2", label: "2", secondaryLabel: "@", code: "Digit2", section: "main" }),
      createKey({ id: "digit-3", label: "3", secondaryLabel: "#", code: "Digit3", section: "main" }),
      createKey({ id: "digit-4", label: "4", secondaryLabel: "$", code: "Digit4", section: "main" }),
      createKey({ id: "digit-5", label: "5", secondaryLabel: "%", code: "Digit5", section: "main" }),
      createKey({ id: "digit-6", label: "6", secondaryLabel: "^", code: "Digit6", section: "main" }),
      createKey({ id: "digit-7", label: "7", secondaryLabel: "&", code: "Digit7", section: "main" }),
      createKey({ id: "digit-8", label: "8", secondaryLabel: "*", code: "Digit8", section: "main" }),
      createKey({ id: "digit-9", label: "9", secondaryLabel: "(", code: "Digit9", section: "main" }),
      createKey({ id: "digit-0", label: "0", secondaryLabel: ")", code: "Digit0", section: "main" }),
      createKey({ id: "minus", label: "-", secondaryLabel: "_", code: "Minus", section: "main" }),
      createKey({ id: "equal", label: "=", secondaryLabel: "+", code: "Equal", section: "main" }),
      createKey({ id: "backspace", label: "Backspace", code: "Backspace", widthRatio: 1.9, section: "main" }),
    ],
    [
      createKey({ id: "tab", label: "Tab", code: "Tab", widthRatio: 1.48, section: "main" }),
      createKey({ id: "key-q", label: "Q", code: "KeyQ", section: "main" }),
      createKey({ id: "key-w", label: "W", code: "KeyW", section: "main" }),
      createKey({ id: "key-e", label: "E", code: "KeyE", section: "main" }),
      createKey({ id: "key-r", label: "R", code: "KeyR", section: "main" }),
      createKey({ id: "key-t", label: "T", code: "KeyT", section: "main" }),
      createKey({ id: "key-y", label: "Y", code: "KeyY", section: "main" }),
      createKey({ id: "key-u", label: "U", code: "KeyU", section: "main" }),
      createKey({ id: "key-i", label: "I", code: "KeyI", section: "main" }),
      createKey({ id: "key-o", label: "O", code: "KeyO", section: "main" }),
      createKey({ id: "key-p", label: "P", code: "KeyP", section: "main" }),
      createKey({ id: "bracket-left", label: "[", secondaryLabel: "{", code: "BracketLeft", section: "main" }),
      createKey({ id: "bracket-right", label: "]", secondaryLabel: "}", code: "BracketRight", section: "main" }),
      createKey({ id: "backslash", label: "\\", secondaryLabel: "|", code: "Backslash", widthRatio: 1.42, section: "main" }),
    ],
    [
      createKey({ id: "caps-lock", label: "CapsLock", code: "CapsLock", widthRatio: 1.72, section: "main" }),
      createKey({ id: "key-a", label: "A", code: "KeyA", section: "main" }),
      createKey({ id: "key-s", label: "S", code: "KeyS", section: "main" }),
      createKey({ id: "key-d", label: "D", code: "KeyD", section: "main" }),
      createKey({ id: "key-f", label: "F", code: "KeyF", section: "main" }),
      createKey({ id: "key-g", label: "G", code: "KeyG", section: "main" }),
      createKey({ id: "key-h", label: "H", code: "KeyH", section: "main" }),
      createKey({ id: "key-j", label: "J", code: "KeyJ", section: "main" }),
      createKey({ id: "key-k", label: "K", code: "KeyK", section: "main" }),
      createKey({ id: "key-l", label: "L", code: "KeyL", section: "main" }),
      createKey({ id: "semicolon", label: ";", secondaryLabel: ":", code: "Semicolon", section: "main" }),
      createKey({ id: "quote", label: "'", secondaryLabel: '"', code: "Quote", section: "main" }),
      createKey({ id: "enter", label: "Enter", code: "Enter", widthRatio: 2.18, section: "main" }),
    ],
    [
      createKey({ id: "shift-left", label: "Shift", code: "ShiftLeft", widthRatio: 2.2, activeState: "activeGreen", section: "main" }),
      createKey({ id: "key-z", label: "Z", code: "KeyZ", section: "main" }),
      createKey({ id: "key-x", label: "X", code: "KeyX", section: "main" }),
      createKey({ id: "key-c", label: "C", code: "KeyC", section: "main" }),
      createKey({ id: "key-v", label: "V", code: "KeyV", section: "main" }),
      createKey({ id: "key-b", label: "B", code: "KeyB", section: "main" }),
      createKey({ id: "key-n", label: "N", code: "KeyN", section: "main" }),
      createKey({ id: "key-m", label: "M", code: "KeyM", section: "main" }),
      createKey({ id: "comma", label: ",", secondaryLabel: "<", code: "Comma", section: "main" }),
      createKey({ id: "period", label: ".", secondaryLabel: ">", code: "Period", section: "main" }),
      createKey({ id: "slash", label: "/", secondaryLabel: "?", code: "Slash", section: "main" }),
      createKey({ id: "shift-right", label: "Shift", code: "ShiftRight", widthRatio: 2.64, activeState: "activeGreen", section: "main" }),
    ],
    [
      createKey({ id: "control-left", label: "Ctrl", code: "ControlLeft", widthRatio: 1.1, activeState: "activeYellow", section: "main" }),
      createKey({ id: "meta-left", label: "Win", code: "MetaLeft", widthRatio: 1.08, activeState: "activeYellow", section: "main" }),
      createKey({ id: "alt-left", label: "Alt", code: "AltLeft", widthRatio: 1.08, section: "main" }),
      createKey({ id: "space", label: "Space", code: "Space", widthRatio: 5.92, activeState: "activeGreen", section: "main", align: "center" }),
      createKey({ id: "alt-right", label: "Alt", code: "AltRight", widthRatio: 1.08, section: "main" }),
      createKey({ id: "meta-right", label: "Win", code: "MetaRight", widthRatio: 1.08, activeState: "activeYellow", section: "main" }),
      createKey({ id: "menu", label: "Menu", code: "ContextMenu", widthRatio: 1.08, section: "main" }),
      createKey({ id: "control-right", label: "Ctrl", code: "ControlRight", widthRatio: 1.1, activeState: "activeYellow", section: "main" }),
    ],
  ],
  editRows: [
    [
      createKey({ id: "insert", label: "Insert", code: "Insert", section: "edit" }),
      createKey({ id: "home", label: "Home", code: "Home", section: "edit" }),
      createKey({ id: "page-up", label: "Page", secondaryLabel: "Up", secondaryPlacement: "bottom", code: "PageUp", section: "edit" }),
    ],
    [
      createKey({ id: "delete", label: "Delete", code: "Delete", section: "edit" }),
      createKey({ id: "end", label: "End", code: "End", section: "edit" }),
      createKey({ id: "page-down", label: "Page", secondaryLabel: "Down", secondaryPlacement: "bottom", code: "PageDown", section: "edit" }),
    ],
  ],
  arrowRows: [
    [createSpacer(), createKey({ id: "arrow-up", label: "↑", code: "ArrowUp", section: "arrow", align: "center" }), createSpacer()],
    [
      createKey({ id: "arrow-left", label: "←", code: "ArrowLeft", section: "arrow", align: "center" }),
      createKey({ id: "arrow-down", label: "↓", code: "ArrowDown", section: "arrow", align: "center" }),
      createKey({ id: "arrow-right", label: "→", code: "ArrowRight", section: "arrow", align: "center" }),
    ],
  ],
  numpadKeys: [
    createKey({ id: "num-lock", label: "Num", secondaryLabel: "Lock", secondaryPlacement: "bottom", code: "NumLock", section: "numpad" }),
    createKey({ id: "numpad-divide", label: "/", code: "NumpadDivide", section: "numpad", align: "center" }),
    createKey({ id: "numpad-multiply", label: "*", code: "NumpadMultiply", section: "numpad", align: "center" }),
    createKey({ id: "numpad-subtract", label: "-", code: "NumpadSubtract", section: "numpad", align: "center" }),
    createKey({ id: "numpad-7", label: "7", secondaryLabel: "Home", secondaryPlacement: "bottom", code: "Numpad7", section: "numpad" }),
    createKey({ id: "numpad-8", label: "8", secondaryLabel: "↑", secondaryPlacement: "bottom", code: "Numpad8", section: "numpad" }),
    createKey({ id: "numpad-9", label: "9", secondaryLabel: "PgUp", secondaryPlacement: "bottom", code: "Numpad9", section: "numpad" }),
    createKey({ id: "numpad-add", label: "+", code: "NumpadAdd", section: "numpad", align: "center", rowSpan: 2 }),
    createKey({ id: "numpad-4", label: "4", secondaryLabel: "←", secondaryPlacement: "bottom", code: "Numpad4", section: "numpad" }),
    createKey({ id: "numpad-5", label: "5", secondaryLabel: "↑", secondaryPlacement: "bottom", code: "Numpad5", section: "numpad" }),
    createKey({ id: "numpad-6", label: "6", secondaryLabel: "→", secondaryPlacement: "bottom", code: "Numpad6", section: "numpad" }),
    createKey({ id: "numpad-1", label: "1", secondaryLabel: "End", secondaryPlacement: "bottom", code: "Numpad1", section: "numpad" }),
    createKey({ id: "numpad-2", label: "2", secondaryLabel: "↓", secondaryPlacement: "bottom", code: "Numpad2", section: "numpad" }),
    createKey({ id: "numpad-3", label: "3", secondaryLabel: "PgDn", secondaryPlacement: "bottom", code: "Numpad3", section: "numpad" }),
    createKey({ id: "numpad-enter", label: "Enter", code: "NumpadEnter", section: "numpad", rowSpan: 2 }),
    createKey({ id: "numpad-0", label: "0", secondaryLabel: "Ins", secondaryPlacement: "bottom", code: "Numpad0", section: "numpad", colSpan: 2 }),
    createKey({ id: "numpad-decimal", label: ".", secondaryLabel: "Del", secondaryPlacement: "bottom", code: "NumpadDecimal", section: "numpad" }),
  ],
};

const pressedKeys = ref({});
const testedKeys = ref({});
const lastKey = ref({
  label: "--",
  code: "--",
  keyCode: "--",
});
const audioAvailable = ref(true);

let audioContext = null;
let masterGain = null;
let clickNoiseBuffer = null;
const lastPlaybackAt = new Map();
const listenerOptions = { capture: true };
const modifierCodeSet = new Set([
  "ControlLeft",
  "ControlRight",
  "ShiftLeft",
  "ShiftRight",
  "AltLeft",
  "AltRight",
  "MetaLeft",
  "MetaRight",
]);

function suppressKeyboardEvent(event) {
  if (event.cancelable) {
    event.preventDefault();
  }
  event.stopPropagation();
}

function setKeyPressed(code, pressed) {
  const next = { ...pressedKeys.value };
  if (pressed) {
    next[code] = true;
  } else {
    delete next[code];
  }
  pressedKeys.value = next;
}

function markKeyTested(code) {
  testedKeys.value = {
    ...testedKeys.value,
    [code]: true,
  };
}

function isModifierCode(code) {
  return modifierCodeSet.has(code);
}

function removeOtherNonModifierKeys(keepCode) {
  const next = { ...pressedKeys.value };
  for (const code of Object.keys(next)) {
    if (code !== keepCode && !isModifierCode(code)) {
      delete next[code];
    }
  }
  pressedKeys.value = next;
}

function clearNonModifierKeys() {
  const next = { ...pressedKeys.value };
  for (const code of Object.keys(next)) {
    if (!isModifierCode(code)) {
      delete next[code];
    }
  }
  pressedKeys.value = next;
}

function hasAnyModifierPressed(event) {
  return Boolean(event.ctrlKey || event.altKey || event.metaKey || event.shiftKey);
}

function getDisplayKeyLabel(event) {
  if (event.key === " ") {
    return "Space";
  }
  return event.key?.length === 1 ? event.key.toUpperCase() : event.key;
}

function getToneFrequency(code) {
  let total = 0;
  for (const char of code) {
    total += char.charCodeAt(0);
  }
  const toneScale = [620, 680, 740, 820, 900, 960];
  return toneScale[total % toneScale.length];
}

async function ensureAudioContext() {
  if (typeof window === "undefined") {
    return null;
  }

  const AudioContextClass = window.AudioContext || window.webkitAudioContext;
  if (!AudioContextClass) {
    audioAvailable.value = false;
    return null;
  }

  if (!audioContext) {
    audioContext = new AudioContextClass();
    masterGain = audioContext.createGain();
    masterGain.gain.value = 0.17;
    masterGain.connect(audioContext.destination);
  }

  if (audioContext.state === "suspended") {
    await audioContext.resume();
  }

  return audioContext;
}

function getNoiseBuffer(context) {
  if (clickNoiseBuffer) {
    return clickNoiseBuffer;
  }

  const duration = 0.03;
  const frameCount = Math.floor(context.sampleRate * duration);
  const buffer = context.createBuffer(1, frameCount, context.sampleRate);
  const channel = buffer.getChannelData(0);

  for (let index = 0; index < frameCount; index += 1) {
    const decay = 1 - index / frameCount;
    channel[index] = (Math.random() * 2 - 1) * decay * decay;
  }

  clickNoiseBuffer = buffer;
  return buffer;
}

async function playKeyClick(code) {
  const nowMs = performance.now();
  const lastPlayedAt = lastPlaybackAt.get(code) || 0;
  if (nowMs - lastPlayedAt < 40) {
    return;
  }
  lastPlaybackAt.set(code, nowMs);

  const context = await ensureAudioContext();
  if (!context || !masterGain) {
    return;
  }

  const now = context.currentTime;
  const frequency = getToneFrequency(code);

  const noiseSource = context.createBufferSource();
  noiseSource.buffer = getNoiseBuffer(context);
  const noiseFilter = context.createBiquadFilter();
  noiseFilter.type = "highpass";
  noiseFilter.frequency.setValueAtTime(1500, now);
  const noiseGain = context.createGain();
  noiseGain.gain.setValueAtTime(0.0001, now);
  noiseGain.gain.exponentialRampToValueAtTime(0.18, now + 0.001);
  noiseGain.gain.exponentialRampToValueAtTime(0.0001, now + 0.018);

  const oscillator = context.createOscillator();
  oscillator.type = "triangle";
  oscillator.frequency.setValueAtTime(frequency, now);
  oscillator.frequency.exponentialRampToValueAtTime(frequency * 0.72, now + 0.03);
  const toneGain = context.createGain();
  toneGain.gain.setValueAtTime(0.0001, now);
  toneGain.gain.exponentialRampToValueAtTime(0.07, now + 0.001);
  toneGain.gain.exponentialRampToValueAtTime(0.0001, now + 0.03);

  noiseSource.connect(noiseFilter);
  noiseFilter.connect(noiseGain);
  noiseGain.connect(masterGain);

  oscillator.connect(toneGain);
  toneGain.connect(masterGain);

  noiseSource.start(now);
  noiseSource.stop(now + 0.03);
  oscillator.start(now);
  oscillator.stop(now + 0.032);
}

async function handleKeydown(event) {
  suppressKeyboardEvent(event);

  if (pressedKeys.value[event.code] && event.repeat) {
    return;
  }

  if (!isModifierCode(event.code) && (event.ctrlKey || event.altKey || event.metaKey)) {
    removeOtherNonModifierKeys(event.code);
  }

  setKeyPressed(event.code, true);
  markKeyTested(event.code);
  lastKey.value = {
    label: getDisplayKeyLabel(event),
    code: event.code,
    keyCode: event.which || event.keyCode || "--",
  };
  await playKeyClick(event.code);
}

function handleKeyup(event) {
  suppressKeyboardEvent(event);
  setKeyPressed(event.code, false);

  if (isModifierCode(event.code) && !hasAnyModifierPressed(event)) {
    clearNonModifierKeys();
  }
}

function clearPressedKeys() {
  pressedKeys.value = {};
}

async function primeAudio() {
  await ensureAudioContext();
}

onMounted(() => {
  window.addEventListener("keydown", handleKeydown, listenerOptions);
  window.addEventListener("keyup", handleKeyup, listenerOptions);
  window.addEventListener("blur", clearPressedKeys);
  document.addEventListener("visibilitychange", clearPressedKeys);
  window.addEventListener("pointerdown", primeAudio, { passive: true });
});

onBeforeUnmount(() => {
  window.removeEventListener("keydown", handleKeydown, listenerOptions);
  window.removeEventListener("keyup", handleKeyup, listenerOptions);
  window.removeEventListener("blur", clearPressedKeys);
  document.removeEventListener("visibilitychange", clearPressedKeys);
  window.removeEventListener("pointerdown", primeAudio);

  if (audioContext && audioContext.state !== "closed") {
    audioContext.close();
  }
  audioContext = null;
  masterGain = null;
});
</script>

<template>
  <section class="tool-form keyboard-tester-shell">
    <KeyboardVisualizer
      :layout="keyboardLayout"
      :pressed-keys="pressedKeys"
      :tested-keys="testedKeys"
      :last-key="lastKey"
      :audio-available="audioAvailable"
    />
  </section>
</template>

<style scoped>
.keyboard-tester-shell {
  overflow: hidden;
}
</style>
