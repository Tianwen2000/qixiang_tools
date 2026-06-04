<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from "vue";

import { WALLPAPER_EXCEPTION_STARS, WALLPAPER_SCENES } from "../data/wallpaper-scenes.js";
import { getWallpaperPreviewMode, onWallpaperPreviewModeChange } from "../utils/wallpaper-preview.js";
import { getMsUntilNextBeijingMidnight, getSeasonalWallpaperKey } from "../utils/wallpaper-theme.js";
import SeasonalForestScene from "./SeasonalForestScene.vue";

const MOBILE_QUERY = "(max-width: 767px)";

const props = defineProps({
  mode: {
    type: String,
    default: "seasonal",
  },
});

const liveSeason = ref(getSeasonalWallpaperKey());
const previewMode = ref(getWallpaperPreviewMode());
const prefersReducedMotion = ref(false);
const pointerTarget = ref({ x: 0.5, y: 0.34 });
const pointerState = ref({ x: 0.5, y: 0.34 });

// 首帧就确定是否手机：手机直接用静态季节图，不创建 video、不下载视频流量
const isMobile = ref(typeof window !== "undefined" && window.matchMedia(MOBILE_QUERY).matches);
// 桌面视频：加载失败 / 不支持时回退 CSS 动态背景
const videoEl = ref(null);
const videoFailed = ref(false);
const shouldLoadVideo = ref(false);
const videoReady = ref(false);

const season = computed(() => {
  if (props.mode !== "seasonal") {
    return liveSeason.value;
  }
  return previewMode.value === "auto" ? liveSeason.value : previewMode.value;
});

const activeScene = computed(() => WALLPAPER_SCENES[season.value] || WALLPAPER_SCENES.spring);

// 首屏统一先显示静态图；桌面视频等浏览器空闲后再加载，避免首屏抢带宽和解码资源。
const useStaticImage = computed(() => props.mode !== "exception");
const canUseVideo = computed(() => props.mode !== "exception" && !isMobile.value && !prefersReducedMotion.value && !videoFailed.value);
const useVideo = computed(() => canUseVideo.value && shouldLoadVideo.value);
const useCssScene = computed(() => props.mode !== "exception" && !useStaticImage.value && !useVideo.value);

const videoSrc = computed(() => `/wallpaper/${season.value}.mp4`);
const posterSrc = computed(() => `/wallpaper/${season.value}.jpg`);
const photoStyle = computed(() => ({ backgroundImage: `url("${posterSrc.value}")` }));

const wallpaperStyle = computed(() => {
  const shiftX = (pointerState.value.x - 0.5) * 24;
  const shiftY = (pointerState.value.y - 0.5) * 18;
  return {
    "--pointer-shift-x": `${shiftX.toFixed(2)}px`,
    "--pointer-shift-y": `${shiftY.toFixed(2)}px`,
    "--pointer-shift-x-soft": `${(shiftX * 0.38).toFixed(2)}px`,
    "--pointer-shift-y-soft": `${(shiftY * 0.28).toFixed(2)}px`,
    "--pointer-shift-x-strong": `${(shiftX * 0.64).toFixed(2)}px`,
    "--pointer-shift-y-strong": `${(shiftY * 0.5).toFixed(2)}px`,
  };
});

let refreshTimer = 0;
let removePreviewListener = () => {};
let removeMotionListener = () => {};
let removeMobileListener = () => {};
let rafId = 0;
let videoLoadTimer = 0;
let videoIdleId = 0;
let videoLoadWaitingForWindow = false;
let removeVideoLoadListener = () => {};

function refreshSeason() {
  liveSeason.value = getSeasonalWallpaperKey();
}

function scheduleRefresh() {
  window.clearTimeout(refreshTimer);
  refreshTimer = window.setTimeout(() => {
    refreshSeason();
    scheduleRefresh();
  }, getMsUntilNextBeijingMidnight());
}

function updateReducedMotionState(mediaQuery) {
  prefersReducedMotion.value = Boolean(mediaQuery.matches);
  if (prefersReducedMotion.value) {
    pointerState.value = { x: 0.5, y: 0.34 };
    pointerTarget.value = { x: 0.5, y: 0.34 };
  }
}

function animatePointer() {
  // 仅 CSS 动态背景（视频兜底）需要指针视差；手机/视频模式直接停掉 rAF
  if (prefersReducedMotion.value || !useCssScene.value) {
    rafId = 0;
    return;
  }
  pointerState.value = {
    x: pointerState.value.x + (pointerTarget.value.x - pointerState.value.x) * 0.08,
    y: pointerState.value.y + (pointerTarget.value.y - pointerState.value.y) * 0.08,
  };
  rafId = window.requestAnimationFrame(animatePointer);
}

function ensurePointerAnimation() {
  if (!rafId && !prefersReducedMotion.value && useCssScene.value) {
    rafId = window.requestAnimationFrame(animatePointer);
  }
}

function bindPointerInteraction() {
  if (typeof window === "undefined") {
    return () => {};
  }

  const handlePointerMove = (event) => {
    if (!useCssScene.value || prefersReducedMotion.value) {
      return;
    }
    const width = Math.max(1, window.innerWidth);
    const height = Math.max(1, window.innerHeight);
    pointerTarget.value = {
      x: event.clientX / width,
      y: event.clientY / height,
    };
    ensurePointerAnimation();
  };

  const handlePointerLeave = () => {
    if (!useCssScene.value || prefersReducedMotion.value) {
      return;
    }
    pointerTarget.value = { x: 0.5, y: 0.34 };
    ensurePointerAnimation();
  };

  window.addEventListener("pointermove", handlePointerMove, { passive: true });
  window.addEventListener("pointerleave", handlePointerLeave, { passive: true });
  return () => {
    window.removeEventListener("pointermove", handlePointerMove);
    window.removeEventListener("pointerleave", handlePointerLeave);
  };
}

function primeVideo() {
  const el = videoEl.value;
  if (!el) {
    return;
  }
  // 显式静音是移动端/桌面自动播放的前提，绕开 Vue 静态 muted 属性不生效的坑
  el.muted = true;
  const attempt = el.play();
  if (attempt && typeof attempt.catch === "function") {
    // 低电量模式 / 浏览器策略禁止自动播放时静默失败，由 poster 静态图兜底
    attempt.catch(() => {});
  }
}

function queueVideoLoad() {
  if (
    typeof window === "undefined" ||
    shouldLoadVideo.value ||
    videoLoadTimer ||
    videoIdleId ||
    videoLoadWaitingForWindow ||
    !canUseVideo.value
  ) {
    return;
  }

  const startLoading = () => {
    videoLoadTimer = 0;
    videoIdleId = 0;
    if (canUseVideo.value) {
      shouldLoadVideo.value = true;
      nextTick(primeVideo);
    }
  };

  const requestIdleStart = () => {
    videoLoadTimer = 0;
    if (!canUseVideo.value) {
      return;
    }
    if ("requestIdleCallback" in window) {
      videoIdleId = window.requestIdleCallback(startLoading, { timeout: 2200 });
      return;
    }
    startLoading();
  };

  const scheduleAfterLoad = () => {
    videoLoadWaitingForWindow = false;
    removeVideoLoadListener();
    videoLoadTimer = window.setTimeout(requestIdleStart, 900);
  };

  if (document.readyState === "complete") {
    scheduleAfterLoad();
    return;
  }

  videoLoadWaitingForWindow = true;
  window.addEventListener("load", scheduleAfterLoad, { once: true });
  removeVideoLoadListener = () => {
    window.removeEventListener("load", scheduleAfterLoad);
    removeVideoLoadListener = () => {};
  };
}

function cancelQueuedVideoLoad() {
  removeVideoLoadListener();
  videoLoadWaitingForWindow = false;
  if (videoLoadTimer) {
    window.clearTimeout(videoLoadTimer);
    videoLoadTimer = 0;
  }
  if (videoIdleId && "cancelIdleCallback" in window) {
    window.cancelIdleCallback(videoIdleId);
    videoIdleId = 0;
  }
}

function onVideoCanPlay() {
  videoReady.value = true;
  primeVideo();
}

function onVideoError() {
  // 视频缺失 / 格式不支持：保留静态季节图，不影响首屏可读性
  videoReady.value = false;
  videoFailed.value = true;
}

// 切到视频模式或换季节时，换源并重试播放
watch(videoSrc, () => {
  videoReady.value = false;
  videoFailed.value = false;
  shouldLoadVideo.value = false;
  cancelQueuedVideoLoad();
  queueVideoLoad();
});

watch(canUseVideo, (nextCanUseVideo) => {
  if (nextCanUseVideo) {
    queueVideoLoad();
    return;
  }
  cancelQueuedVideoLoad();
  shouldLoadVideo.value = false;
  videoReady.value = false;
});

watch([videoSrc, useVideo], async ([, nextUseVideo]) => {
  if (!nextUseVideo) {
    return;
  }
  await nextTick();
  const el = videoEl.value;
  if (el) {
    el.load();
    primeVideo();
  }
});

watch(
  [() => props.mode, previewMode],
  ([nextMode, nextPreviewMode]) => {
    if (nextMode === "seasonal" && nextPreviewMode === "auto") {
      refreshSeason();
      scheduleRefresh();
      return;
    }
    window.clearTimeout(refreshTimer);
  },
  { immediate: true },
);

onMounted(() => {
  const motionQuery = window.matchMedia("(prefers-reduced-motion: reduce)");
  const handleMotionChange = () => {
    updateReducedMotionState(motionQuery);
  };
  updateReducedMotionState(motionQuery);
  motionQuery.addEventListener("change", handleMotionChange);

  const mobileQuery = window.matchMedia(MOBILE_QUERY);
  const handleMobileChange = () => {
    isMobile.value = mobileQuery.matches;
  };
  isMobile.value = mobileQuery.matches;
  mobileQuery.addEventListener("change", handleMobileChange);

  removePreviewListener = onWallpaperPreviewModeChange((mode) => {
    previewMode.value = mode;
  });
  previewMode.value = getWallpaperPreviewMode();

  if (props.mode === "seasonal" && previewMode.value === "auto") {
    refreshSeason();
    scheduleRefresh();
  }

  const cleanupPointer = bindPointerInteraction();
  ensurePointerAnimation();
  queueVideoLoad();
  removeMotionListener = () => {
    motionQuery.removeEventListener("change", handleMotionChange);
    cleanupPointer();
  };
  removeMobileListener = () => {
    mobileQuery.removeEventListener("change", handleMobileChange);
  };
});

onBeforeUnmount(() => {
  window.clearTimeout(refreshTimer);
  cancelQueuedVideoLoad();
  window.cancelAnimationFrame(rafId);
  removePreviewListener();
  removeMotionListener();
  removeMobileListener();
});
</script>

<template>
  <div
    class="site-wallpaper"
    :class="[
      `mode-${mode}`,
      `season-${season}`,
      { 'is-reduced-motion': prefersReducedMotion, 'has-media': useVideo || useStaticImage },
    ]"
    :data-scene="season"
    :style="wallpaperStyle"
    aria-hidden="true"
  >
    <template v-if="mode === 'exception'">
      <div class="exception-base"></div>
      <div class="exception-noise"></div>
      <div class="exception-vignette"></div>
      <span
        v-for="star in WALLPAPER_EXCEPTION_STARS"
        :key="star.id"
        class="exception-star"
        :style="star"
      ></span>
    </template>

    <template v-else>
      <div class="wallpaper-base"></div>

      <!-- 静态季节图：桌面首屏兜底、手机常驻，避免视频首载卡顿 -->
      <div v-if="useStaticImage" class="wallpaper-photo" :style="photoStyle"></div>

      <!-- 桌面：空闲后加载视频，能播放后淡入 -->
      <video
        v-if="useVideo"
        ref="videoEl"
        class="wallpaper-video"
        :class="{ 'is-ready': videoReady }"
        autoplay
        muted
        loop
        playsinline
        preload="metadata"
        :poster="posterSrc"
        @canplay="onVideoCanPlay"
        @loadeddata="onVideoCanPlay"
        @error="onVideoError"
      >
        <source :src="videoSrc" type="video/mp4" />
      </video>

      <div class="wallpaper-reading-veil"></div>
      <div v-if="useVideo || useStaticImage" class="wallpaper-video-shade"></div>

      <!-- 仅当视频不可用且非手机时，回退渲染这套昂贵的 CSS 动态层 -->
      <template v-if="useCssScene">
        <div class="wallpaper-atmosphere">
          <span
            v-for="item in activeScene.orbs"
            :key="item.id"
            class="wallpaper-orb"
            :data-kind="item.kind"
            :style="item.style"
          ></span>

          <span
            v-for="item in activeScene.wisps"
            :key="item.id"
            class="wallpaper-wisp"
            :data-kind="item.kind"
            :style="item.style"
          ></span>

          <span
            v-for="item in activeScene.accents"
            :key="item.id"
            class="wallpaper-accent"
            :data-kind="item.kind"
            :style="item.style"
          ></span>
        </div>

        <SeasonalForestScene :season="season" />

        <div class="wallpaper-motion">
          <span
            v-for="item in activeScene.particles"
            :key="item.id"
            class="wallpaper-particle"
            :data-kind="item.kind"
            :style="item.style"
          ></span>
        </div>
      </template>

      <div class="wallpaper-noise"></div>
      <div class="wallpaper-vignette"></div>
    </template>
  </div>
</template>
