<script setup>
import { computed, onBeforeUnmount, ref } from "vue";

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
const mode = ref("cool");
const audioAvailable = ref(true);

const title = computed(() => props.tool.name || (isAc.value ? "赛博抽象小空调" : "赛博抽象小风扇"));
const statusText = computed(() => {
  if (!isOn.value) {
    return "待机";
  }
  if (isAc.value) {
    return mode.value === "cool" ? "制冷运行" : "制热运行";
  }
  return `${speed.value} 档`;
});
const fanSpinDuration = computed(() => `${Math.max(0.34, 1.42 - speed.value * 0.28)}s`);
const airflowOpacity = computed(() => (isOn.value ? 0.28 + speed.value * 0.16 : 0));

let audioContext = null;
let noiseBuffer = null;
let activeSources = [];
let activeNodes = [];

const fanSoundProfiles = {
  1: { rpm: 720, airGain: 0.11, airCutoff: 820, motorGain: 0.018 },
  2: { rpm: 980, airGain: 0.16, airCutoff: 1180, motorGain: 0.026 },
  3: { rpm: 1260, airGain: 0.22, airCutoff: 1650, motorGain: 0.036 },
};

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
  const profile = fanSoundProfiles[speed.value] || fanSoundProfiles[2];
  const bladePassFrequency = (profile.rpm * 3) / 60;
  const noise = context.createBufferSource();
  const airFilter = context.createBiquadFilter();
  const airGain = context.createGain();
  const bladeTone = context.createOscillator();
  const bladeToneGain = context.createGain();
  const bladeHarmonic = context.createOscillator();
  const bladeHarmonicGain = context.createGain();
  const airPulse = context.createOscillator();
  const airPulseDepth = context.createGain();

  noise.buffer = noiseBuffer;
  noise.loop = true;
  airFilter.type = "lowpass";
  airFilter.frequency.value = profile.airCutoff;
  airFilter.Q.value = 0.7;
  airGain.gain.value = profile.airGain;
  bladeTone.type = "triangle";
  bladeTone.frequency.value = bladePassFrequency;
  bladeToneGain.gain.value = profile.motorGain;
  bladeHarmonic.type = "sine";
  bladeHarmonic.frequency.value = bladePassFrequency * 2;
  bladeHarmonicGain.gain.value = profile.motorGain * 0.45;
  airPulse.type = "sine";
  airPulse.frequency.value = 0.65 + speed.value * 0.24;
  airPulseDepth.gain.value = profile.airGain * 0.18;

  noise.connect(airFilter);
  airFilter.connect(airGain);
  airGain.connect(master);
  bladeTone.connect(bladeToneGain);
  bladeToneGain.connect(master);
  bladeHarmonic.connect(bladeHarmonicGain);
  bladeHarmonicGain.connect(master);
  airPulse.connect(airPulseDepth);
  airPulseDepth.connect(airGain.gain);
  noise.start();
  bladeTone.start();
  bladeHarmonic.start();
  airPulse.start();
  activeSources.push(noise, bladeTone, bladeHarmonic, airPulse);
  activeNodes.push(noise, airFilter, airGain, bladeTone, bladeToneGain, bladeHarmonic, bladeHarmonicGain, airPulse, airPulseDepth, master);
}

function buildAcSound(context, master) {
  noiseBuffer ||= createNoiseBuffer(context);
  const airNoise = context.createBufferSource();
  const airHighpass = context.createBiquadFilter();
  const airLowpass = context.createBiquadFilter();
  const airGain = context.createGain();
  const hissNoise = context.createBufferSource();
  const hissFilter = context.createBiquadFilter();
  const hissGain = context.createGain();
  const compressorHum = context.createOscillator();
  const compressorHumGain = context.createGain();
  const compressorOvertone = context.createOscillator();
  const compressorOvertoneGain = context.createGain();
  const compressorPulse = context.createOscillator();
  const compressorPulseDepth = context.createGain();

  const cooling = mode.value === "cool";
  airNoise.buffer = noiseBuffer;
  airNoise.loop = true;
  airHighpass.type = "highpass";
  airHighpass.frequency.value = cooling ? 130 : 110;
  airLowpass.type = "lowpass";
  airLowpass.frequency.value = cooling ? 1280 : 940;
  airLowpass.Q.value = 0.62;
  airGain.gain.value = cooling ? 0.14 : 0.11;

  hissNoise.buffer = noiseBuffer;
  hissNoise.loop = true;
  hissFilter.type = "bandpass";
  hissFilter.frequency.value = cooling ? 2400 : 1700;
  hissFilter.Q.value = 0.7;
  hissGain.gain.value = cooling ? 0.022 : 0.012;

  compressorHum.type = "sine";
  compressorHum.frequency.value = cooling ? 54 : 46;
  compressorHumGain.gain.value = cooling ? 0.034 : 0.026;
  compressorOvertone.type = "triangle";
  compressorOvertone.frequency.value = cooling ? 108 : 92;
  compressorOvertoneGain.gain.value = cooling ? 0.012 : 0.009;
  compressorPulse.type = "sine";
  compressorPulse.frequency.value = 0.36;
  compressorPulseDepth.gain.value = cooling ? 0.01 : 0.007;

  airNoise.connect(airHighpass);
  airHighpass.connect(airLowpass);
  airLowpass.connect(airGain);
  airGain.connect(master);
  hissNoise.connect(hissFilter);
  hissFilter.connect(hissGain);
  hissGain.connect(master);
  compressorHum.connect(compressorHumGain);
  compressorHumGain.connect(master);
  compressorOvertone.connect(compressorOvertoneGain);
  compressorOvertoneGain.connect(master);
  compressorPulse.connect(compressorPulseDepth);
  compressorPulseDepth.connect(compressorHumGain.gain);
  airNoise.start();
  hissNoise.start();
  compressorHum.start();
  compressorOvertone.start();
  compressorPulse.start();
  activeSources.push(airNoise, hissNoise, compressorHum, compressorOvertone, compressorPulse);
  activeNodes.push(
    airNoise,
    airHighpass,
    airLowpass,
    airGain,
    hissNoise,
    hissFilter,
    hissGain,
    compressorHum,
    compressorHumGain,
    compressorOvertone,
    compressorOvertoneGain,
    compressorPulse,
    compressorPulseDepth,
    master,
  );
}

function playTone(context, { frequency, endFrequency = frequency, startTime, duration, type = "sine", gainValue }) {
  const oscillator = context.createOscillator();
  const gain = context.createGain();
  oscillator.type = type;
  oscillator.frequency.setValueAtTime(frequency, startTime);
  if (endFrequency !== frequency) {
    oscillator.frequency.exponentialRampToValueAtTime(endFrequency, startTime + duration * 0.82);
  }
  gain.gain.setValueAtTime(0.0001, startTime);
  gain.gain.exponentialRampToValueAtTime(gainValue, startTime + 0.012);
  gain.gain.setTargetAtTime(gainValue * 0.84, startTime + duration * 0.45, 0.03);
  gain.gain.exponentialRampToValueAtTime(0.0001, startTime + duration);
  oscillator.connect(gain);
  gain.connect(context.destination);
  oscillator.start(startTime);
  oscillator.stop(startTime + duration + 0.02);
}

function playButtonClick(context, startTime, gainValue) {
  const click = context.createBufferSource();
  const filter = context.createBiquadFilter();
  const gain = context.createGain();
  const buffer = context.createBuffer(1, Math.floor(context.sampleRate * 0.018), context.sampleRate);
  const channel = buffer.getChannelData(0);
  for (let index = 0; index < channel.length; index += 1) {
    channel[index] = (Math.random() * 2 - 1) * (1 - index / channel.length);
  }
  click.buffer = buffer;
  filter.type = "highpass";
  filter.frequency.value = 1700;
  gain.gain.setValueAtTime(gainValue, startTime);
  gain.gain.exponentialRampToValueAtTime(0.0001, startTime + 0.018);
  click.connect(filter);
  filter.connect(gain);
  gain.connect(context.destination);
  click.start(startTime);
}

async function playControlTone(kind) {
  const context = getAudioContext();
  if (!context) {
    audioAvailable.value = false;
    return;
  }
  try {
    await context.resume();
    audioAvailable.value = true;
  } catch {
    audioAvailable.value = false;
    return;
  }

  const now = context.currentTime;
  const gainValue = isAc.value ? 0.09 : Math.min(0.13, 0.045 + speed.value * 0.026);
  playButtonClick(context, now, gainValue * 0.12);
  if (kind === "power") {
    const beepFrequency = isAc.value ? 1780 : 1680;
    playTone(context, {
      frequency: beepFrequency,
      endFrequency: beepFrequency * 1.035,
      startTime: now + 0.012,
      duration: 0.12,
      type: "sine",
      gainValue,
    });
    playTone(context, {
      frequency: beepFrequency * 2.01,
      endFrequency: beepFrequency * 2.04,
      startTime: now + 0.018,
      duration: 0.065,
      type: "sine",
      gainValue: gainValue * 0.18,
    });
    return;
  }
  if (kind === "cool") {
    playTone(context, { frequency: 1120, endFrequency: 1180, startTime: now + 0.012, duration: 0.16, type: "sine", gainValue });
    playTone(context, { frequency: 1520, endFrequency: 1450, startTime: now + 0.17, duration: 0.08, type: "triangle", gainValue: gainValue * 0.46 });
    return;
  }
  if (kind === "heat") {
    playTone(context, { frequency: 760, endFrequency: 720, startTime: now + 0.012, duration: 0.18, type: "sine", gainValue: gainValue * 0.9 });
    playTone(context, { frequency: 980, endFrequency: 1040, startTime: now + 0.18, duration: 0.09, type: "triangle", gainValue: gainValue * 0.42 });
    return;
  }
  if (kind.startsWith("speed-")) {
    const targetSpeed = Number(kind.slice(6)) || speed.value;
    const toneGain = Math.min(0.13, 0.05 + targetSpeed * 0.025);
    playTone(context, {
      frequency: 880 + targetSpeed * 130,
      endFrequency: 920 + targetSpeed * 140,
      startTime: now + 0.012,
      duration: 0.13,
      type: "sine",
      gainValue: toneGain,
    });
    return;
  }
}

function rebuildAudioGraph() {
  stopGraph();
  if (!isOn.value || !audioContext) {
    return;
  }
  const master = audioContext.createGain();
  master.gain.value = isAc.value ? 0.34 : Math.min(0.46, 0.16 + speed.value * 0.1);
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
  await playControlTone("power");
  isOn.value = !isOn.value;
  if (isOn.value) {
    await activateAudio();
  } else {
    stopGraph();
  }
}

async function setSpeed(nextSpeed) {
  speed.value = nextSpeed;
  await playControlTone(`speed-${nextSpeed}`);
  if (isOn.value) {
    await activateAudio();
  }
}

async function setAcMode(nextMode) {
  await playControlTone(nextMode);
  mode.value = nextMode;
  if (!isOn.value) {
    isOn.value = true;
  }
  await activateAudio();
}

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
        </div>
        <span class="appliance-state" :class="{ active: isOn }">{{ statusText }}</span>
      </div>
    </div>

    <div class="appliance-stage">
      <div v-if="!isAc" class="fan-machine">
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
          <div class="ac-energy-label" aria-label="能耗简要图">
            <div class="energy-head">
              <span></span>
              <span></span>
              <span></span>
              <span></span>
            </div>
            <div class="energy-bars">
              <span class="green wide"></span>
              <span class="green"></span>
              <span class="yellow mid"></span>
              <span class="orange wide"></span>
              <span class="red"></span>
            </div>
            <div class="energy-lines">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
          <div class="ac-display">{{ isOn ? (mode === "cool" ? "❄" : "♨") : "--" }}</div>
          <div class="ac-light" :class="{ active: isOn }"></div>
          <div class="ac-vent" :class="{ swinging: isOn }">
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

    <div v-if="!isAc" class="appliance-controls fan-controls">
      <button type="button" class="power-button" :class="{ active: isOn }" @click="togglePower">关</button>

      <div class="appliance-control-group">
        <div class="segmented-buttons">
          <button v-for="item in [1, 2, 3]" :key="item" type="button" :class="{ active: speed === item }" @click="setSpeed(item)">
            {{ item }}
          </button>
        </div>
      </div>
    </div>

    <div v-else class="appliance-controls ac-controls" aria-label="空调控制">
      <button type="button" class="icon-button cool-button" :class="{ active: isOn && mode === 'cool' }" aria-label="制冷" title="制冷" @click="setAcMode('cool')">
        <svg viewBox="0 0 24 24" aria-hidden="true">
          <path d="M12 3v18M5 6.5l14 11M19 6.5l-14 11" />
          <path d="M8 4.8 12 7l4-2.2M8 19.2 12 17l4 2.2M4.5 10.2 8.4 12l-3.9 1.8M19.5 10.2 15.6 12l3.9 1.8" />
        </svg>
      </button>
      <button type="button" class="icon-button heat-button" :class="{ active: isOn && mode === 'heat' }" aria-label="制热" title="制热" @click="setAcMode('heat')">
        <svg viewBox="0 0 24 24" aria-hidden="true">
          <path d="M7 20c3-1.5 3.2-4.2 1.5-6.4C6.9 11.5 7.3 8.8 10 6c-.4 2.7 1.1 4.2 2.9 5.8 2.1 1.9 2.7 5.2-.9 8.2" />
          <path d="M15.6 19.2c2.2-1.2 2.9-3.5 1.7-5.5-.7-1.2-.4-2.8 1-4.3.1 2 .9 3.1 2 4.5 1.2 1.6.7 4-1.4 5.3" />
        </svg>
      </button>
      <button type="button" class="icon-button power-button" :class="{ active: isOn }" aria-label="开关" title="开关" @click="togglePower">
        <svg viewBox="0 0 24 24" aria-hidden="true">
          <path d="M12 3v9" />
          <path d="M7.2 6.8a7 7 0 1 0 9.6 0" />
        </svg>
      </button>
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

.abstract-appliance-tool.ac .appliance-stage {
  min-height: 320px;
}

.fan-machine {
  position: relative;
  display: grid;
  justify-items: center;
  max-width: 100%;
  transform-origin: 50% 68%;
}

.fan-cage {
  position: relative;
  width: min(310px, 68vw);
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
  /* 把昂贵的网罩渐变栅格化成独立合成层，旋转时减少重绘 */
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
  height: 96px;
  margin-top: -4px;
  border-radius: 20px;
  background: linear-gradient(90deg, #9cb4c9, #edf4fa 48%, #8fa9c0);
}

.fan-base {
  width: 190px;
  height: 48px;
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
  width: min(620px, 100%);
  max-width: 100%;
  display: grid;
  justify-items: center;
  gap: 16px;
}

.ac-body {
  position: relative;
  width: min(560px, 92vw);
  min-width: 0;
  min-height: 172px;
  border-radius: 8px;
  border: 1px solid rgba(187, 202, 216, 0.92);
  background: linear-gradient(180deg, #ffffff, #e9f1f7);
  box-shadow: 0 26px 58px rgba(52, 77, 101, 0.18), inset 0 -14px 28px rgba(131, 154, 177, 0.12);
}

.ac-energy-label {
  position: absolute;
  top: 18px;
  left: 24px;
  width: 82px;
  height: 104px;
  border-radius: 4px;
  background: #ffffff;
  border: 3px solid #66b6f3;
  box-shadow: inset 0 0 0 1px rgba(27, 96, 160, 0.12);
  padding: 7px 7px 6px;
}

.energy-head {
  display: flex;
  gap: 4px;
  margin-bottom: 7px;
}

.energy-head span {
  width: 7px;
  height: 5px;
  border-radius: 999px;
  background: #42a7ec;
}

.energy-bars {
  display: grid;
  gap: 4px;
  margin-bottom: 9px;
}

.energy-bars span {
  height: 4px;
  border-radius: 999px;
}

.energy-bars .green {
  width: 34px;
  background: #2ec86b;
}

.energy-bars .yellow {
  width: 42px;
  background: #f4c430;
}

.energy-bars .orange {
  width: 50px;
  background: #ff8a2a;
}

.energy-bars .red {
  width: 60px;
  background: #f04438;
}

.energy-bars .mid {
  width: 46px;
}

.energy-bars .wide {
  width: 55px;
}

.energy-lines {
  display: grid;
  gap: 3px;
}

.energy-lines span {
  height: 2px;
  background: repeating-linear-gradient(90deg, #3b4b5f 0 3px, transparent 3px 6px);
}

.ac-display {
  position: absolute;
  top: 28px;
  right: 34px;
  min-width: 76px;
  border-radius: 999px;
  padding: 9px 13px;
  background: #26384d;
  color: #eef9ff;
  text-align: center;
  font-weight: 800;
  letter-spacing: 0;
  font-size: 20px;
}

.ac-light {
  position: absolute;
  top: 44px;
  right: 126px;
  width: 14px;
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
  left: 132px;
  right: 36px;
  bottom: 30px;
  display: grid;
  gap: 8px;
  transform-origin: 50% 0;
}

.ac-vent.swinging {
  animation: vent-swing 2s ease-in-out infinite;
  will-change: transform;
}

.ac-vent span {
  height: 6px;
  border-radius: 999px;
  background: linear-gradient(90deg, #aabccc, #f8fbfd, #aabccc);
}

.ac-airflow {
  top: 176px;
  display: grid;
  justify-items: center;
  gap: 18px;
}

.ac-airflow span {
  width: min(420px, 72vw);
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

.fan-controls {
  justify-content: center;
}

.ac-controls {
  justify-content: center;
}

.appliance-controls button {
  min-width: 72px;
  border: 1px solid #dbe3eb;
  border-radius: 14px;
  padding: 11px 13px;
  background: #fff;
  color: var(--ink);
  cursor: pointer;
}

.ac-controls .icon-button {
  display: inline-grid;
  place-items: center;
  width: 64px;
  min-width: 64px;
  aspect-ratio: 1;
  border-radius: 50%;
  padding: 0;
}

.ac-controls .icon-button svg {
  width: 30px;
  height: 30px;
  stroke: currentColor;
  stroke-width: 2;
  stroke-linecap: round;
  stroke-linejoin: round;
  fill: none;
}

.ac-controls .cool-button {
  color: #1687d9;
  background: #eef8ff;
}

.ac-controls .heat-button {
  color: #dc5a1f;
  background: #fff3ec;
}

.ac-controls .power-button {
  color: #324154;
}

.appliance-controls button.active,
.segmented-buttons button.active,
.power-button.active {
  border-color: transparent;
  background: linear-gradient(135deg, var(--accent) 0%, var(--accent-strong) 100%);
  color: #fff;
}

.appliance-control-group {
  display: grid;
  gap: 8px;
  min-width: 120px;
  max-width: 100%;
}

.appliance-control-group > span {
  color: var(--muted);
  font-size: 13px;
}

.segmented-buttons {
  display: flex;
  gap: 8px;
  align-items: center;
}

@keyframes fan-spin {
  to {
    transform: rotate(360deg);
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

  .appliance-controls button {
    min-width: 0;
  }

  .appliance-control-group {
    width: 100%;
  }

  .segmented-buttons {
    min-width: 0;
  }

  .segmented-buttons button {
    flex: 1 1 0;
  }

  .abstract-appliance-tool.ac .appliance-stage {
    min-height: 300px;
  }

  .ac-controls {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }

  .ac-body {
    width: min(460px, 92vw);
    min-height: 160px;
  }

  .ac-energy-label {
    top: 16px;
    left: 18px;
    transform: scale(0.86);
    transform-origin: top left;
  }

  .ac-display {
    top: 24px;
    right: 24px;
  }

  .ac-light {
    top: 40px;
    right: 108px;
  }

  .ac-vent {
    left: 112px;
    right: 24px;
  }

  .ac-airflow {
    top: 164px;
  }

  /* 移动端降低大模糊阴影的填充开销，减轻旋转时的卡顿 */
  .fan-cage {
    box-shadow: inset 0 0 0 8px rgba(255, 255, 255, 0.7), 0 14px 26px rgba(75, 95, 120, 0.16);
  }

  .ac-body {
    box-shadow: 0 14px 30px rgba(75, 95, 120, 0.16);
  }
}
</style>
