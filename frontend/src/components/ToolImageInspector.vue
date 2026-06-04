<script setup>
import { onBeforeUnmount, ref } from "vue";

import { showToast } from "../utils/toast.js";

const detail = ref(null);
const previewUrl = ref("");
const loading = ref(false);
const dragging = ref(false);
const fileInput = ref(null);

// 常见宽高比（横向 + 竖向）。精确命中则显示标准比，否则显示「最近似 x:x」
const COMMON_RATIOS = [
  { label: "1:1", v: 1 },
  { label: "5:4", v: 5 / 4 },
  { label: "4:5", v: 4 / 5 },
  { label: "4:3", v: 4 / 3 },
  { label: "3:4", v: 3 / 4 },
  { label: "3:2", v: 3 / 2 },
  { label: "2:3", v: 2 / 3 },
  { label: "16:10", v: 16 / 10 },
  { label: "10:16", v: 10 / 16 },
  { label: "16:9", v: 16 / 9 },
  { label: "9:16", v: 9 / 16 },
  { label: "5:3", v: 5 / 3 },
  { label: "3:5", v: 3 / 5 },
  { label: "2:1", v: 2 },
  { label: "1:2", v: 0.5 },
  { label: "21:9", v: 21 / 9 },
  { label: "9:21", v: 9 / 21 },
];

const TRANSPARENT_FORMATS = new Set(["PNG", "GIF", "WebP", "AVIF", "HEIC/HEIF", "ICO", "SVG", "TIFF"]);

function gcd(a, b) {
  let x = a;
  let y = b;
  while (y) {
    [x, y] = [y, x % y];
  }
  return x || 1;
}

function aspectInfo(width, height) {
  if (!width || !height) {
    return { text: "--", exact: "--", standard: false };
  }
  const g = gcd(width, height);
  const exact = `${width / g}:${height / g}`;
  const ratio = width / height;
  if (COMMON_RATIOS.some((item) => item.label === exact)) {
    return { text: exact, exact, standard: true };
  }
  let nearest = COMMON_RATIOS[0];
  let bestDiff = Infinity;
  for (const item of COMMON_RATIOS) {
    const diff = Math.abs(item.v - ratio);
    if (diff < bestDiff) {
      bestDiff = diff;
      nearest = item;
    }
  }
  return { text: `最近似 ${nearest.label}`, exact, standard: false };
}

function formatBytes(bytes) {
  if (!Number.isFinite(bytes)) {
    return "--";
  }
  if (bytes >= 1024 * 1024) {
    return `${(bytes / 1024 / 1024).toFixed(2)} MB`;
  }
  if (bytes >= 1024) {
    return `${(bytes / 1024).toFixed(2)} KB`;
  }
  return `${bytes} 字节`;
}

function formatPixels(width, height) {
  const total = width * height;
  if (total >= 1e6) {
    return `${(total / 1e6).toFixed(2)} MP（${total.toLocaleString()} 像素）`;
  }
  return `${total.toLocaleString()} 像素`;
}

// 读前 32 字节，按文件头魔数识别真实格式（比后缀可靠）
async function detectFormat(file) {
  const buffer = new Uint8Array(await file.slice(0, 32).arrayBuffer());
  const ascii = (start, len) => String.fromCharCode(...buffer.slice(start, start + len));
  const b = (index) => buffer[index];

  if (b(0) === 0xff && b(1) === 0xd8 && b(2) === 0xff) return "JPEG";
  if (b(0) === 0x89 && ascii(1, 3) === "PNG") return "PNG";
  if (ascii(0, 3) === "GIF") return "GIF";
  if (ascii(0, 4) === "RIFF" && ascii(8, 4) === "WEBP") return "WebP";
  if (b(0) === 0x42 && b(1) === 0x4d) return "BMP";
  if (ascii(4, 4) === "ftyp") {
    const brand = ascii(8, 4).toLowerCase();
    if (brand.includes("avif")) return "AVIF";
    if (brand.includes("heic") || brand.includes("heif") || brand.includes("mif1")) return "HEIC/HEIF";
    return "ISO-BMFF";
  }
  if ((b(0) === 0x49 && b(1) === 0x49 && b(2) === 0x2a) || (b(0) === 0x4d && b(1) === 0x4d && b(2) === 0x00)) return "TIFF";
  if (b(0) === 0x00 && b(1) === 0x00 && b(2) === 0x01 && b(3) === 0x00) return "ICO";
  const head = ascii(0, 6).toLowerCase();
  if (head.includes("<svg") || head.includes("<?xml")) return "SVG";
  return "";
}

function readSizeByImage(file) {
  return new Promise((resolve, reject) => {
    const url = URL.createObjectURL(file);
    const img = new Image();
    img.onload = () => {
      resolve({ width: img.naturalWidth, height: img.naturalHeight });
      URL.revokeObjectURL(url);
    };
    img.onerror = () => {
      URL.revokeObjectURL(url);
      reject(new Error("decode failed"));
    };
    img.src = url;
  });
}

async function inspect(file) {
  if (!file || loading.value) {
    return;
  }
  loading.value = true;
  detail.value = null;
  if (previewUrl.value) {
    URL.revokeObjectURL(previewUrl.value);
    previewUrl.value = "";
  }

  try {
    const format = await detectFormat(file);
    const mime = file.type || "未知";
    const looksImage = mime.startsWith("image/") || Boolean(format);

    let width = 0;
    let height = 0;
    let note = "";
    if (looksImage) {
      try {
        if (typeof window.createImageBitmap === "function") {
          // createImageBitmap 在浏览器内部线程解码，几乎不阻塞主线程
          const bitmap = await createImageBitmap(file);
          width = bitmap.width;
          height = bitmap.height;
          bitmap.close?.();
        } else {
          ({ width, height } = await readSizeByImage(file));
        }
      } catch {
        try {
          ({ width, height } = await readSizeByImage(file));
        } catch {
          note = "（无法解码尺寸）";
        }
      }
    }

    previewUrl.value = URL.createObjectURL(file);
    const fmt = format || (mime.startsWith("image/") ? mime.split("/")[1].toUpperCase() : "未知");

    detail.value = {
      name: file.name || "未知",
      size: formatBytes(file.size),
      sizeBytes: `${file.size.toLocaleString()} 字节`,
      format: fmt,
      mime,
      dimension: width && height ? `${width} × ${height} px ${note}`.trim() : "无法读取",
      aspect: width && height ? aspectInfo(width, height) : null,
      pixels: width && height ? formatPixels(width, height) : "--",
      transparent: TRANSPARENT_FORMATS.has(fmt) ? "格式支持（可能含透明）" : "不支持",
      modified: file.lastModified ? new Date(file.lastModified).toLocaleString() : "--",
      looksImage,
    };

    if (!looksImage) {
      showToast({
        type: "info",
        title: "可能不是图片",
        message: "该文件看起来不是图片，部分信息可能读不到。",
        duration: 2600,
      });
    }
  } catch (err) {
    showToast({
      type: "error",
      title: "读取失败",
      message: err?.message || "无法读取该文件",
      duration: 3000,
    });
  } finally {
    loading.value = false;
  }
}

function onPick(event) {
  const file = event.target.files?.[0];
  if (file) {
    inspect(file);
  }
}

function onDrop(event) {
  dragging.value = false;
  const file = event.dataTransfer?.files?.[0];
  if (file) {
    inspect(file);
  }
}

function clearAll() {
  detail.value = null;
  if (previewUrl.value) {
    URL.revokeObjectURL(previewUrl.value);
    previewUrl.value = "";
  }
  if (fileInput.value) {
    fileInput.value.value = "";
  }
}

onBeforeUnmount(() => {
  if (previewUrl.value) {
    URL.revokeObjectURL(previewUrl.value);
  }
});
</script>

<template>
  <section class="tool-form local-tool-panel image-inspector-tool">
    <div class="local-tool-header">
      <div class="local-tool-header-bar">
        <div>
          <h3>图片详情查看</h3>
          <p>在浏览器本地读取图片的体积、尺寸、宽高比、格式等信息，全程不上传、不依赖后端。</p>
        </div>
        <div v-if="detail" class="result-actions">
          <button type="button" class="secondary-button" @click="fileInput?.click()">换一张</button>
          <button type="button" class="secondary-button" @click="clearAll">清空</button>
        </div>
      </div>
    </div>

    <label
      class="image-drop"
      :class="{ dragging }"
      @dragover.prevent="dragging = true"
      @dragleave.prevent="dragging = false"
      @drop.prevent="onDrop"
    >
      <input ref="fileInput" type="file" accept="image/*" hidden @change="onPick" />
      <span>{{ loading ? "读取中…" : detail ? "点击或拖入图片可换一张（不会上传）" : "点击选择，或把图片拖到这里（不会上传）" }}</span>
    </label>

    <template v-if="detail">
      <div class="image-inspector-body">
        <div class="image-preview">
          <img :src="previewUrl" alt="图片预览" />
        </div>
        <div class="insight-grid">
          <article class="insight-card">
            <span class="insight-label">文件名</span>
            <strong class="insight-value">{{ detail.name }}</strong>
          </article>
          <article class="insight-card">
            <span class="insight-label">文件体积</span>
            <strong class="insight-value">{{ detail.size }}</strong>
          </article>
          <article class="insight-card">
            <span class="insight-label">图片格式</span>
            <strong class="insight-value">{{ detail.format }}</strong>
          </article>
          <article class="insight-card">
            <span class="insight-label">MIME 类型</span>
            <strong class="insight-value">{{ detail.mime }}</strong>
          </article>
          <article class="insight-card">
            <span class="insight-label">尺寸</span>
            <strong class="insight-value">{{ detail.dimension }}</strong>
          </article>
          <article class="insight-card">
            <span class="insight-label">宽高比</span>
            <strong class="insight-value">
              {{ detail.aspect ? detail.aspect.text : "--" }}
              <small v-if="detail.aspect && !detail.aspect.standard">（精确 {{ detail.aspect.exact }}）</small>
            </strong>
          </article>
          <article class="insight-card">
            <span class="insight-label">像素总量</span>
            <strong class="insight-value">{{ detail.pixels }}</strong>
          </article>
          <article class="insight-card">
            <span class="insight-label">透明通道</span>
            <strong class="insight-value">{{ detail.transparent }}</strong>
          </article>
          <article class="insight-card">
            <span class="insight-label">字节数</span>
            <strong class="insight-value">{{ detail.sizeBytes }}</strong>
          </article>
          <article class="insight-card">
            <span class="insight-label">最后修改</span>
            <strong class="insight-value">{{ detail.modified }}</strong>
          </article>
        </div>
      </div>
      <p class="image-inspector-note">
        提示：图片的“编码”就是它的格式（JPEG / PNG / WebP / GIF / AVIF 等，已按真实文件头识别）；H.264 / H.265 是视频编码，图片不涉及。
      </p>
    </template>
  </section>
</template>

<style scoped>
.image-inspector-tool {
  gap: 14px;
}

.image-drop {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 92px;
  padding: 18px;
  border: 1.5px dashed rgba(150, 180, 210, 0.7);
  border-radius: 14px;
  cursor: pointer;
  text-align: center;
  color: var(--muted);
  background: rgba(255, 255, 255, 0.5);
  transition: border-color 0.18s ease, background 0.18s ease;
}

.image-drop.dragging {
  border-color: var(--accent-strong);
  background: rgba(220, 248, 240, 0.6);
}

.image-inspector-body {
  display: grid;
  grid-template-columns: minmax(0, 220px) minmax(0, 1fr);
  gap: 16px;
  align-items: start;
}

.image-preview {
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid rgba(200, 216, 232, 0.7);
  background: repeating-conic-gradient(#eef2f6 0 25%, #ffffff 0 50%) 0 / 16px 16px;
}

.image-preview img {
  display: block;
  width: 100%;
  height: auto;
  max-height: 240px;
  object-fit: contain;
}

.insight-value small {
  color: var(--muted);
  font-weight: 400;
  font-size: 12px;
}

.image-inspector-note {
  margin: 0;
  color: var(--muted);
  font-size: 13px;
  line-height: 1.6;
}

@media (max-width: 768px) {
  .image-inspector-body {
    grid-template-columns: 1fr;
  }
}
</style>
