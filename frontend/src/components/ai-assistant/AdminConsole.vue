<script setup>
import { computed, onMounted, ref } from "vue";

import { listAdminFeedback, listAdminLogs } from "./service.js";

const tab = ref("feedback");
const feedback = ref([]);
const logs = ref([]);
const loading = ref(true);
const errorMsg = ref("");

function fmt(iso) {
  return iso ? String(iso).replace("T", " ").slice(0, 19) : "";
}

const eventLabel = { register: "注册", login: "登录", logout: "退出" };
const feedbackTypeLabel = { bug: "问题反馈", suggestion: "功能建议", content: "内容纠错", praise: "表扬", other: "其他" };

const feedbackCount = computed(() => feedback.value.length);
const logsCount = computed(() => logs.value.length);

async function load() {
  loading.value = true;
  errorMsg.value = "";
  try {
    const [fb, lg] = await Promise.all([listAdminFeedback(), listAdminLogs()]);
    feedback.value = fb?.items || [];
    logs.value = lg?.items || [];
  } catch (error) {
    const msg = error?.message || "加载失败";
    errorMsg.value = msg.includes("管理员")
      ? "需要管理员权限：请先用管理员账号在站内登录，再打开本页。"
      : msg.includes("登录")
        ? "尚未登录：请先用管理员账号在站内登录，再打开本页。"
        : msg;
  } finally {
    loading.value = false;
  }
}

onMounted(load);
</script>

<template>
  <div class="qxadmin">
    <div class="qxadmin-card">
      <header class="qxadmin-head">
        <h1>反馈系统 · 只读查看</h1>
        <button type="button" class="qxadmin-refresh" :disabled="loading" @click="load">
          {{ loading ? "加载中…" : "刷新" }}
        </button>
      </header>

      <p v-if="errorMsg" class="qxadmin-error">{{ errorMsg }}</p>

      <template v-else>
        <div class="qxadmin-tabs">
          <button type="button" :class="{ active: tab === 'feedback' }" @click="tab = 'feedback'">
            反馈（{{ feedbackCount }}）
          </button>
          <button type="button" :class="{ active: tab === 'logs' }" @click="tab = 'logs'">
            账号活动日志（{{ logsCount }}）
          </button>
        </div>

        <!-- 反馈 -->
        <div v-show="tab === 'feedback'" class="qxadmin-table-wrap">
          <p v-if="!loading && !feedback.length" class="qxadmin-empty">暂无反馈</p>
          <table v-else class="qxadmin-table">
            <colgroup>
              <col class="qxadmin-col-time" />
              <col class="qxadmin-col-type" />
              <col class="qxadmin-col-content" />
              <col class="qxadmin-col-tool" />
              <col class="qxadmin-col-contact" />
              <col class="qxadmin-col-account" />
              <col class="qxadmin-col-source" />
            </colgroup>
            <thead>
              <tr>
                <th>时间</th><th>类型</th><th>内容</th><th>工具</th><th>联系方式</th><th>账号</th><th>来源页</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in feedback" :key="row.id">
                <td class="nowrap">{{ fmt(row.created_at) }}</td>
                <td>{{ feedbackTypeLabel[row.feedback_type] || row.feedback_type || "-" }}</td>
                <td class="content">
                  <div class="qxadmin-cell-scroll">{{ row.content }}</div>
                </td>
                <td>
                  <div class="qxadmin-cell-scroll compact">{{ row.tool_name || row.tool_slug || "-" }}</div>
                </td>
                <td>
                  <div class="qxadmin-cell-scroll compact">
                    {{ row.contact_type ? `${row.contact_type}：${row.contact_value}` : (row.contact_value || "-") }}
                  </div>
                </td>
                <td>{{ row.account || "" }}</td>
                <td class="dim">
                  <div class="qxadmin-cell-scroll url">{{ row.submitted_page || "-" }}</div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- 活动日志 -->
        <div v-show="tab === 'logs'" class="qxadmin-table-wrap">
          <p v-if="!loading && !logs.length" class="qxadmin-empty">暂无日志</p>
          <table v-else class="qxadmin-table">
            <thead>
              <tr><th>时间</th><th>事件</th><th>账号</th><th>IP</th><th>UA</th></tr>
            </thead>
            <tbody>
              <tr v-for="row in logs" :key="row.id">
                <td class="nowrap">{{ fmt(row.created_at) }}</td>
                <td>{{ eventLabel[row.event] || row.event }}</td>
                <td>{{ row.account || "-" }}</td>
                <td class="nowrap">{{ row.ip || "-" }}</td>
                <td class="dim ua">
                  <div class="qxadmin-cell-scroll ua">{{ row.user_agent || "-" }}</div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </template>
    </div>
  </div>
</template>

<style scoped>
.qxadmin {
  position: relative;
  z-index: 1;
  min-height: 100vh;
  padding: 28px 20px;
  display: flex;
  justify-content: center;
}

.qxadmin-card {
  width: min(1100px, 100%);
  align-self: flex-start;
  background: rgba(255, 255, 255, 0.94);
  border: 1px solid rgba(159, 188, 224, 0.5);
  border-radius: 18px;
  box-shadow: 0 18px 44px rgba(34, 70, 124, 0.18);
  padding: 22px 24px 26px;
}

.qxadmin-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.qxadmin-head h1 {
  margin: 0;
  font-size: 20px;
  color: #1f3556;
}

.qxadmin-refresh {
  border: 1px solid rgba(63, 140, 255, 0.4);
  background: rgba(106, 160, 255, 0.12);
  color: #2f6bff;
  border-radius: 10px;
  padding: 7px 16px;
  font-size: 13.5px;
  cursor: pointer;
}

.qxadmin-refresh:disabled {
  cursor: default;
  opacity: 0.6;
}

.qxadmin-error {
  margin: 22px 0;
  padding: 14px 16px;
  border-radius: 12px;
  background: rgba(212, 56, 13, 0.08);
  color: #b4310d;
  font-size: 14px;
}

.qxadmin-tabs {
  display: flex;
  gap: 8px;
  margin: 18px 0 14px;
}

.qxadmin-tabs button {
  border: 1px solid rgba(159, 188, 224, 0.6);
  background: #fff;
  color: #41557a;
  border-radius: 10px;
  padding: 8px 16px;
  font-size: 13.5px;
  cursor: pointer;
}

.qxadmin-tabs button.active {
  background: linear-gradient(135deg, #6aa0ff, #3f8cff);
  border-color: transparent;
  color: #fff;
}

.qxadmin-table-wrap {
  overflow-x: auto;
}

.qxadmin-empty {
  color: #8aa0bf;
  font-size: 14px;
  padding: 24px 0;
  text-align: center;
}

.qxadmin-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
  table-layout: fixed;
}

.qxadmin-col-time {
  width: 156px;
}

.qxadmin-col-type {
  width: 62px;
}

.qxadmin-col-content {
  width: 25%;
}

.qxadmin-col-tool {
  width: 74px;
}

.qxadmin-col-contact {
  width: 108px;
}

.qxadmin-col-account {
  width: 108px;
}

.qxadmin-col-source {
  width: 27%;
}

.qxadmin-table th,
.qxadmin-table td {
  border-bottom: 1px solid rgba(159, 188, 224, 0.35);
  padding: 10px 10px;
  text-align: left;
  vertical-align: top;
}

.qxadmin-table th {
  color: #5a6d8c;
  font-weight: 600;
  white-space: nowrap;
}

.qxadmin-table td.content {
  white-space: pre-wrap;
  word-break: break-word;
  color: #20344f;
}

.qxadmin-cell-scroll {
  max-height: 112px;
  overflow: auto;
  overscroll-behavior: contain;
  padding-right: 4px;
  white-space: pre-wrap;
  word-break: break-word;
  line-height: 1.55;
}

.qxadmin-cell-scroll.compact {
  max-height: 74px;
}

.qxadmin-cell-scroll.url,
.qxadmin-cell-scroll.ua {
  max-height: 74px;
  word-break: break-all;
}

.qxadmin-cell-scroll::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

.qxadmin-cell-scroll::-webkit-scrollbar-thumb {
  background: rgba(135, 166, 190, 0.55);
  border-radius: 999px;
}

.qxadmin-cell-scroll::-webkit-scrollbar-track {
  background: rgba(207, 224, 235, 0.36);
  border-radius: 999px;
}

.qxadmin-table td.nowrap {
  white-space: nowrap;
}

.qxadmin-table td.dim {
  color: #8aa0bf;
}

.qxadmin-table td.ua {
  max-width: 260px;
  word-break: break-all;
}
</style>
