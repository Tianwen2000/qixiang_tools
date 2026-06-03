<script setup>
import { computed, onBeforeUnmount, ref, watch } from "vue";

import { showToast } from "../utils/toast.js";

const props = defineProps({
  tool: {
    type: Object,
    required: true,
  },
});

const isAc = computed(() => props.tool.slug === "abstract-ac");
const isOn = ref(false);
const speed = ref(2);
const swing = ref(true);
const muted = ref(false);
const volume = ref(0.42);
const mode = ref("cool");
const temperature = ref(24);
const audioAvailable = ref(true);

const title = computed(() => (isAc.value ? "抽象小空调" : "抽象小风扇"));
const statusText = computed(() => {
  if (!isOn.value) {
    return "待机";
  }
  if (isAc.value) {
    return `${mode.value === "cool" ? "制冷" : "送风"} · ${temperature.value}℃ · ${speed.value} 档`;
  }
  return `${speed.value} 档 · ${swing.value ? "摆头" : "定向"}`;
});
const fanSpinDuration = computed(() => `${Math.max(0.34, 1.42 - speed.value * 0.28)}s`);
const airflowOpacity = computed(() => (isOn.value ? 0.28 + speed.value * 0.16 : 0));

let audioContext = null;
let noiseBuffer = null;
let activeSources = [];
let activeNodes = [];

function getAudioContext() {
  if (typeof window === "undefined") {
    return null;
  }
  if (!audioContext) {
    const AudioContextClass = window.AudioContext || window.webkitAudioContext;
    if (!AudioContextClass) {
      return null;
    }
    audioContext = new AudioContextClass();
  }
  return audioContext;
}

function createNoiseBuffer(context) {
  const length = context.sampleRate * 2;
  const buffer = context.createBuffer(1, length, context.sampleRate);
  const channel = buffer.getChannelData(0);
  for (let index = 0; index < length; index += 1) {
    channel[index] = Math.random() * 2 - 1;
  }
  return buffer;
}

function stopGraph() {
  activeSources.forEach((source) => {
    try {
      source.stop();
    } catch {
      // Source nodes can already be stopped after rapid control changes.
    }
  });
  activeNodes.forEach((node) => {
    try {
      node.disconnect();
    } catch {
      // Disconnect is best-effort for Web Audio cleanup.
    }
  });
  activeSources = [];
  activeNodes = [];
}

function buildFanSound(context, master) {
  noiseBuffer ||= createNoiseBuffer(context);
  const noise = context.createBufferSource();
  const filter = context.createBiquadFilter();
  const gain = context.createGain();
  const motor = context.createOscillator();
  const motorGain = context.createGain();

  noise.buffer = noiseBuffer;
  noise.loop = true;
  filter.type = "lowpass";
  filter.frequency.value = 520 + speed.value * 360;
  gain.gain.value = 0.13 + speed.value * 0.055;
  motor.type = "sine";
  motor.frequency.value = 78 + speed.value * 18;
  motorGain.gain.value = 0.018 + speed.value * 0.007;

  noise.connect(filter);
  filter.connect(gain);
  gain.connect(master);
  motor.connect(motorGain);
  motorGain.connect(master);
  noise.start();
  motor.start();
  activeSources.push(noise, motor);
  activeNodes.push(noise, filter, gain, motor, motorGain, master);
}

function buildAcSound(context, master) {
  noiseBuffer ||= createNoiseBuffer(context);
  const noise = context.createBufferSource();
  const filter = context.createBiquadFilter();
  const noiseGain = context.createGain();
  const compressor = context.createOscillator();
  const compressorGain = context.createGain();

  noise.buffer = noiseBuffer;
  noise.loop = true;
  filter.type = "bandpass";
  filter.frequency.value = mode.value === "cool" ? 840 : 640;
  filter.Q.value = 0.8;
  noiseGain.gain.value = 0.09 + speed.value * 0.035;
  compressor.type = "triangle";
  compressor.frequency.value = mode.value === "cool" ? 58 : 44;
  compressorGain.gain.value = mode.value === "cool" ? 0.028 : 0.015;

  noise.connect(filter);
  filter.connect(noiseGain);
  noiseGain.connect(master);
  compressor.connect(compressorGain);
  compressorGain.connect(master);
  noise.start();
  compressor.start();
  activeSources.push(noise, compressor);
  activeNodes.push(noise, filter, noiseGain, compressor, compressorGain, master);
}

function rebuildAudioGraph() {
  stopGraph();
  if (!isOn.value || muted.value || volume.value <= 0 || !audioContext) {
    return;
  }
  const master = audioContext.createGain();
  master.gain.value = Math.min(0.55, Math.max(0, volume.value));
  master.connect(audioContext.destination);
  if (isAc.value) {
    buildAcSound(audioContext, master);
  } else {
    buildFanSound(audioContext, master);
  }
}

async function activateAudio() {
  const context = getAudioContext();
  if (!context) {
    audioAvailable.value = false;
    showToast({
      type: "error",
      title: "声音不可用",
      message: "当前浏览器不支持 Web Audio。",
      duration: 2800,
    });
    return;
  }
  try {
    await context.resume();
    audioAvailable.value = true;
    rebuildAudioGraph();
  } catch (error) {
    audioAvailable.value = false;
    showToast({
      type: "error",
      title: "声音未启动",
      message: error?.message || "浏览器阻止了音频播放。",
      duration: 3200,
    });
  }
}

async function togglePower() {
  isOn.value = !isOn.value;
  if (isOn.value) {
    await activateAudio();
  } else {
    stopGraph();
  }
}

async function setSpeed(nextSpeed) {
  speed.value = nextSpeed;
  if (isOn.value) {
    await activateAudio();
  }
}

async function setMode(nextMode) {
  mode.value = nextMode;
  if (isOn.value) {
    await activateAudio();
  }
}

async function nudgeTemperature(delta) {
  temperature.value = Math.min(30, Math.max(16, temperature.value + delta));
  if (isOn.value && mode.value === "cool") {
    await activateAudio();
  }
}

async function toggleSwing() {
  swing.value = !swing.value;
  if (isOn.value) {
    await activateAudio();
  }
}

async function toggleMute() {
  muted.value = !muted.value;
  if (isOn.value) {
    await activateAudio();
  }
}

watch([volume, () => props.tool.slug], () => {
  if (audioContext) {
    rebuildAudioGraph();
  }
});

onBeforeUnmount(() => {
  stopGraph();
  if (audioContext) {
    audioContext.close();
    audioContext = null;
  }
});
</script>

<template>
  <section class="tool-form local-tool-panel abstract-appliance-tool" :class="{ ac: isAc, running: isOn }">
    <div class="local-tool-header">
      <div class="local-tool-header-bar">
        <div>
          <h3>{{ title }}</h3>
          <p>纯前端按钮和 Web Audio 声音，状态只保存在当前页面。</p>
        </div>
        <span class="appliance-state" :class="{ active: isOn }">{{ statusText }}</span>
      </div>
    </div>

    <div class="appliance-stage">
      <div v-if="!isAc" class="fan-machine" :class="{ oscillating: swing && isOn }">
        <div class="fan-cage">
          <div class="fan-ring"></div>
          <div class="fan-blades" :class="{ spinning: isOn }" :style="{ '--spin-duration': fanSpinDuration }">
            <span></span>
            <span></span>
            <span></span>
          </div>
          <div class="fan-hub"></div>
        </div>
        <div class="fan-neck"></div>
        <div class="fan-base"></div>
        <div class="fan-wind" :style="{ opacity: airflowOpacity }">
          <span></span>
          <span></span>
          <span></span>
        </div>
      </div>

      <div v-else class="ac-machine">
        <div class="ac-body">
          <div class="ac-display">{{ isOn ? `${temperature}℃` : "--" }}</div>
          <div class="ac-light" :class="{ active: isOn }"></div>
          <div class="ac-vent" :class="{ swinging: swing && isOn }">
            <span></span>
            <span></span>
            <span></span>
          </div>
        </div>
        <div class="ac-airflow" :style="{ opacity: airflowOpacity }">
          <span></span>
          <span></span>
          <span></span>
          <span></span>
        </div>
      </div>
    </div>

    <div class="appliance-controls">
      <button type="button" class="power-button" :class="{ active: isOn }" @click="togglePower">电源</button>

      <div class="appliance-control-group">
        <span>档位</span>
        <div class="segmented-buttons">
          <button v-for="item in [1, 2, 3]" :key="item" type="button" :class="{ active: speed === item }" @click="setSpeed(item)">
            {{ item }}
          </button>
        </div>
      </div>

      <div v-if="isAc" class="appliance-control-group temperature-control">
        <span>温度</span>
        <div>
          <button type="button" @click="nudgeTemperature(-1)">-</button>
          <strong>{{ temperature }}℃</strong>
          <button type="button" @click="nudgeTemperature(1)">+</button>
        </div>
      </div>

      <div v-if="isAc" class="appliance-control-group">
        <span>模式</span>
        <div class="segmented-buttons">
          <button type="button" :class="{ active: mode === 'cool' }" @click="setMode('cool')">制冷</button>
          <button type="button" :class="{ active: mode === 'wind' }" @click="setMode('wind')">送风</button>
        </div>
      </div>

      <button type="button" class="secondary-button" :class="{ active: swing }" @click="toggleSwing">{{ swing ? "摆头开" : "摆头关" }}</button>
      <button type="button" class="secondary-button" :class="{ active: muted }" @click="toggleMute">{{ muted ? "静音" : "声音" }}</button>

      <label class="volume-control">
        <span>音量</span>
        <input v-model.number="volume" type="range" min="0" max="0.55" step="0.01" :disabled="!audioAvailable" />
      </label>
    </div>
  </section>
</template>

<style scoped>
.abstract-appliance-tool {
  overflow: hidden;
}

.abstract-appliance-tool,
.abstract-appliance-tool * {
  box-sizing: border-box;
}

.local-tool-header-bar > div {
  min-width: 0;
}

.local-tool-header h3,
.local-tool-header p {
  overflow-wrap: anywhere;
}

.appliance-state {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 38px;
  padding: 0 12px;
  border-radius: 999px;
  border: 1px solid #dbe3eb;
  background: rgba(255, 255, 255, 0.86);
  color: var(--muted);
  font-weight: 700;
}

.appliance-state.active {
  border-color: rgba(45, 179, 106, 0.26);
  background: rgba(45, 179, 106, 0.12);
  color: #137345;
}

.appliance-stage {
  position: relative;
  display: grid;
  place-items: center;
  min-width: 0;
  min-height: 360px;
  border-radius: 8px;
  border: 1px solid rgba(210, 222, 234, 0.86);
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.76), rgba(237, 245, 251, 0.7)),
    repeating-linear-gradient(90deg, rgba(115, 139, 166, 0.06) 0 1px, transparent 1px 42px);
}

.fan-machine {
  position: relative;
  display: grid;
  justify-items: center;
  max-width: 100%;
  transform-origin: 50% 68%;
}

.fan-machine.oscillating {
  animation: fan-swing 2.8s ease-in-out infinite;
  will-change: transform;
}

.fan-cage {
  position: relative;
  width: min(260px, 64vw);
  aspect-ratio: 1;
  display: grid;
  place-items: center;
  border-radius: 50%;
  border: 10px solid #d9e3ed;
  background:
    repeating-radial-gradient(circle, transparent 0 18px, rgba(109, 131, 154, 0.28) 19px 21px),
    repeating-conic-gradient(from 0deg, rgba(91, 110, 130, 0.28) 0deg 2deg, transparent 2deg 15deg),
    rgba(255, 255, 255, 0.72);
  box-shadow: inset 0 0 0 8px rgba(255, 255, 255, 0.7), 0 28px 60px rgba(75, 95, 120, 0.18);
  /* 把昂贵的网罩渐变栅格化成独立合成层，摆头时只做位移而不重绘 */
  transform: translateZ(0);
  backface-visibility: hidden;
}

.fan-ring {
  position: absolute;
  inset: 20px;
  border-radius: 50%;
  border: 2px solid rgba(117, 141, 164, 0.28);
}

.fan-blades {
  position: absolute;
  width: 62%;
  aspect-ratio: 1;
  transform-origin: center;
}

.fan-blades.spinning {
  animation: fan-spin var(--spin-duration) linear infinite;
  will-change: transform;
}

.fan-blades span {
  position: absolute;
  left: 50%;
  top: 50%;
  width: 44%;
  height: 24%;
  border-radius: 80% 18% 80% 18%;
  background: linear-gradient(135deg, rgba(94, 153, 195, 0.92), rgba(198, 231, 243, 0.9));
  transform-origin: 0 50%;
}

.fan-blades span:nth-child(1) {
  transform: rotate(0deg) translateX(8px);
}

.fan-blades span:nth-child(2) {
  transform: rotate(120deg) translateX(8px);
}

.fan-blades span:nth-child(3) {
  transform: rotate(240deg) translateX(8px);
}

.fan-hub {
  position: relative;
  width: 54px;
  aspect-ratio: 1;
  border-radius: 50%;
  background: linear-gradient(135deg, #eef5fb, #8fb7d0);
  box-shadow: inset 0 3px 8px rgba(255, 255, 255, 0.7), 0 8px 18px rgba(49, 73, 96, 0.18);
}

.fan-neck {
  width: 32px;
  height: 86px;
  margin-top: -4px;
  border-radius: 20px;
  background: linear-gradient(90deg, #9cb4c9, #edf4fa 48%, #8fa9c0);
}

.fan-base {
  width: 168px;
  height: 44px;
  border-radius: 50%;
  background: linear-gradient(180deg, #f6f9fc, #b8c8d8);
  box-shadow: 0 18px 34px rgba(75, 95, 120, 0.2);
}

.fan-wind,
.ac-airflow {
  position: absolute;
  pointer-events: none;
}

.fan-wind {
  left: 62%;
  top: 30%;
  display: grid;
  gap: 22px;
}

.fan-wind span,
.ac-airflow span {
  display: block;
  width: 210px;
  height: 12px;
  border-radius: 999px;
  background: linear-gradient(90deg, rgba(89, 164, 211, 0), rgba(89, 164, 211, 0.48), rgba(89, 164, 211, 0));
  animation: airflow 1.3s ease-in-out infinite;
  will-change: transform, opacity;
}

.fan-wind span:nth-child(2),
.ac-airflow span:nth-child(2) {
  animation-delay: 0.18s;
}

.fan-wind span:nth-child(3),
.ac-airflow span:nth-child(3) {
  animation-delay: 0.36s;
}

.ac-machine {
  position: relative;
  width: min(560px, 100%);
  max-width: 100%;
  display: grid;
  justify-items: center;
  gap: 18px;
}

.ac-body {
  position: relative;
  width: 100%;
  min-width: 0;
  min-height: 154px;
  border-radius: 8px;
  border: 1px solid rgba(187, 202, 216, 0.92);
  background: linear-gradient(180deg, #ffffff, #e8f0f6);
  box-shadow: 0 26px 62px rgba(75, 95, 120, 0.18);
}

.ac-display {
  position: absolute;
  top: 26px;
  right: 34px;
  min-width: 76px;
  border-radius: 8px;
  padding: 8px 12px;
  background: #172033;
  color: #9ef7df;
  text-align: center;
  font-weight: 800;
  letter-spacing: 0;
}

.ac-light {
  position: absolute;
  top: 38px;
  left: 36px;
  width: 12px;
  aspect-ratio: 1;
  border-radius: 50%;
  background: #a5b3c0;
}

.ac-light.active {
  background: #2db36a;
  box-shadow: 0 0 18px rgba(45, 179, 106, 0.72);
}

.ac-vent {
  position: absolute;
  left: 36px;
  right: 36px;
  bottom: 28px;
  display: grid;
  gap: 8px;
  transform-origin: 50% 0;
}

.ac-vent.swinging {
  animation: vent-swing 2s ease-in-out infinite;
  will-change: transform;
}

.ac-vent span {
  height: 7px;
  border-radius: 999px;
  background: linear-gradient(90deg, #aabccc, #f8fbfd, #aabccc);
}

.ac-airflow {
  top: 158px;
  display: grid;
  justify-items: center;
  gap: 18px;
}

.ac-airflow span {
  width: min(460px, 72vw);
}

.ac-airflow span:nth-child(4) {
  animation-delay: 0.54s;
}

.appliance-controls {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  align-items: center;
  min-width: 0;
}

.appliance-controls button,
.temperature-control button {
  min-width: 72px;
  border: 1px solid #dbe3eb;
  border-radius: 14px;
  padding: 11px 13px;
  background: #fff;
  color: var(--ink);
  cursor: pointer;
}

.appliance-controls button.active,
.segmented-buttons button.active,
.power-button.active {
  border-color: transparent;
  background: linear-gradient(135deg, var(--accent) 0%, var(--accent-strong) 100%);
  color: #fff;
}

.appliance-control-group,
.volume-control {
  display: grid;
  gap: 8px;
  min-width: 120px;
  max-width: 100%;
}

.appliance-control-group > span,
.volume-control > span {
  color: var(--muted);
  font-size: 13px;
}

.segmented-buttons,
.temperature-control > div {
  display: flex;
  gap: 8px;
  align-items: center;
}

.temperature-control strong {
  min-width: 54px;
  text-align: center;
}

.volume-control input {
  width: 160px;
}

@keyframes fan-spin {
  to {
    transform: rotate(360deg);
  }
}

@keyframes fan-swing {
  0%,
  100% {
    transform: rotate(-10deg);
  }
  50% {
    transform: rotate(10deg);
  }
}

@keyframes vent-swing {
  0%,
  100% {
    transform: rotateX(0deg);
  }
  50% {
    transform: rotateX(28deg);
  }
}

@keyframes airflow {
  0% {
    transform: translateX(-18px) scaleX(0.84);
    opacity: 0;
  }
  45% {
    opacity: 1;
  }
  100% {
    transform: translateX(30px) scaleX(1);
    opacity: 0;
  }
}

@media (prefers-reduced-motion: reduce) {
  .fan-machine.oscillating,
  .fan-blades.spinning,
  .ac-vent.swinging,
  .fan-wind span,
  .ac-airflow span {
    animation: none;
  }
}

@media (max-width: 760px) {
  .abstract-appliance-tool :deep(.local-tool-header-bar) {
    min-width: 0;
  }

  .abstract-appliance-tool :deep(.local-tool-header) {
    min-width: 0;
  }

  .abstract-appliance-tool :deep(.local-tool-header h3),
  .abstract-appliance-tool :deep(.local-tool-header p) {
    overflow-wrap: anywhere;
  }

  .appliance-stage {
    min-height: 330px;
  }

  .fan-wind {
    left: 56%;
  }

  .fan-wind span {
    width: 138px;
  }

  .appliance-controls {
    align-items: stretch;
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .appliance-controls button,
  .temperature-control button {
    min-width: 0;
  }

  .appliance-control-group,
  .volume-control,
  .volume-control input {
    width: 100%;
  }

  .volume-control {
    grid-column: 1 / -1;
  }

  .segmented-buttons,
  .temperature-control > div {
    min-width: 0;
  }

  .segmented-buttons button {
    flex: 1 1 0;
  }

  /* 移动端降低大模糊阴影的填充开销，减轻摆头/旋转时的卡顿 */
  .fan-cage {
    box-shadow: inset 0 0 0 8px rgba(255, 255, 255, 0.7), 0 14px 26px rgba(75, 95, 120, 0.16);
  }

  .ac-body {
    box-shadow: 0 14px 30px rgba(75, 95, 120, 0.16);
  }
}
</style>
