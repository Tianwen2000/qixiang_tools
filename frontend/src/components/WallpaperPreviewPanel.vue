<script setup>
// 文件说明：定义 WallpaperPreviewPanel 前端组件。
import { computed, onBeforeUnmount, onMounted, ref } from "vue";

import { showToast } from "../utils/toast.js";
import { getWallpaperPreviewMode, onWallpaperPreviewModeChange, setWallpaperPreviewMode } from "../utils/wallpaper-preview.js";

const props = defineProps({
  embedded: {
    type: Boolean,
    default: false,
  },
});

const emit = defineEmits(["close"]);

const previewMode = ref(getWallpaperPreviewMode());
let removePreviewListener = () => {};

const currentModeLabel = computed(() => {
  const labelMap = {
    auto: "自动跟随节气",
    spring: "春分背景预览中",
    summer: "夏至背景预览中",
    autumn: "秋分背景预览中",
    winter: "冬至背景预览中",
  };
  return labelMap[previewMode.value] || labelMap.auto;
});

const previewOptions = [
  { key: "auto", label: "自动", description: "恢复按节气自动切换", image: "" },
  { key: "spring", label: "春分", description: "樱花嫩绿、清透芽影与春日气息", image: "/wallpaper/spring.jpg" },
  { key: "summer", label: "夏至", description: "蓝色水光、白花日影与清凉微风", image: "/wallpaper/summer.jpg" },
  { key: "autumn", label: "秋分", description: "金黄落叶、暖光小路与明亮秋色", image: "/wallpaper/autumn.jpg" },
  { key: "winter", label: "冬至", description: "雪白霜林、安静雪路与冬日微光", image: "/wallpaper/winter.jpg" },
];

function applyPreviewMode(mode) {
  const nextMode = setWallpaperPreviewMode(mode);
  previewMode.value = nextMode;
  showToast({
    type: "success",
    title: "预览已切换",
    message: nextMode === "auto" ? "背景已恢复自动节气模式。" : `当前正在预览${currentModeLabel.value.replace("预览中", "")}。`,
    duration: 1800,
  });
}

onMounted(() => {
  removePreviewListener = onWallpaperPreviewModeChange((mode) => {
    previewMode.value = mode;
  });
});

onBeforeUnmount(() => {
  removePreviewListener();
});
</script>

<template>
  <div class="mega-panel preview-mega-panel" :class="{ 'is-page-panel': embedded }">
    <div class="mega-panel-head preview-panel-head">
      <div>
        <p class="mega-panel-eyebrow">手动预览</p>
        <h2>四季背景预览</h2>
        <p>当前状态：{{ currentModeLabel }}。这里只影响当前浏览器标签页，方便你快速切换春夏秋冬效果。</p>
      </div>
      <button v-if="!props.embedded" type="button" class="mega-panel-action" @click="emit('close')">收起面板</button>
    </div>

    <section class="preview-panel-section">
      <div class="preview-section-head">
        <h3>四季背景</h3>
        <p>点击后全站背景会立即切换，不需要刷新页面。</p>
      </div>
      <div class="preview-option-grid">
        <button
          v-for="item in previewOptions"
          :key="item.key"
          type="button"
          class="preview-option-card"
          :class="{ active: previewMode === item.key }"
          @click="applyPreviewMode(item.key)"
        >
          <span
            class="preview-option-thumb"
            :class="{ 'preview-option-thumb-auto': !item.image }"
            :style="item.image ? { backgroundImage: `url(${item.image})` } : null"
            aria-hidden="true"
          ></span>
          <strong>{{ item.label }}</strong>
          <span class="preview-option-desc">{{ item.description }}</span>
        </button>
      </div>
    </section>
  </div>
</template>
