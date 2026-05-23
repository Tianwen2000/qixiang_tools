<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";

import { fallbackCategories } from "../data/fallback-meta.js";
import { useFavoriteTools } from "../utils/favorite-tools.js";
import { getWallpaperPreviewMode, onWallpaperPreviewModeChange } from "../utils/wallpaper-preview.js";
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
const previewMode = ref(getWallpaperPreviewMode());
const localKeyword = ref(props.keyword || "");
const { favoriteCount } = useFavoriteTools();

let removePreviewListener = () => {};

const resolvedCategories = computed(() => (props.categories.length ? props.categories : fallbackCategories));
const previewActive = computed(() => route.name === "preview" || previewMode.value !== "auto");
const searchActive = computed(() => localKeyword.value.trim().length > 0);
const favoriteActive = computed(() => route.name === "favorites" || favoriteCount.value > 0);

watch(
  () => props.keyword,
  (value) => {
    localKeyword.value = value || "";
  },
);

watch(localKeyword, (value) => {
  emit("update:keyword", value);
});

function focusSearch() {
  searchInput.value?.focus();
}

function handleSearchSubmit() {
  const trimmed = localKeyword.value.trim();
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
    focusSearch();
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

        <form
          class="site-search"
          :class="{ 'is-active': searchActive }"
          @submit.prevent="handleSearchSubmit"
          @click="focusSearch"
        >
          <button type="submit" class="site-search-icon-button" aria-label="搜索工具">
            <span class="site-search-icon">⌕</span>
          </button>
          <input ref="searchInput" v-model="localKeyword" type="search" placeholder="搜索工具" />
          <kbd>Ctrl+K</kbd>
        </form>
      </div>
    </div>
  </header>
</template>
