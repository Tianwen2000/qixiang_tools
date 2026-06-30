<script setup>
// 文件说明：定义 PreviewPage 页面组件。
import { ref } from "vue";

import SiteHeader from "../components/SiteHeader.vue";
import WallpaperPreviewPanel from "../components/WallpaperPreviewPanel.vue";

const headerKeyword = ref("");
</script>

<template>
  <main class="tool-detail-page">
    <SiteHeader :keyword="headerKeyword" @update:keyword="headerKeyword = $event" />

    <div class="page-shell preview-page-shell">
      <section class="detail-header preview-page-hero" :style="{ '--detail-accent': '#5a7cff', '--detail-soft': 'rgba(90, 124, 255, 0.14)' }">
        <div class="detail-header-copy">
          <div class="tool-header-top">
            <span class="tool-chip">手动预览</span>
            <span class="tool-chip muted">独立页面</span>
          </div>
          <h1>四季背景预览</h1>
          <p>这里可以单独切换春夏秋冬背景效果，不会再挤在顶部导航弹层里。</p>
          <p class="tool-description">切换结果只影响当前浏览器，适合你手动检查全站壁纸表现。</p>
        </div>
      </section>

      <section class="tool-form preview-page-body">
        <WallpaperPreviewPanel embedded />
      </section>
    </div>
  </main>
</template>
