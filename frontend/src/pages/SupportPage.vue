<script setup>
import { computed, ref } from "vue";
import { useRoute } from "vue-router";

import SiteHeader from "../components/SiteHeader.vue";
import { getFallbackTool } from "../data/fallback-meta.js";

const route = useRoute();
const headerKeyword = ref(typeof route.query.keyword === "string" ? route.query.keyword : "");

const fromTool = computed(() => {
  const slug = typeof route.query.from === "string" ? route.query.from : "";
  return getFallbackTool(slug);
});
</script>

<template>
  <main class="tool-detail-page">
    <SiteHeader :active-category="fromTool?.category || ''" :keyword="headerKeyword" @update:keyword="headerKeyword = $event" />

    <div class="page-shell support-page-shell">
      <section class="detail-header support-page-hero" :style="{ '--detail-accent': '#1f9d8b', '--detail-soft': 'rgba(31, 157, 139, 0.14)' }">
        <div class="detail-header-copy">
          <div class="tool-header-top">
            <span class="tool-chip">统一打赏页</span>
            <span class="tool-chip muted">Support</span>
          </div>
          <h1>感谢支持琦湘工具集合</h1>
          <p>所有小工具共用这一页，微信和支付宝收款码已经放好，扫码就能直接支持。</p>
          <p v-if="fromTool" class="tool-description">当前来自：{{ fromTool.name }}</p>
        </div>
      </section>

      <section class="tool-form support-page-body">
        <div class="detail-tip-grid">
          <div class="detail-tip-slot support-payment-card">
            <strong>微信支付</strong>
            <img class="support-payment-image" src="/微信收款.jpg" alt="微信支付收款码" />
          </div>
          <div class="detail-tip-slot support-payment-card">
            <strong>支付宝</strong>
            <img class="support-payment-image" src="/支付宝收款.jpg" alt="支付宝收款码" />
          </div>
        </div>

        <section class="time-tool-note">
          <strong>说明</strong>
          <p>收款码已接入当前页面，保持简洁展示，不额外增加复杂打赏流程。</p>
        </section>
      </section>
    </div>
  </main>
</template>
