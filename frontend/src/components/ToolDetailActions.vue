<script setup>
import { computed } from "vue";
import { useRouter } from "vue-router";

import { isFavoriteTool, toggleFavoriteTool } from "../utils/favorite-tools.js";
import { showToast } from "../utils/toast.js";

const props = defineProps({
  tool: {
    type: Object,
    required: true,
  },
});

const router = useRouter();
const favorite = computed(() => isFavoriteTool(props.tool.slug));

function buildToolUrl() {
  if (typeof window === "undefined") {
    return `/tool/${props.tool.slug}`;
  }
  return window.location.href;
}

function handleFavoriteToggle() {
  const nextFavorite = toggleFavoriteTool(props.tool.slug);
  showToast({
    type: nextFavorite ? "success" : "info",
    title: nextFavorite ? "已加入收藏" : "已取消收藏",
    message: nextFavorite ? `${props.tool.name} 已加入本地收藏列表。` : `${props.tool.name} 已从本地收藏列表移除。`,
    duration: 2200,
  });
}

function goToFeedback() {
  router.push({
    name: "feedback",
    query: {
      tool: props.tool.slug,
      name: props.tool.name,
      from: buildToolUrl(),
    },
  });
}

function goToSupport() {
  router.push({
    name: "support",
    query: {
      from: props.tool.slug,
    },
  });
}
</script>

<template>
  <section class="detail-actions-card">
    <div class="detail-actions-bar">
      <button type="button" class="detail-action-button" :class="{ active: favorite }" @click="handleFavoriteToggle">
        {{ favorite ? "已收藏" : "收藏" }}
      </button>
      <button type="button" class="detail-action-button" @click="goToFeedback">反馈</button>
      <button type="button" class="detail-action-button" @click="goToSupport">打赏</button>
    </div>
  </section>
</template>
