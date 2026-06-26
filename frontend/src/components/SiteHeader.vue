<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";

import { getBackofficeChallenge, requestBackofficeEntry } from "../api/backoffice.js";
import { fallbackCategories } from "../data/fallback-meta.js";
import { useFavoriteTools } from "../utils/favorite-tools.js";
import { getWallpaperPreviewMode, onWallpaperPreviewModeChange } from "../utils/wallpaper-preview.js";
import { showToast } from "../utils/toast.js";
import HeaderQXMarquee from "./HeaderQXMarquee.vue";

const props = defineProps({
  categories: {
    type: Array,
    default: () => [],
  },
  activeCategory: {
    type: String,
    default: "",
  },
  keyword: {
    type: String,
    default: "",
  },
  homeMode: {
    type: Boolean,
    default: false,
  },
});

const emit = defineEmits(["update:keyword", "select-category"]);

const route = useRoute();
const router = useRouter();
const searchInput = ref(null);
const searchModalOpen = ref(false);
const backofficeAnswerInput = ref(null);
const backofficeModalOpen = ref(false);
const backofficeQuestion = ref("");
const backofficeAnswer = ref("");
const backofficeLoading = ref(false);
const backofficeAnswerVisible = ref(false);
const previewMode = ref(getWallpaperPreviewMode());
const localKeyword = ref(props.keyword || "");
const { favoriteCount } = useFavoriteTools();

let removePreviewListener = () => {};
const BACKOFFICE_CLICK_LIMIT = 5;
const BACKOFFICE_CLICK_WINDOW_MS = 3000;
const BACKOFFICE_GATE_KEY = "qx_backoffice_gate";
const BACKOFFICE_GATE_TTL_MS = 2 * 60 * 1000;

const INVISIBLE_CONTROL_RE =
  /[\u0000-\u001f\u007f-\u009f\u00ad\u034f\u061c\u115f\u1160\u17b4\u17b5\u180e\u200b-\u200f\u2028-\u202f\u205f\u2060-\u206f\u3000\u3164\ufe00-\ufe0f\ufeff\uffa0]/g;

const resolvedCategories = computed(() => (props.categories.length ? props.categories : fallbackCategories));
const previewActive = computed(() => route.name === "preview" || previewMode.value !== "auto");
const searchActive = computed(() => (props.keyword || "").trim().length > 0);
const favoriteActive = computed(() => route.name === "favorites" || favoriteCount.value > 0);

watch(
  () => props.keyword,
  (value) => {
    localKeyword.value = value || "";
  },
);

async function openSearchModal() {
  localKeyword.value = props.keyword || "";
  searchModalOpen.value = true;
  await nextTick();
  searchInput.value?.focus();
  searchInput.value?.select();
}

function closeSearchModal() {
  searchModalOpen.value = false;
}

function normalizeSearchKeyword(value) {
  return String(value || "").replace(INVISIBLE_CONTROL_RE, "").trim();
}

function hasVisibleSearchContent(value) {
  return normalizeSearchKeyword(value).replace(/\s/g, "").length > 0;
}

function handleSearchSubmit() {
  const trimmed = normalizeSearchKeyword(localKeyword.value);
  if (!hasVisibleSearchContent(localKeyword.value)) {
    showToast({
      type: "info",
      title: "请输入搜索内容",
      message: "搜索关键词不能为空。",
      duration: 2200,
    });
    searchInput.value?.focus();
    return;
  }
  emit("update:keyword", trimmed);
  searchModalOpen.value = false;
  if (props.homeMode) {
    router.push({
      name: "home",
      query: {
        keyword: trimmed || undefined,
        category: props.activeCategory || undefined,
      },
    });
    return;
  }
  router.push({
    name: "home",
    query: {
      keyword: trimmed || undefined,
      category: props.activeCategory || undefined,
    },
  });
}

function handleCategoryClick(slug) {
  localKeyword.value = "";
  if (props.homeMode) {
    emit("select-category", slug);
    router.push({
      name: "home",
      query: {
        category: slug,
      },
    });
    return;
  }
  router.push({
    name: "home",
    query: {
      category: slug,
    },
  });
}

function goToPreview() {
  if (route.name !== "preview") {
    router.push({ name: "preview" });
  }
}

function goToFavorites() {
  router.push({ name: "favorites" });
}

async function openBackofficeEntryModal() {
  backofficeLoading.value = true;
  backofficeAnswer.value = "";
  backofficeAnswerVisible.value = false;
  try {
    const data = await getBackofficeChallenge();
    backofficeQuestion.value = data?.question || "请输入后台入口口令";
    backofficeModalOpen.value = true;
    await nextTick();
    backofficeAnswerInput.value?.focus();
  } catch (error) {
    showToast({
      type: "error",
      title: "后台入口不可用",
      message: error?.message || "请稍后再试。",
      duration: 2600,
    });
  } finally {
    backofficeLoading.value = false;
  }
}

function closeBackofficeModal() {
  if (backofficeLoading.value) return;
  backofficeModalOpen.value = false;
  backofficeAnswer.value = "";
  backofficeAnswerVisible.value = false;
}

function resetBackofficeClickState(state) {
  window.clearTimeout(state.timer);
  state.count = 0;
  state.startedAt = 0;
  state.timer = null;
}

function getBackofficeClickState() {
  // 使用 window 暂存 3 秒点击窗口，避免普通点击跳转首页后组件重建导致计数丢失。
  window.__qxBackofficeClickState ||= { count: 0, startedAt: 0, timer: null };
  return window.__qxBackofficeClickState;
}

function handleBrandClick(event) {
  // 3 秒内连续点击品牌热区 5 次才打开后台入口，降低普通用户误触概率。
  const state = getBackofficeClickState();
  const now = Date.now();
  if (!state.startedAt || now - state.startedAt > BACKOFFICE_CLICK_WINDOW_MS) {
    resetBackofficeClickState(state);
    state.startedAt = now;
    state.timer = window.setTimeout(() => resetBackofficeClickState(state), BACKOFFICE_CLICK_WINDOW_MS);
  }

  state.count += 1;

  if (state.count < BACKOFFICE_CLICK_LIMIT) {
    return;
  }

  event.preventDefault();
  resetBackofficeClickState(state);
  openBackofficeEntryModal();
}

function writeBackofficeGate() {
  // localStorage 同域多标签页共享，新后台标签页可据此确认刚刚已答对入口问题。
  window.localStorage.setItem(
    BACKOFFICE_GATE_KEY,
    JSON.stringify({
      grantedAt: Date.now(),
      expiresAt: Date.now() + BACKOFFICE_GATE_TTL_MS,
    }),
  );
}

async function submitBackofficeEntry() {
  const answer = backofficeAnswer.value.trim();
  if (!answer) {
    showToast({
      type: "info",
      title: "请输入答案",
      message: "后台入口答案不能为空。",
      duration: 2000,
    });
    backofficeAnswerInput.value?.focus();
    return;
  }

  const targetWindow = window.open("about:blank", "_blank");
  if (targetWindow) {
    targetWindow.opener = null;
  }

  backofficeLoading.value = true;
  try {
    const data = await requestBackofficeEntry(answer);
    if (!data?.path) {
      throw new Error("后台入口返回无效");
    }
    writeBackofficeGate();
    if (targetWindow) {
      targetWindow.location.href = `${window.location.origin}/qx-backoffice`;
    } else {
      showToast({
        type: "error",
        title: "新标签页被拦截",
        message: "请允许浏览器打开新标签页后重试。",
        duration: 2600,
      });
    }
    backofficeModalOpen.value = false;
    backofficeAnswer.value = "";
    backofficeAnswerVisible.value = false;
  } catch (error) {
    targetWindow?.close();
    showToast({
      type: "error",
      title: "验证失败",
      message: error?.message || "答案不正确。",
      duration: 2600,
    });
    backofficeAnswerInput.value?.focus();
  } finally {
    backofficeLoading.value = false;
  }
}

function handleGlobalKeydown(event) {
  if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "k") {
    event.preventDefault();
    openSearchModal();
  }
}

onMounted(() => {
  window.addEventListener("keydown", handleGlobalKeydown);
  removePreviewListener = onWallpaperPreviewModeChange((mode) => {
    previewMode.value = mode;
  });
});

onBeforeUnmount(() => {
  window.removeEventListener("keydown", handleGlobalKeydown);
  removePreviewListener();
});
</script>

<template>
  <header class="site-header">
    <HeaderQXMarquee />
    <div class="site-header-inner">
      <router-link class="site-brand" to="/" @click="handleBrandClick">
        <span class="site-brand-mark" aria-hidden="true">
          <img src="/qx-logo-upload.png" alt="" />
        </span>
        <span class="site-brand-text">琦湘工具集合</span>
      </router-link>

      <div class="site-nav-wrap">
        <nav class="site-nav">
          <button
            v-for="item in resolvedCategories"
            :key="item.slug"
            type="button"
            class="site-nav-item"
            :class="{ active: activeCategory === item.slug }"
            @click="handleCategoryClick(item.slug)"
          >
            {{ item.name }}
            <span class="site-nav-caret">▼</span>
          </button>

          <button
            type="button"
            class="site-nav-item preview-switch-item"
            :class="{ active: previewActive }"
            @click="goToPreview"
          >
            手动预览
            <span class="site-nav-caret">✦</span>
          </button>
        </nav>
      </div>

      <div class="site-header-actions">
        <div class="header-favorite-wrap">
          <button
            type="button"
            class="favorite-trigger"
            :class="{ active: favoriteActive }"
            @click="goToFavorites"
          >
            <span class="favorite-trigger-star">★</span>
            <span>已收藏</span>
            <span v-if="favoriteCount" class="favorite-trigger-count">{{ favoriteCount }}</span>
          </button>
        </div>

        <button
          type="button"
          class="site-search-trigger"
          :class="{ 'is-active': searchActive }"
          @click="openSearchModal"
        >
          <span aria-hidden="true">🔍</span>
          <span>搜索</span>
        </button>
      </div>
    </div>

    <teleport to="body">
      <div v-if="searchModalOpen" class="site-search-modal" @keydown.esc="closeSearchModal">
        <button type="button" class="site-search-backdrop" aria-label="关闭搜索" @click="closeSearchModal"></button>
        <form class="site-search-dialog" role="search" @submit.prevent="handleSearchSubmit">
          <input ref="searchInput" v-model="localKeyword" type="search" placeholder="输入关键词……" />
          <button type="submit">
            <span aria-hidden="true">🔍</span>
            <span>搜索</span>
          </button>
        </form>
      </div>
    </teleport>

    <teleport to="body">
      <div v-if="backofficeModalOpen" class="backoffice-entry-modal" @keydown.esc="closeBackofficeModal">
        <button
          type="button"
          class="backoffice-entry-backdrop"
          aria-label="关闭后台入口"
          @click="closeBackofficeModal"
        ></button>
        <form class="backoffice-entry-dialog" @submit.prevent="submitBackofficeEntry">
          <h2>{{ backofficeQuestion }}</h2>
          <div class="backoffice-entry-secret">
            <input
              ref="backofficeAnswerInput"
              v-model="backofficeAnswer"
              type="text"
              autocomplete="off"
              autocapitalize="off"
              spellcheck="false"
              :class="{ 'is-masked': !backofficeAnswerVisible }"
            />
            <button type="button" :disabled="backofficeLoading" @click="backofficeAnswerVisible = !backofficeAnswerVisible">
              {{ backofficeAnswerVisible ? "隐藏" : "显示" }}
            </button>
          </div>
          <div class="backoffice-entry-actions">
            <button type="button" :disabled="backofficeLoading" @click="closeBackofficeModal">取消</button>
            <button type="submit" :disabled="backofficeLoading">{{ backofficeLoading ? "验证中…" : "确认" }}</button>
          </div>
        </form>
      </div>
    </teleport>
  </header>
</template>
