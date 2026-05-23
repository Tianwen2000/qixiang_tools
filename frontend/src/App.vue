<script setup>
import SiteWallpaper from "./components/SiteWallpaper.vue";
import ToastViewport from "./components/ToastViewport.vue";
</script>

<template>
  <div class="app-shell">
    <router-view v-slot="{ Component, route }">
      <SiteWallpaper :mode="route.meta.wallpaperMode || 'seasonal'" />
      <ToastViewport />
      <component :is="Component" :key="route.path" />
    </router-view>
  </div>
</template>
