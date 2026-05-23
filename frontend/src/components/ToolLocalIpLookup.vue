<script setup>
import { computed, ref } from "vue";

import { executeTextTool } from "../api/tools.js";
import { showToast, updateToast } from "../utils/toast.js";

const props = defineProps({
  tool: {
    type: Object,
    required: true,
  },
});

const loading = ref(false);
const result = ref(null);
const outputVisible = ref(true);

const splitStatus = computed(() => result.value?.split_result?.status || "unknown");
const splitTone = computed(() => {
  if (splitStatus.value === "same") {
    return "success";
  }
  if (splitStatus.value === "split") {
    return "warning";
  }
  return "danger";
});
const splitLabel = computed(() => {
  if (splitStatus.value === "same") {
    return "出口一致";
  }
  if (splitStatus.value === "split") {
    return "疑似分流";
  }
  return "无法判断";
});
const publicTone = computed(() => {
  const status = result.value?.public_summary?.status;
  if (status === "same") {
    return "success";
  }
  if (status === "different") {
    return "warning";
  }
  return "danger";
});

function displayIp(item) {
  return item?.ip || "暂无结果";
}

async function lookupIp() {
  if (loading.value) {
    return;
  }
  loading.value = true;
  outputVisible.value = true;
  const toastId = showToast({
    type: "loading",
    title: "正在查询",
    message: "正在检测内网、公网与分流出口...",
    duration: 0,
  });
  try {
    const data = await executeTextTool(props.tool.slug, { text: "", params: {} });
    result.value = data.result;
    updateToast(toastId, {
      type: "success",
      title: "查询完成",
      message: "IP 检测结果已更新。",
      duration: 2200,
    });
  } catch (err) {
    updateToast(toastId, {
      type: "error",
      title: "查询失败",
      message: err.message || "IP 查询失败",
      duration: 3600,
    });
  } finally {
    loading.value = false;
  }
}

function clearOutput() {
  outputVisible.value = false;
  showToast({
    type: "info",
    title: "已清空输出",
    message: "IP 查询结果已从当前页面隐藏。",
    duration: 1800,
  });
}
</script>

<template>
  <section class="tool-form local-tool-panel">
    <div class="local-tool-header">
      <div class="local-tool-header-bar">
        <div>
          <h3>内网、公网与分流 IP 检测</h3>
          <p>查询由后端服务发起，会对国内视角、境外视角和多个公网服务做交叉验证。</p>
        </div>
        <div class="tool-actions">
          <button type="button" :disabled="loading" @click="lookupIp">{{ loading ? "查询中..." : "开始查询" }}</button>
          <button v-if="result" type="button" class="secondary-button" @click="clearOutput">清空输出</button>
        </div>
      </div>
    </div>

    <section v-if="!result" class="result-panel">
      <div class="result-panel-head">
        <h3>等待查询</h3>
      </div>
      <p class="empty-hint">点击“开始查询”后，会返回本机内网 IP、国内真实出口、境外出口和公网服务投票结果。</p>
    </section>

    <template v-else-if="outputVisible">
      <div class="insight-grid">
        <article class="insight-card">
          <span class="insight-label">本机内网 IP</span>
          <strong class="insight-value">{{ result.local_ip }}</strong>
        </article>
        <article class="insight-card">
          <span class="insight-label">国内服务器视角</span>
          <strong class="insight-value">{{ displayIp(result.domestic) }}</strong>
          <small>{{ result.domestic?.url || "未返回来源" }}</small>
        </article>
        <article class="insight-card">
          <span class="insight-label">境外服务器视角</span>
          <strong class="insight-value">{{ displayIp(result.overseas) }}</strong>
          <small>{{ result.overseas?.url || "未返回来源" }}</small>
        </article>
        <article class="insight-card">
          <span class="insight-label">分流判断</span>
          <strong class="insight-value">{{ splitLabel }}</strong>
          <span class="summary-chip" :class="splitTone">{{ result.split_result.message }}</span>
        </article>
      </div>

      <section class="result-panel">
        <div class="result-panel-head">
          <h3>公网服务交叉验证</h3>
          <span class="summary-chip" :class="publicTone">
            {{ result.public_summary.majority_ip || "暂无多数 IP" }}
          </span>
        </div>
        <div class="ip-lookup-service-list">
          <article v-for="item in result.public_results" :key="item.service" class="ip-lookup-service-item">
            <div>
              <strong>{{ item.service }}</strong>
              <small>{{ item.url || "请求失败" }}</small>
            </div>
            <span class="status-chip" :class="{ success: item.ok, danger: !item.ok }">{{ item.ip }}</span>
          </article>
        </div>
      </section>

      <section class="result-panel">
        <div class="result-panel-head">
          <h3>结果分析</h3>
          <span class="summary-chip" :class="publicTone">{{ result.public_summary.message }}</span>
        </div>
        <div class="ip-lookup-vote-list">
          <article v-for="vote in result.public_summary.votes" :key="vote.ip" class="ip-lookup-vote-item">
            <strong>{{ vote.ip }}</strong>
            <span>{{ vote.count }} 票</span>
          </article>
        </div>
        <p class="empty-hint">{{ result.public_summary.relation }}</p>
      </section>

      <section class="result-panel">
        <div class="result-panel-head">
          <h3>说明</h3>
        </div>
        <ul class="ip-lookup-note-list">
          <li v-for="note in result.notes" :key="note">{{ note }}</li>
        </ul>
      </section>
    </template>

    <section v-else class="result-panel">
      <div class="result-panel-head">
        <h3>结果</h3>
      </div>
      <p class="empty-hint">输出已清空，可点击“开始查询”重新检测。</p>
    </section>
  </section>
</template>
