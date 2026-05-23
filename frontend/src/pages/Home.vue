<script setup>
import { computed, onMounted, ref, watch } from "vue";
import { useRoute } from "vue-router";

import { listCategories, listTools } from "../api/tools.js";
import LoadingState from "../components/LoadingState.vue";
import SiteHeader from "../components/SiteHeader.vue";
import ToolCard from "../components/ToolCard.vue";
import ToolDateTimeCard from "../components/ToolDateTimeCard.vue";
import { readJsonCache, writeJsonCache } from "../utils/page-cache.js";

const route = useRoute();
const META_CACHE_KEY = "tw-meta-cache-v1";
const HOME_STATE_CACHE_KEY = "tw-home-state-v1";
const categories = ref([]);
const tools = ref([]);
const activeCategory = ref("");
const keyword = ref("");
const loading = ref(true);
const error = ref("");

const filteredTools = computed(() =>
  tools.value.filter((tool) => {
    const byKeyword =
      !keyword.value ||
      tool.name.toLowerCase().includes(keyword.value.toLowerCase()) ||
      tool.summary.toLowerCase().includes(keyword.value.toLowerCase()) ||
      tool.description.toLowerCase().includes(keyword.value.toLowerCase());
    return byKeyword;
  }),
);

const activeCategoryMeta = computed(() => {
  return categories.value.find((item) => item.slug === activeCategory.value) || categories.value[0] || null;
});

const displayTools = computed(() => {
  if (keyword.value) {
    return filteredTools.value;
  }
  return tools.value.filter((tool) => tool.category === activeCategory.value);
});

const displayTitle = computed(() => {
  if (keyword.value) {
    return "搜索结果";
  }
  return activeCategoryMeta.value?.name || "工具列表";
});

const displayDescription = computed(() => {
  if (keyword.value) {
    return `与 “${keyword.value}” 相关的工具结果`;
  }
  return activeCategoryMeta.value?.description || "当前可用工具";
});

const toolRouteQuery = computed(() => {
  const query = {};
  if (activeCategory.value) {
    query.category = activeCategory.value;
  }
  if (keyword.value.trim()) {
    query.keyword = keyword.value.trim();
  }
  return query;
});

function activateCategory(slug) {
  activeCategory.value = slug;
}

function applyRouteState(categoryData = categories.value) {
  const cachedState = readJsonCache(HOME_STATE_CACHE_KEY, {});
  const hasRouteKeyword = Object.prototype.hasOwnProperty.call(route.query, "keyword");
  const hasRouteCategory = Object.prototype.hasOwnProperty.call(route.query, "category");
  const routeKeyword = typeof route.query.keyword === "string" ? route.query.keyword : "";
  const routeCategory = typeof route.query.category === "string" ? route.query.category : "";
  const nextKeyword = hasRouteKeyword ? routeKeyword : hasRouteCategory ? "" : cachedState.keyword || "";
  const nextCategory = hasRouteCategory ? routeCategory : cachedState.category || "";

  keyword.value = nextKeyword;

  if (nextCategory && categoryData.some((item) => item.slug === nextCategory)) {
    activeCategory.value = nextCategory;
    return;
  }

  if (!activeCategory.value && categoryData.length) {
    activeCategory.value = categoryData[0].slug;
  }
}

function hydrateFromCache() {
  const cachedMeta = readJsonCache(META_CACHE_KEY, null);
  if (!cachedMeta?.categories?.length || !cachedMeta?.tools?.length) {
    return false;
  }
  categories.value = cachedMeta.categories;
  tools.value = cachedMeta.tools;
  loading.value = false;
  applyRouteState(cachedMeta.categories);
  return true;
}

async function fetchMeta() {
  loading.value = !tools.value.length;
  error.value = "";
  try {
    const [categoryData, toolData] = await Promise.all([listCategories(), listTools()]);
    categories.value = categoryData;
    tools.value = toolData;
    writeJsonCache(META_CACHE_KEY, { categories: categoryData, tools: toolData });
    applyRouteState(categoryData);
  } catch (err) {
    if (!tools.value.length) {
      error.value = err.message || "加载失败";
    }
  } finally {
    loading.value = false;
  }
}

watch(
  [() => route.query.category, () => route.query.keyword, () => categories.value.length],
  () => {
    if (categories.value.length) {
      applyRouteState();
    }
  },
);

watch(
  [activeCategory, keyword],
  ([category, searchKeyword]) => {
    if (!category && !searchKeyword) {
      return;
    }
    writeJsonCache(HOME_STATE_CACHE_KEY, {
      category,
      keyword: searchKeyword.trim(),
    });
  },
  { deep: false },
);

hydrateFromCache();

onMounted(() => {
  fetchMeta();
});
</script>

<template>
  <main class="catalog-page">
    <SiteHeader
      :categories="categories"
      :active-category="activeCategory"
      :keyword="keyword"
      home-mode
      @update:keyword="keyword = $event"
      @select-category="activateCategory"
    />

    <div class="page-shell">
      <section class="showcase-strip">
        <article class="promo-card promo-card-large">
          <div class="promo-card-copy">
            <h1>{{ activeCategoryMeta?.name || "工具导航" }}</h1>
            <p>{{ activeCategoryMeta?.description || "轻量、清爽、可快速扩展的在线工具页面。" }}</p>
          </div>
          <ToolDateTimeCard compact />
        </article>
      </section>

      <section v-if="keyword" class="section-head">
        <div>
          <p class="section-kicker">搜索模式</p>
          <h2>{{ displayTitle }}</h2>
          <p>{{ displayDescription }}</p>
        </div>
        <div class="section-stat">
          <strong>{{ displayTools.length }}</strong>
          <span>个工具</span>
        </div>
      </section>

      <LoadingState v-if="loading" />
      <section v-else-if="error" class="empty-state status-card">
        <h3>工具列表暂时加载失败</h3>
        <p>{{ error }}</p>
        <button type="button" class="mega-panel-action" @click="fetchMeta">重新加载</button>
      </section>

      <section v-else class="tool-grid tool-grid-page">
        <ToolCard v-for="tool in displayTools" :key="tool.slug" :tool="tool" :query="toolRouteQuery" />
      </section>

      <section v-if="!loading && !error && displayTools.length === 0" class="empty-state">
        <h3>暂时没有匹配的工具</h3>
        <p>试试切换分类，或者使用更短的关键词搜索。</p>
      </section>
    </div>
  </main>
</template>
