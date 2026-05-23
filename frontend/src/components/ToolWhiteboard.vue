<script setup>
import { onMounted, ref } from "vue";

import { showToast } from "../utils/toast.js";

const canvasRef = ref(null);
const color = ref("#1d4ed8");
const lineWidth = ref(4);
const erasing = ref(false);
let drawing = false;
let context = null;

function resizeCanvas() {
  const canvas = canvasRef.value;
  if (!canvas) {
    return;
  }
  const ratio = window.devicePixelRatio || 1;
  const width = canvas.parentElement?.clientWidth || 960;
  const height = 520;
  const snapshot = canvas.toDataURL("image/png");
  canvas.width = width * ratio;
  canvas.height = height * ratio;
  canvas.style.width = `${width}px`;
  canvas.style.height = `${height}px`;
  context = canvas.getContext("2d");
  context.scale(ratio, ratio);
  context.lineCap = "round";
  context.lineJoin = "round";
  context.fillStyle = "#ffffff";
  context.fillRect(0, 0, width, height);
  const image = new Image();
  image.onload = () => {
    context.drawImage(image, 0, 0, width, height);
  };
  image.src = snapshot;
}

function pointerPosition(event) {
  const rect = canvasRef.value.getBoundingClientRect();
  return {
    x: event.clientX - rect.left,
    y: event.clientY - rect.top,
  };
}

function startDraw(event) {
  if (!context) {
    return;
  }
  drawing = true;
  const { x, y } = pointerPosition(event);
  context.beginPath();
  context.moveTo(x, y);
}

function draw(event) {
  if (!drawing || !context) {
    return;
  }
  const { x, y } = pointerPosition(event);
  context.strokeStyle = erasing.value ? "#ffffff" : color.value;
  context.lineWidth = Number(lineWidth.value);
  context.lineTo(x, y);
  context.stroke();
}

function stopDraw() {
  drawing = false;
}

function clearBoard() {
  const canvas = canvasRef.value;
  if (!canvas || !context) {
    return;
  }
  context.clearRect(0, 0, canvas.clientWidth, canvas.clientHeight);
  context.fillStyle = "#ffffff";
  context.fillRect(0, 0, canvas.clientWidth, canvas.clientHeight);
  showToast({
    type: "info",
    title: "白板已清空",
    message: "可以重新开始绘制了。",
    duration: 1800,
  });
}

function downloadBoard() {
  const canvas = canvasRef.value;
  if (!canvas) {
    return;
  }
  const link = document.createElement("a");
  link.href = canvas.toDataURL("image/png");
  link.download = "whiteboard.png";
  link.click();
  showToast({
    type: "success",
    title: "已开始下载",
    message: "白板 PNG 已导出。",
    duration: 1800,
  });
}

onMounted(() => {
  const canvas = canvasRef.value;
  if (!canvas) {
    return;
  }
  resizeCanvas();
  window.addEventListener("resize", resizeCanvas);
});
</script>

<template>
  <section class="tool-form local-tool-panel whiteboard-panel">
    <div class="local-tool-header">
      <h3>在线白板</h3>
      <p>本地画板，不上传内容。支持画笔、橡皮和导出 PNG。</p>
    </div>

    <div class="whiteboard-toolbar">
      <label>
        <span>画笔颜色</span>
        <input v-model="color" type="color" />
      </label>
      <label>
        <span>粗细</span>
        <input v-model="lineWidth" type="range" min="1" max="24" />
      </label>
      <label class="whiteboard-toggle">
        <input v-model="erasing" type="checkbox" />
        <span>橡皮模式</span>
      </label>
      <button type="button" class="secondary-button" @click="clearBoard">清空白板</button>
      <button type="button" @click="downloadBoard">下载 PNG</button>
    </div>

    <div class="whiteboard-canvas-wrap">
      <canvas
        ref="canvasRef"
        class="whiteboard-canvas"
        @pointerdown="startDraw"
        @pointermove="draw"
        @pointerup="stopDraw"
        @pointerleave="stopDraw"
      ></canvas>
    </div>
  </section>
</template>
