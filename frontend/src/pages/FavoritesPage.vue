<script setup>
// 文件说明：定义 FavoritesPage 页面组件。
import { computed, ref } from "vue";

import SiteHeader from "../components/SiteHeader.vue";
import { getCategoryTheme, getToolModeLabel } from "../data/ui-mapping.js";
import { getFallbackTool } from "../data/fallback-meta.js";
import { clearFavoriteTools, useFavoriteTools } from "../utils/favorite-tools.js";
import { showToast } from "../utils/toast.js";

const headerKeyword = ref("");
const { favoriteSlugs } = useFavoriteTools();

const favoriteEntries = computed(() =>
  favoriteSlugs.value
    .map((slug) => getFallbackTool(slug) || { slug, name: slug, category: "default", summary: "本地收藏工具", description: "", input_mode: "local" })
    .filter(Boolean),
);

function getTheme(tool) {
  return getCategoryTheme(tool.category);
}

function handleClearAll() {
  clearFavoriteTools();
  showToast({
    type: "success",
    title: "收藏已清空",
    message: "当前浏览器中的收藏工具已全部清空。",
    duration: 2200,
  });
}
</script>

<template>
  <main class="tool-detail-page">
    <SiteHeader :keyword="headerKeyword" @update:keyword="headerKeyword = $event" />

    <div class="page-shell favorites-page-shell">
      <section class="detail-header favorites-page-hero" :style="{ '--detail-accent': '#6077c8', '--detail-soft': 'rgba(96, 119, 200, 0.14)' }">
        <div class="detail-header-copy">
          <div class="tool-header-top">
            <span class="tool-chip">我的收藏</span>
            <span class="tool-chip muted">本地列表</span>
          </div>
          <h1>我的收藏</h1>
          <p>收藏的小工具会保存在当前浏览器，可快速回访和清空列表。</p>
        </div>
      </section>

      <section class="favorites-info-bar">
        <div class="favorites-info-copy">
          <span class="favorites-info-icon">i</span>
          <p>收藏的工具会在这里显示并保存在本地，当前浏览器有效。</p>
        </div>
        <button v-if="favoriteEntries.length" type="button" class="mega-panel-action" @click="handleClearAll">清空全部</button>
      </section>

      <section v-if="!favoriteEntries.length" class="empty-state status-card">
        <h3>当前还没有收藏工具</h3>
        <p>你可以先进入任意小工具详情页，点击“收藏”后再回来查看。</p>
      </section>

      <section v-else class="favorites-grid">
        <article
          v-for="tool in favoriteEntries"
          :key="tool.slug"
          class="favorite-tool-card"
          :style="{ '--tool-accent': getTheme(tool).accent, '--tool-soft': getTheme(tool).soft }"
        >
          <router-link class="favorite-tool-link" :to="{ name: 'tool', params: { slug: tool.slug }, query: { category: tool.category } }">
            <div class="favorite-tool-icon">{{ getTheme(tool).label.slice(0, 1) }}</div>
            <div class="favorite-tool-copy">
              <div class="tool-card-top">
                <span class="tool-chip">{{ getToolModeLabel(tool) }}</span>
                <span class="tool-chip muted">{{ getTheme(tool).label }}</span>
              </div>
              <h3>{{ tool.name }}</h3>
              <p>{{ tool.summary }}</p>
            </div>
          </router-link>
        </article>
      </section>
    </div>
  </main>
</template>
