<script setup>
import SiteWallpaper from "./components/SiteWallpaper.vue";
import ToastViewport from "./components/ToastViewport.vue";
import AiAssistantWidget from "./components/ai-assistant/AiAssistantWidget.vue";
</script>

<template>
  <div class="app-shell">
    <router-view v-slot="{ Component, route }">
      <SiteWallpaper v-if="!route.meta.backoffice" :mode="route.meta.wallpaperMode || 'seasonal'" />
      <ToastViewport />
      <component :is="Component" :key="route.path" />
    </router-view>
    <!-- AI 助手为独立自包含模块，放在 router-view 外，跨页面常驻、不与工具耦合 -->
    <AiAssistantWidget v-if="$route.meta.backoffice !== true" />
  </div>
</template>
