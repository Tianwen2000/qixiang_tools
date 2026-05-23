<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from "vue";

import { WALLPAPER_EXCEPTION_STARS, WALLPAPER_SCENES } from "../data/wallpaper-scenes.js";
import { getWallpaperPreviewMode, onWallpaperPreviewModeChange } from "../utils/wallpaper-preview.js";
import { getMsUntilNextBeijingMidnight, getSeasonalWallpaperKey } from "../utils/wallpaper-theme.js";
import SeasonalForestScene from "./SeasonalForestScene.vue";

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

const season = computed(() => {
  if (props.mode !== "seasonal") {
    return liveSeason.value;
  }
  return previewMode.value === "auto" ? liveSeason.value : previewMode.value;
});

const activeScene = computed(() => WALLPAPER_SCENES[season.value] || WALLPAPER_SCENES.spring);
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
let rafId = 0;

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
  if (prefersReducedMotion.value) {
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
  if (!rafId && !prefersReducedMotion.value) {
    rafId = window.requestAnimationFrame(animatePointer);
  }
}

function bindPointerInteraction() {
  if (typeof window === "undefined") {
    return () => {};
  }

  const handlePointerMove = (event) => {
    const width = Math.max(1, window.innerWidth);
    const height = Math.max(1, window.innerHeight);
    pointerTarget.value = {
      x: event.clientX / width,
      y: event.clientY / height,
    };
    ensurePointerAnimation();
  };

  const handlePointerLeave = () => {
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
  const mediaQuery = window.matchMedia("(prefers-reduced-motion: reduce)");
  const handleMotionChange = () => {
    updateReducedMotionState(mediaQuery);
  };

  updateReducedMotionState(mediaQuery);
  mediaQuery.addEventListener("change", handleMotionChange);

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
  removeMotionListener = () => {
    mediaQuery.removeEventListener("change", handleMotionChange);
    cleanupPointer();
  };
});

onBeforeUnmount(() => {
  window.clearTimeout(refreshTimer);
  window.cancelAnimationFrame(rafId);
  removePreviewListener();
  removeMotionListener();
});
</script>

<template>
  <div
    class="site-wallpaper"
    :class="[
      `mode-${mode}`,
      `season-${season}`,
      { 'is-reduced-motion': prefersReducedMotion },
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
      <div class="wallpaper-reading-veil"></div>
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

      <div class="wallpaper-noise"></div>
      <div class="wallpaper-vignette"></div>
    </template>
  </div>
</template>
