<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";

import {
  consumeBackofficeTicket,
  getBackofficeMe,
  listBackofficeFeedback,
  listBackofficeLogs,
  loginBackoffice,
  logoutBackoffice,
} from "../api/backoffice.js";

const route = useRoute();
const router = useRouter();

const user = ref(null);
const account = ref("");
const password = ref("");
const activePanel = ref("feedback");
const feedback = ref([]);
const logs = ref([]);
const loading = ref(true);
const loggingIn = ref(false);
const dataLoading = ref(false);
const gateOpen = ref(false);
const blocked = ref(false);
const errorMsg = ref("");
const animationState = ref("idle");

const BACKOFFICE_GATE_KEY = "qx_backoffice_gate";
let idleTimer = null;
let returnTimer = null;
let attentionTimer = null;
let watchingTimer = null;

const eventLabel = { register: "注册", login: "登录", logout: "退出" };
const feedbackTypeLabel = { bug: "问题反馈", suggestion: "功能建议", content: "内容纠错", praise: "表扬", other: "其他" };

const isLoggedIn = computed(() => Boolean(user.value));
const isAdmin = computed(() => user.value?.role === "admin");
const feedbackCount = computed(() => feedback.value.length);
const logsCount = computed(() => logs.value.length);

function fmt(iso) {
  return iso ? String(iso).replace("T", " ").slice(0, 19) : "";
}

function clearAnimationTimers() {
  window.clearTimeout(idleTimer);
  window.clearTimeout(returnTimer);
  window.clearTimeout(attentionTimer);
  window.clearTimeout(watchingTimer);
  idleTimer = null;
  returnTimer = null;
  attentionTimer = null;
  watchingTimer = null;
}

function activateLoginAnimation() {
  clearAnimationTimers();
  if (animationState.value === "idle" || animationState.value === "returnIdle") {
    animationState.value = "attention";
    attentionTimer = window.setTimeout(() => {
      if (animationState.value === "attention") {
        animationState.value = "lookInput";
      }
    }, 180);
    watchingTimer = window.setTimeout(() => {
      if (animationState.value === "lookInput") {
        animationState.value = "watching";
      }
    }, 420);
  } else {
    animationState.value = "watching";
  }
  idleTimer = window.setTimeout(() => {
    animationState.value = "returnIdle";
    returnTimer = window.setTimeout(() => {
      animationState.value = "idle";
    }, 620);
  }, 3000);
}

function hasValidGate() {
  try {
    const raw = window.localStorage.getItem(BACKOFFICE_GATE_KEY);
    const data = raw ? JSON.parse(raw) : null;
    if (!data?.expiresAt || Number(data.expiresAt) <= Date.now()) {
      window.localStorage.removeItem(BACKOFFICE_GATE_KEY);
      return false;
    }
    return true;
  } catch {
    window.localStorage.removeItem(BACKOFFICE_GATE_KEY);
    return false;
  }
}

function writeGate() {
  window.localStorage.setItem(
    BACKOFFICE_GATE_KEY,
    JSON.stringify({ grantedAt: Date.now(), expiresAt: Date.now() + 2 * 60 * 1000 }),
  );
}

async function loadData() {
  dataLoading.value = true;
  errorMsg.value = "";
  try {
    const requests = [listBackofficeFeedback()];
    if (isAdmin.value) {
      requests.push(listBackofficeLogs());
    }
    const [fb, lg] = await Promise.all(requests);
    feedback.value = fb?.items || [];
    logs.value = isAdmin.value ? lg?.items || [] : [];
    if (!isAdmin.value) {
      activePanel.value = "feedback";
    }
  } catch (error) {
    errorMsg.value = error?.message || "加载失败";
  } finally {
    dataLoading.value = false;
  }
}

async function refreshMe() {
  try {
    const data = await getBackofficeMe();
    user.value = data?.user || null;
    gateOpen.value = true;
    return true;
  } catch {
    user.value = null;
    return false;
  }
}

async function submitLogin() {
  if (loggingIn.value) return;
  loggingIn.value = true;
  errorMsg.value = "";
  try {
    const data = await loginBackoffice(account.value, password.value);
    user.value = data?.user || null;
    account.value = "";
    password.value = "";
    await loadData();
  } catch (error) {
    errorMsg.value = error?.message || "登录失败";
  } finally {
    loggingIn.value = false;
  }
}

async function logout() {
  await logoutBackoffice().catch(() => {});
  user.value = null;
  feedback.value = [];
  logs.value = [];
}

async function boot() {
  loading.value = true;
  errorMsg.value = "";
  const hasSession = await refreshMe();
  if (hasSession) {
    await loadData();
    loading.value = false;
    return;
  }

  const ticket = typeof route.params.ticket === "string" ? route.params.ticket : "";
  if (hasValidGate()) {
    gateOpen.value = true;
    loading.value = false;
    return;
  }

  if (!ticket) {
    blocked.value = true;
    loading.value = false;
    return;
  }

  try {
    await consumeBackofficeTicket(ticket);
    writeGate();
    gateOpen.value = true;
    // ticket 是一次性的，消费后从地址栏移除，避免复制出去继续使用。
    router.replace({ name: "backoffice" });
  } catch (error) {
    blocked.value = true;
    errorMsg.value = error?.message || "后台入口已失效";
  } finally {
    loading.value = false;
  }
}

onMounted(boot);

onBeforeUnmount(() => {
  clearAnimationTimers();
});
</script>

<template>
  <main class="backoffice-page">
    <section v-if="loading" class="backoffice-loading">正在进入后台…</section>

    <section v-else-if="blocked" class="backoffice-login-shell">
      <article class="backoffice-login-card">
        <div class="login-bot" aria-hidden="true">
          <div class="bot-head">
            <span class="bot-eye eye-left"></span>
            <span class="bot-eye eye-right"></span>
            <span class="bot-mouth"></span>
          </div>
          <div class="bot-body"></div>
        </div>
        <p class="backoffice-kicker">QIXIANG ADMIN</p>
        <h1>琦湘工具站后台管理</h1>
        <p>{{ errorMsg || "后台入口无效，请从站点入口重新进入。" }}</p>
      </article>
    </section>

    <section
      v-else-if="!isLoggedIn"
      class="backoffice-login-stage"
      :class="[
        `state-${animationState}`,
        { 'is-watching': animationState === 'watching' || animationState === 'lookInput', 'is-returning': animationState === 'returnIdle' },
      ]"
    >
      <div class="login-grid" aria-hidden="true"></div>
      <span class="login-orb orb-a"></span>
      <span class="login-orb orb-b"></span>
      <span class="login-orb orb-c"></span>
      <span class="floating-cube cube-a"></span>
      <span class="floating-cube cube-b"></span>
      <span class="floating-cube cube-c"></span>

      <article class="backoffice-login-card">
        <div class="login-bot" aria-hidden="true">
          <div class="bot-head">
            <span class="bot-eye eye-left"></span>
            <span class="bot-eye eye-right"></span>
            <span class="bot-mouth"></span>
          </div>
          <div class="bot-body"></div>
        </div>
        <p class="backoffice-kicker">QIXIANG ADMIN</p>
        <h1>琦湘工具站后台管理</h1>
        <form class="backoffice-login-form" @submit.prevent="submitLogin" @mousedown="activateLoginAnimation" @keydown="activateLoginAnimation">
          <input
            v-model="account"
            autocomplete="username"
            aria-label="后台账号"
            placeholder="账号"
            @focus="activateLoginAnimation"
            @input="activateLoginAnimation"
          />
          <input
            v-model="password"
            autocomplete="current-password"
            aria-label="后台密码"
            placeholder="密码"
            type="password"
            @focus="activateLoginAnimation"
            @input="activateLoginAnimation"
          />
          <button type="submit" :disabled="loggingIn">{{ loggingIn ? "登录中…" : "登录" }}</button>
        </form>
        <p v-if="errorMsg" class="backoffice-error">{{ errorMsg }}</p>
      </article>
    </section>

    <section v-else class="backoffice-layout">
      <aside class="backoffice-sidebar">
        <div class="backoffice-account">
          <span class="backoffice-avatar">管</span>
          <div>
            <strong>{{ user.account }}</strong>
            <small>{{ isAdmin ? "管理员" : "观察员" }}</small>
          </div>
        </div>

      <nav class="backoffice-menu" aria-label="后台导航">
        <button type="button" :class="{ active: activePanel === 'feedback' }" @click="activePanel = 'feedback'">
          <span>反馈系统</span>
          <em>{{ feedbackCount }}</em>
        </button>

        <button v-if="isAdmin" type="button" :class="{ active: activePanel === 'logs' }" @click="activePanel = 'logs'">
          <span>账号活动日志</span>
          <em>{{ logsCount }}</em>
        </button>
      </nav>

        <button type="button" class="backoffice-logout" @click="logout">退出后台</button>
      </aside>

      <section class="backoffice-main">
        <header class="backoffice-main-head">
          <div>
            <p class="backoffice-kicker">MANAGEMENT</p>
            <h1>{{ activePanel === "feedback" ? "反馈系统" : "账号活动日志" }}</h1>
          </div>
          <button type="button" class="backoffice-refresh" :disabled="dataLoading" @click="loadData">
            {{ dataLoading ? "刷新中…" : "刷新" }}
          </button>
        </header>

        <p v-if="errorMsg" class="backoffice-error">{{ errorMsg }}</p>

        <div v-show="activePanel === 'feedback'" class="backoffice-table-wrap">
          <p v-if="!dataLoading && !feedback.length" class="backoffice-empty">暂无反馈</p>
          <table v-else class="backoffice-table">
            <thead>
              <tr>
                <th>时间</th><th>类型</th><th>账号</th><th>工具</th><th>内容</th><th>联系方式</th><th>来源页</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in feedback" :key="row.id">
                <td class="nowrap">{{ fmt(row.created_at) }}</td>
                <td><span class="status-tag tag-neutral">{{ feedbackTypeLabel[row.feedback_type] || row.feedback_type || "-" }}</span></td>
                <td>{{ row.account || "" }}</td>
                <td><div class="cell-scroll compact">{{ row.tool_name || row.tool_slug || "-" }}</div></td>
                <td class="wide"><div class="cell-scroll">{{ row.content }}</div></td>
                <td>
                  <div class="cell-scroll compact">
                    {{ row.contact_type ? `${row.contact_type}：${row.contact_value}` : (row.contact_value || "-") }}
                  </div>
                </td>
                <td class="dim"><div class="cell-scroll url">{{ row.submitted_page || "-" }}</div></td>
              </tr>
            </tbody>
          </table>
        </div>

        <div v-show="activePanel === 'logs'" class="backoffice-table-wrap">
          <p v-if="!dataLoading && !logs.length" class="backoffice-empty">暂无日志</p>
          <table v-else class="backoffice-table">
            <thead>
              <tr><th>时间</th><th>事件</th><th>账号</th><th>IP</th><th>UA</th></tr>
            </thead>
            <tbody>
              <tr v-for="row in logs" :key="row.id">
                <td class="nowrap">{{ fmt(row.created_at) }}</td>
                <td><span class="status-tag" :class="`event-${row.event || 'other'}`">{{ eventLabel[row.event] || row.event }}</span></td>
                <td>{{ row.account || "-" }}</td>
                <td class="nowrap"><span class="ip-tag">{{ row.ip || "-" }}</span></td>
                <td class="dim wide"><div class="ua-ellipsis" :title="row.user_agent || '-'">{{ row.user_agent || "-" }}</div></td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>
    </section>
  </main>
</template>

<style scoped>
.backoffice-page {
  min-height: 100vh;
  background: #f6f9ff;
  color: #172033;
}

.backoffice-loading,
.backoffice-login-shell {
  min-height: 100vh;
  display: grid;
  place-items: center;
  padding: 24px;
  background:
    radial-gradient(circle at 18% 18%, rgba(118, 177, 255, 0.28), transparent 28%),
    radial-gradient(circle at 82% 16%, rgba(181, 150, 255, 0.2), transparent 30%),
    linear-gradient(135deg, #f9fcff 0%, #edf7ff 50%, #f8f4ff 100%);
}

.backoffice-login-stage {
  position: relative;
  min-height: 100vh;
  display: grid;
  place-items: center;
  padding: 32px;
  overflow: hidden;
  background:
    radial-gradient(circle at 16% 18%, rgba(106, 178, 255, 0.3), transparent 27%),
    radial-gradient(circle at 82% 18%, rgba(177, 142, 255, 0.22), transparent 30%),
    radial-gradient(circle at 50% 88%, rgba(83, 215, 255, 0.18), transparent 34%),
    linear-gradient(135deg, #f9fcff 0%, #eef7ff 48%, #f8f4ff 100%);
}

.login-grid {
  position: absolute;
  inset: 0;
  opacity: 0.26;
  background-image:
    linear-gradient(rgba(92, 132, 190, 0.16) 1px, transparent 1px),
    linear-gradient(90deg, rgba(92, 132, 190, 0.16) 1px, transparent 1px);
  background-size: 36px 36px;
  mask-image: radial-gradient(circle at center, rgba(0, 0, 0, 0.82), transparent 72%);
}

.login-orb,
.floating-cube {
  position: absolute;
  pointer-events: none;
}

.orb-a {
  width: 210px;
  height: 210px;
  left: 14%;
  top: 20%;
  border-radius: 999px;
  background: rgba(105, 171, 255, 0.2);
  filter: blur(6px);
}

.orb-b {
  width: 260px;
  height: 260px;
  right: 12%;
  bottom: 12%;
  border-radius: 999px;
  background: rgba(167, 133, 255, 0.16);
  filter: blur(8px);
}

.orb-c {
  width: 140px;
  height: 140px;
  right: 24%;
  top: 18%;
  border-radius: 999px;
  background: rgba(82, 221, 255, 0.14);
  filter: blur(5px);
}

.floating-cube {
  width: 44px;
  height: 44px;
  border-radius: 14px;
  border: 1px solid rgba(255, 255, 255, 0.66);
  background: rgba(255, 255, 255, 0.34);
  box-shadow: 0 18px 42px rgba(88, 119, 168, 0.12);
}

.cube-a {
  left: 24%;
  top: 24%;
}

.cube-b {
  right: 24%;
  top: 28%;
  width: 34px;
  height: 34px;
  animation-delay: 0.7s;
}

.cube-c {
  width: 18px;
  height: 18px;
  left: 28%;
  bottom: 20%;
  animation-delay: 1.2s;
}

.backoffice-login-card {
  position: relative;
  z-index: 1;
  width: min(420px, calc(100vw - 32px));
  padding: 34px;
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.65);
  border: 1px solid rgba(255, 255, 255, 0.62);
  box-shadow: 0 28px 80px rgba(74, 92, 133, 0.18);
  backdrop-filter: blur(18px);
  -webkit-backdrop-filter: blur(18px);
  animation: login-card-in 0.48s ease both;
}

.login-bot {
  position: absolute;
  right: 24px;
  top: 20px;
  width: 54px;
  height: 62px;
  display: grid;
  grid-template-rows: 38px 18px;
  place-items: center;
  opacity: 0.94;
  transform: translate3d(0, 0, 0) scale(1);
  transform-origin: 50% 78%;
  transition: transform 0.46s cubic-bezier(0.22, 1, 0.36, 1), filter 0.28s ease, opacity 0.28s ease;
  animation: bot-idle-float 4s ease-in-out infinite;
}

.bot-head {
  position: relative;
  width: 52px;
  height: 38px;
  border-radius: 17px;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.96), rgba(211, 222, 242, 0.92));
  box-shadow: 0 13px 24px rgba(72, 102, 154, 0.18), inset 0 1px 0 rgba(255, 255, 255, 0.95);
}

.bot-head::before {
  content: "";
  position: absolute;
  left: 7px;
  right: 7px;
  top: 9px;
  height: 19px;
  border-radius: 10px;
  background: #071a2f;
  box-shadow: inset 0 0 9px rgba(50, 226, 255, 0.18);
}

.bot-head::after {
  content: "";
  position: absolute;
  left: 50%;
  top: -5px;
  width: 24px;
  height: 7px;
  border-radius: 999px;
  background: rgba(66, 206, 255, 0.45);
  transform: translateX(-50%);
  box-shadow: 0 0 9px rgba(66, 206, 255, 0.28);
}

.bot-eye {
  position: absolute;
  z-index: 1;
  top: 18px;
  width: 8px;
  height: 5px;
  border-radius: 999px;
  background: #31e7ff;
  box-shadow: 0 0 8px rgba(49, 231, 255, 0.88);
  transform: translate(0, 0) scaleY(1);
  animation: bot-blink 4.6s ease-in-out infinite;
  transition: transform 0.42s cubic-bezier(0.22, 1, 0.36, 1), width 0.24s ease, height 0.24s ease;
}

.eye-left {
  left: 17px;
}

.eye-right {
  right: 17px;
}

.bot-mouth {
  position: absolute;
  z-index: 1;
  left: 50%;
  top: 25px;
  width: 8px;
  height: 3px;
  border-radius: 999px;
  background: rgba(49, 231, 255, 0.85);
  transform: translateX(-50%);
  box-shadow: 0 0 6px rgba(49, 231, 255, 0.4);
}

.bot-body {
  width: 31px;
  height: 24px;
  margin-top: 2px;
  border-radius: 14px 14px 11px 11px;
  background: linear-gradient(180deg, rgba(249, 252, 255, 0.96), rgba(190, 205, 227, 0.92));
  box-shadow: 0 13px 22px rgba(72, 102, 154, 0.14), inset 0 1px 0 rgba(255, 255, 255, 0.88);
}

.bot-body::before {
  content: "";
  display: block;
  width: 11px;
  height: 11px;
  margin: 5px auto 0;
  border-radius: 999px;
  background: radial-gradient(circle, #dffaff 0 28%, #31e7ff 32% 62%, #4693ff 66%);
  box-shadow: 0 0 12px rgba(49, 231, 255, 0.48);
}

.state-attention .login-bot {
  animation: none;
  filter: brightness(1.05) saturate(1.08);
  transform: translate3d(-3px, 2px, 0) rotate(-2deg) scale(1.03);
}

.state-attention .bot-eye {
  width: 9px;
  height: 7px;
  transform: translate(-2px, 1px) scale(1.08);
  animation: none;
}

.state-lookInput .login-bot,
.state-watching .login-bot {
  animation: none;
  filter: brightness(1.04) saturate(1.06);
  transform: translate3d(-7px, 4px, 0) rotate(-4deg) skewY(1deg) scale(1.03);
}

.state-lookInput .bot-eye,
.state-watching .bot-eye {
  transform: translate(-5px, 2px);
  animation: none;
}

.state-returnIdle .login-bot {
  animation: none;
  transform: translate3d(0, 0, 0) rotate(0) scale(1);
}

.state-returnIdle .bot-eye {
  transform: translate(0, 0);
}

.backoffice-kicker {
  margin: 0 0 8px;
  font-size: 12px;
  letter-spacing: 0;
  color: #5f72a2;
  font-weight: 700;
}

.backoffice-login-card h1,
.backoffice-main-head h1 {
  margin: 0;
  color: #14223b;
  font-size: 26px;
  line-height: 1.25;
}

.backoffice-login-card p {
  color: #65758f;
}

.backoffice-login-form {
  display: grid;
  gap: 14px;
  margin-top: 28px;
}

.backoffice-login-form input {
  height: 52px;
  border-radius: 14px;
  border: 1px solid rgba(124, 150, 196, 0.42);
  background: rgba(255, 255, 255, 0.58);
  padding: 0 16px;
  font-size: 15px;
  color: #172033;
  outline: none;
  transition: border-color 0.18s ease, box-shadow 0.18s ease, background 0.18s ease;
}

.backoffice-login-form input::placeholder {
  color: #8a9ab3;
}

.backoffice-login-form input:focus {
  border-color: #6f7cff;
  background: rgba(255, 255, 255, 0.82);
  box-shadow: 0 0 0 4px rgba(113, 124, 255, 0.14), 0 0 22px rgba(63, 139, 255, 0.14);
}

.backoffice-login-form button,
.backoffice-refresh {
  height: 48px;
  border: none;
  border-radius: 14px;
  background: linear-gradient(135deg, #4d8cff, #7a5cff);
  color: white;
  font-weight: 700;
  cursor: pointer;
  box-shadow: 0 14px 28px rgba(60, 91, 255, 0.24);
  transition: transform 0.18s ease, box-shadow 0.18s ease, filter 0.18s ease;
}

.backoffice-login-form button:hover:not(:disabled),
.backoffice-refresh:hover:not(:disabled) {
  transform: translateY(-1px);
  filter: brightness(1.03);
  box-shadow: 0 18px 34px rgba(60, 91, 255, 0.3);
}

.backoffice-login-form button:disabled,
.backoffice-refresh:disabled {
  opacity: 0.58;
  cursor: default;
}

@keyframes login-card-in {
  from {
    opacity: 0;
    transform: translateY(16px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes bot-idle-float {
  0%,
  100% {
    transform: translate3d(0, 0, 0);
  }
  50% {
    transform: translate3d(0, -5px, 0);
  }
}

@keyframes bot-blink {
  0%,
  88%,
  100% {
    transform: translate(0, 0) scaleY(1);
  }
  92% {
    transform: translate(0, 0) scaleY(0.18);
  }
}

.backoffice-error {
  margin: 14px 0 0;
  padding: 10px 12px;
  border-radius: 12px;
  background: rgba(255, 241, 239, 0.86);
  color: #b72d17;
  border: 1px solid rgba(255, 180, 168, 0.42);
}

.backoffice-layout {
  min-height: 100vh;
  display: grid;
  grid-template-columns: 280px minmax(0, 1fr);
  background: #f6f9ff;
}

.backoffice-sidebar {
  position: sticky;
  top: 0;
  min-height: 100vh;
  background: linear-gradient(180deg, #0f172a 0%, #111827 100%);
  color: #e9eef6;
  padding: 24px 18px;
  display: flex;
  flex-direction: column;
  gap: 20px;
  border-right: 1px solid rgba(255, 255, 255, 0.08);
  box-shadow: 14px 0 42px rgba(15, 23, 42, 0.08);
}

.backoffice-account {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 15px;
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.075);
  border: 1px solid rgba(255, 255, 255, 0.08);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.06);
}

.backoffice-avatar {
  width: 42px;
  height: 42px;
  border-radius: 14px;
  display: grid;
  place-items: center;
  background: linear-gradient(135deg, #4d8cff, #7a5cff);
  font-weight: 800;
  box-shadow: 0 14px 30px rgba(50, 95, 255, 0.24);
}

.backoffice-account strong,
.backoffice-account small {
  display: block;
}

.backoffice-account small {
  margin-top: 3px;
  color: #9aa8bd;
}

.backoffice-menu {
  display: grid;
  gap: 8px;
}

.backoffice-menu button,
.backoffice-logout {
  border: none;
  border-radius: 14px;
  min-height: 46px;
  padding: 0 13px;
  cursor: pointer;
  transition: background 0.18s ease, color 0.18s ease, transform 0.18s ease, box-shadow 0.18s ease;
}

.backoffice-menu button {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: transparent;
  color: #cdd7e6;
  text-align: left;
}

.backoffice-menu button span {
  display: inline-flex;
  align-items: center;
}



.backoffice-menu button:hover {
  background: rgba(96, 165, 250, 0.12);
  color: #fff;
}

.backoffice-menu button.active {
  background: rgba(59, 130, 246, 0.2);
  color: #fff;
  box-shadow: inset 0 0 0 1px rgba(147, 197, 253, 0.16);
}

.backoffice-menu em {
  font-style: normal;
  min-width: 28px;
  height: 22px;
  display: inline-grid;
  place-items: center;
  padding: 0 8px;
  border-radius: 999px;
  background: rgba(148, 163, 184, 0.14);
  color: #cbd5e1;
  font-size: 12px;
}

.backoffice-logout {
  margin-top: auto;
  background: rgba(255, 255, 255, 0.07);
  color: #ffc4bd;
}

.backoffice-logout:hover {
  background: rgba(248, 113, 113, 0.14);
  color: #fff;
}

.backoffice-main {
  min-width: 0;
  padding: 34px;
  background:
    radial-gradient(circle at 80% 0%, rgba(124, 169, 255, 0.13), transparent 28%),
    #f6f9ff;
}

.backoffice-main-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 18px;
  margin-bottom: 22px;
}

.backoffice-refresh {
  width: auto;
  min-width: 92px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0 18px;
  border-radius: 12px;
}

.backoffice-table-wrap {
  overflow: auto;
  border-radius: 18px;
  background: #fff;
  border: 1px solid #e2eaf5;
  box-shadow: 0 18px 50px rgba(37, 49, 68, 0.07);
}

.backoffice-empty {
  margin: 0;
  padding: 56px 24px;
  text-align: center;
  color: #71819b;
  background:
    radial-gradient(circle at 50% 34%, rgba(94, 154, 255, 0.1), transparent 26%),
    #fff;
}

.backoffice-table {
  width: 100%;
  border-collapse: collapse;
  table-layout: fixed;
  min-width: 980px;
  font-size: 13px;
}

.backoffice-table th,
.backoffice-table td {
  padding: 15px 14px;
  border-bottom: 1px solid #e3ebf4;
  text-align: left;
  vertical-align: top;
}

.backoffice-table th {
  color: #64748b;
  font-weight: 700;
  background: #f8fbff;
  position: sticky;
  top: 0;
  z-index: 1;
}

.backoffice-table tbody tr {
  transition: background 0.16s ease;
}

.backoffice-table tbody tr:hover {
  background: #f8fbff;
}

.backoffice-table .wide {
  width: 28%;
}

.nowrap {
  white-space: nowrap;
}

.dim {
  color: #65758d;
}

.status-tag,
.ip-tag {
  display: inline-flex;
  align-items: center;
  max-width: 100%;
  min-height: 26px;
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 700;
  line-height: 1.2;
  white-space: nowrap;
}

.status-tag {
  color: #2563eb;
  background: #eff6ff;
  border: 1px solid #bfdbfe;
}

.tag-neutral {
  color: #475569;
  background: #f8fafc;
  border-color: #e2e8f0;
}

.event-login {
  color: #047857;
  background: #ecfdf5;
  border-color: #a7f3d0;
}

.event-register {
  color: #1d4ed8;
  background: #eff6ff;
  border-color: #bfdbfe;
}

.event-logout {
  color: #b45309;
  background: #fffbeb;
  border-color: #fde68a;
}

.ip-tag {
  color: #475569;
  background: #f1f5f9;
  border: 1px solid #e2e8f0;
}

.ua-ellipsis {
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.cell-scroll {
  max-height: 112px;
  overflow: auto;
  white-space: pre-wrap;
  word-break: break-word;
  line-height: 1.55;
  padding-right: 4px;
}

.cell-scroll.compact,
.cell-scroll.url,
.cell-scroll.ua {
  max-height: 78px;
  word-break: break-all;
}

@media (max-width: 760px) {
  .backoffice-login-stage {
    padding: 16px;
  }

  .backoffice-login-card {
    padding: 28px 22px;
    border-radius: 22px;
  }

  .backoffice-layout {
    grid-template-columns: 1fr;
  }

  .backoffice-sidebar {
    position: static;
    min-height: auto;
    padding: 16px;
    gap: 14px;
  }

  .backoffice-menu {
    display: flex;
    overflow-x: auto;
    padding-bottom: 2px;
  }

  .backoffice-menu button {
    min-width: max-content;
    gap: 12px;
  }

  .backoffice-logout {
    margin-top: 0;
  }

  .backoffice-main {
    padding: 20px 16px 28px;
  }

  .backoffice-main-head {
    align-items: flex-start;
    flex-direction: column;
  }

  .backoffice-refresh {
    width: 100%;
  }
}
</style>
