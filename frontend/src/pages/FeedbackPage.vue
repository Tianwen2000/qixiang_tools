<script setup>
// 文件说明：定义 FeedbackPage 页面组件。
import { computed, ref } from "vue";
import { useRoute } from "vue-router";

import { submitFeedback } from "../api/feedback.js";
import GlassSelect from "../components/GlassSelect.vue";
import SiteHeader from "../components/SiteHeader.vue";
import { getFallbackTool } from "../data/fallback-meta.js";
import { showToast } from "../utils/toast.js";

const route = useRoute();
const headerKeyword = ref(typeof route.query.keyword === "string" ? route.query.keyword : "");
const submitting = ref(false);
const submitStatus = ref({ type: "", message: "" });
const feedbackType = ref("bug");
const content = ref("");
const contactType = ref("email");
const contactValue = ref("");
const FEEDBACK_DEVICE_ID_KEY = "tw-feedback-device-id-v1";

const feedbackTypeOptions = [
  { value: "bug", label: "问题反馈" },
  { value: "suggestion", label: "功能建议" },
  { value: "content", label: "内容纠错" },
  { value: "other", label: "其他" },
];

const contactTypeOptions = [
  { value: "email", label: "邮箱" },
  { value: "qq", label: "QQ" },
  { value: "wechat", label: "微信" },
];

const toolSlug = computed(() => (typeof route.query.tool === "string" ? route.query.tool : ""));
const toolMeta = computed(() => getFallbackTool(toolSlug.value));
const toolName = computed(() => toolMeta.value?.name || (typeof route.query.name === "string" ? route.query.name : toolSlug.value || "未指定工具"));
const toolUrl = computed(() => {
  if (typeof route.query.from === "string" && route.query.from) {
    return route.query.from;
  }
  if (typeof window === "undefined" || !toolSlug.value) {
    return toolSlug.value ? `/tool/${toolSlug.value}` : "";
  }
  return `${window.location.origin}/tool/${toolSlug.value}`;
});
const deliveryHint = computed(() =>
  import.meta.env.VITE_FEEDBACK_ENDPOINT
    ? "当前会提交到你配置的 Serverless 反馈接口。"
    : "当前未配置线上反馈接口，提交后会先本地暂存，方便你后续接入 Cloudflare Workers。",
);

function getContactPlaceholder() {
  const placeholderMap = {
    email: "例如 you@example.com",
    qq: "例如 123456789",
    wechat: "例如 your_wechat_id",
  };
  return placeholderMap[contactType.value] || "请输入联系方式";
}

function getFeedbackDeviceId() {
  if (typeof window === "undefined") {
    return "";
  }
  const randomPart =
    typeof crypto !== "undefined" && crypto.randomUUID
      ? crypto.randomUUID()
      : `${Date.now()}-${Math.random().toString(16).slice(2)}`;
  const deviceId = `web-${randomPart}`;
  try {
    const existing = window.localStorage.getItem(FEEDBACK_DEVICE_ID_KEY);
    if (existing) {
      return existing;
    }
    window.localStorage.setItem(FEEDBACK_DEVICE_ID_KEY, deviceId);
  } catch {
    return deviceId;
  }
  return deviceId;
}

async function handleSubmit() {
  if (!content.value.trim()) {
    submitStatus.value = { type: "error", message: "请先写一点反馈内容。" };
    showToast({
      type: "error",
      title: "反馈内容不能为空",
      message: "至少写一下问题现象、建议或复现步骤。",
      duration: 2400,
    });
    return;
  }

  if (!contactValue.value.trim()) {
    submitStatus.value = { type: "error", message: "请补充一种可联系到你的方式。" };
    showToast({
      type: "error",
      title: "请补充联系方式",
      message: "邮箱、QQ 或微信三选一填写即可。",
      duration: 2400,
    });
    return;
  }

  submitting.value = true;
  submitStatus.value = { type: "", message: "" };
  try {
    const result = await submitFeedback({
      toolSlug: toolSlug.value,
      toolName: toolName.value,
      toolUrl: toolUrl.value,
      feedbackType: feedbackType.value,
      content: content.value.trim(),
      contactType: contactType.value,
      contactValue: contactValue.value.trim(),
      submittedPage: typeof window === "undefined" ? route.fullPath : window.location.href,
      userAgent: typeof navigator === "undefined" ? "" : navigator.userAgent,
      deviceId: getFeedbackDeviceId(),
    });

    submitStatus.value = {
      type: "success",
      message: result.message,
    };
    showToast({
      type: "success",
      title: "反馈已提交",
      message: result.message,
      duration: 2600,
    });
    content.value = "";
    contactValue.value = "";
  } catch (error) {
    const message = error.message || "反馈提交失败，请稍后再试。";
    submitStatus.value = {
      type: "error",
      message,
    };
    showToast({
      type: "error",
      title: "提交失败",
      message,
      duration: 2800,
    });
  } finally {
    submitting.value = false;
  }
}
</script>

<template>
  <main class="tool-detail-page">
    <SiteHeader :active-category="toolMeta?.category || ''" :keyword="headerKeyword" @update:keyword="headerKeyword = $event" />

    <div class="page-shell feedback-page-shell">
      <section class="detail-header feedback-page-hero" :style="{ '--detail-accent': '#2aa6c5', '--detail-soft': 'rgba(42, 166, 197, 0.14)' }">
        <div class="detail-header-copy">
          <div class="tool-header-top">
            <span class="tool-chip">反馈页</span>
            <span class="tool-chip muted">独立页面</span>
          </div>
          <h1>工具反馈</h1>
          <p>把问题、建议或纠错内容单独提交，不和小工具页面混在一起。</p>
          <p class="tool-description">{{ deliveryHint }}</p>
        </div>
      </section>

      <section class="tool-form feedback-page-form">
        <section class="time-tool-note">
          <strong>当前工具信息</strong>
          <p>工具名称：{{ toolName }}</p>
          <p>工具 slug：{{ toolSlug || "未指定" }}</p>
          <p>工具地址：{{ toolUrl || "未指定" }}</p>
        </section>

        <div class="feedback-form-grid">
          <label class="detail-feedback-field">
            <span>反馈类型</span>
            <GlassSelect v-model="feedbackType" :options="feedbackTypeOptions" placeholder="请选择反馈类型" />
          </label>

          <label class="detail-feedback-field wide">
            <span>反馈内容</span>
            <textarea v-model="content" rows="7" placeholder="请尽量写清楚现象、期望结果、复现步骤或改进建议。"></textarea>
          </label>

          <label class="detail-feedback-field">
            <span>联系方式类型</span>
            <GlassSelect v-model="contactType" :options="contactTypeOptions" placeholder="请选择联系方式类型" />
          </label>

          <label class="detail-feedback-field">
            <span>联系方式</span>
            <input v-model="contactValue" type="text" :placeholder="getContactPlaceholder()" />
          </label>
        </div>

        <div class="detail-action-panel-actions">
          <button type="button" :disabled="submitting" @click="handleSubmit">
            {{ submitting ? "提交中..." : "提交反馈" }}
          </button>
        </div>

        <section v-if="submitStatus.message" class="status-card feedback-submit-status" :data-type="submitStatus.type">
          <strong>{{ submitStatus.type === "success" ? "提交成功" : "提交失败" }}</strong>
          <p>{{ submitStatus.message }}</p>
        </section>
      </section>
    </div>
  </main>
</template>
