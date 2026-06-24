<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";

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
const previewMode = ref(getWallpaperPreviewMode());
const localKeyword = ref(props.keyword || "");
const { favoriteCount } = useFavoriteTools();

let removePreviewListener = () => {};

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
      <router-link class="site-brand" to="/">
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
  </header>
</template>
