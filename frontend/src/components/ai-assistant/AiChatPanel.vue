<script setup>
// 文件说明：定义 AI 助手的 AiChatPanel 组件或辅助逻辑。
import { computed, nextTick, onMounted, ref } from "vue";

import AiRobotLogo from "./AiRobotLogo.vue";
import ModelSelect from "./ModelSelect.vue";
import { clearLocalUser, listChatModels, logout, sendChatMessage, useAuth } from "./service.js";

const emit = defineEmits(["close", "need-auth"]);

const { user, isLoggedIn } = useAuth();

const models = ref([]);
const selectedModel = ref("");
const messages = ref([]);
const input = ref("");
const sending = ref(false);
const showProfile = ref(false);
const listRef = ref(null);
const textareaRef = ref(null);

const SUGGESTIONS = ["帮我梳理一份清晰大纲", "把这段话润色得更专业", "用通俗的话解释一个概念"];

const canSend = computed(() => input.value.trim().length > 0 && !sending.value);
const expiresText = computed(() => {
  const value = user.value?.expires_at;
  return value ? String(value).slice(0, 10) : "";
});

function scrollToBottom() {
  nextTick(() => {
    const node = listRef.value;
    if (node) node.scrollTop = node.scrollHeight;
  });
}

async function loadModels() {
  try {
    const data = await listChatModels();
    models.value = data?.models || [];
    selectedModel.value = data?.default || models.value[0]?.id || "";
  } catch {
    models.value = [];
  }
}

function useSuggestion(text) {
  input.value = text;
  textareaRef.value?.focus();
}

async function doSend(text) {
  const userMessageIndex = messages.value.push({ role: "user", content: text }) - 1;
  input.value = "";
  sending.value = true;
  scrollToBottom();

  const history = messages.value
    .filter((item) => item.role === "user" || item.role === "assistant")
    .slice(-10)
    .map((item) => ({ role: item.role, content: item.content }));
  try {
    const data = await sendChatMessage({ message: text, model: selectedModel.value, history });
    messages.value.push({ role: "assistant", content: data?.reply || "（空回复）" });
  } catch (error) {
    const message = error?.message || "发送失败，请稍后再试";
    if (message.includes("登录")) {
      input.value = text;
      if (messages.value[userMessageIndex]?.role === "user" && messages.value[userMessageIndex]?.content === text) {
        messages.value.splice(userMessageIndex, 1);
      }
      clearLoginAndPromptAuth();
      messages.value.push({ role: "system", content: "登录状态已失效，请重新登录后再发送。" });
    } else {
      messages.value.push({ role: "system", content: message });
    }
  } finally {
    sending.value = false;
    scrollToBottom();
  }
}

function clearLoginAndPromptAuth() {
  // 会话失效：仅清本地登录态并唤起登录（服务端会话本就已失效，无需再发退出请求）。
  clearLocalUser();
  emit("need-auth");
}

function send() {
  const text = input.value.trim();
  if (!text || sending.value) return;
  if (!isLoggedIn.value) {
    // 点发送时未登录：保留输入内容，唤起登录/注册。
    emit("need-auth");
    return;
  }
  doSend(text);
}

// 登录成功后由父组件调用：输入框还有内容则自动发出。
function resumeSend() {
  if (isLoggedIn.value && input.value.trim() && !sending.value) {
    doSend(input.value.trim());
  }
}

function onKeydown(event) {
  if (event.key === "Enter" && !event.shiftKey && !event.isComposing) {
    event.preventDefault();
    send();
  }
}

function toggleProfile() {
  showProfile.value = !showProfile.value;
}

async function onLogout() {
  showProfile.value = false;
  await logout();
}

function onLoginFromProfile() {
  showProfile.value = false;
  emit("need-auth");
}

onMounted(loadModels);

defineExpose({ resumeSend });
</script>

<template>
  <Teleport to="body">
    <div class="qxai-chat-mask" @click.self="emit('close')">
      <section class="qxai-chat-panel" role="dialog" aria-modal="true" aria-label="AI 助手">
        <aside class="qxai-chat-side">
          <div class="qxai-chat-side-title">
            <AiRobotLogo class="qxai-chat-mark" :size="28" />
            AI 助手
          </div>
          <div class="qxai-chat-model">
            <span class="qxai-chat-model-label">选择模型</span>
            <ModelSelect v-model="selectedModel" :options="models" placeholder="选择模型" />
          </div>
        </aside>

        <div class="qxai-chat-main">
          <header class="qxai-chat-main-head">
            <div class="qxai-chat-head-left">
              <!-- 账号主页：左上角头像，点击查看账号信息 / 退出登录 -->
              <div class="qxai-profile-wrap">
                <button
                  type="button"
                  class="qxai-profile-btn"
                  :class="{ guest: !isLoggedIn }"
                  :aria-label="isLoggedIn ? '账号主页' : '登录'"
                  @click="toggleProfile"
                >
                  <AiRobotLogo :size="38" />
                </button>

                <template v-if="showProfile">
                  <div class="qxai-profile-backdrop" @click="showProfile = false"></div>
                  <div class="qxai-profile-pop" role="dialog" aria-label="账号主页">
                    <div class="qxai-profile-top">
                      <span class="qxai-profile-bigavatar">
                        <AiRobotLogo :size="48" />
                      </span>
                      <div class="qxai-profile-id">
                        <strong>{{ isLoggedIn ? user.account : "未登录" }}</strong>
                        <small>{{ isLoggedIn ? "已登录" : "登录后可使用 AI 对话" }}</small>
                      </div>
                    </div>

                    <template v-if="isLoggedIn">
                      <dl class="qxai-profile-info">
                        <div><dt>账号</dt><dd>{{ user.account }}</dd></div>
                        <div><dt>登录有效期</dt><dd>30 天</dd></div>
                        <div v-if="expiresText"><dt>有效期至</dt><dd>{{ expiresText }}</dd></div>
                      </dl>
                      <button type="button" class="qxai-profile-logout" @click="onLogout">退出登录</button>
                    </template>
                    <template v-else>
                      <button type="button" class="qxai-profile-login" @click="onLoginFromProfile">登录 / 注册</button>
                    </template>
                  </div>
                </template>
              </div>

              <h2>智能对话</h2>
            </div>
            <button type="button" class="qxai-chat-close" aria-label="关闭" @click="emit('close')">×</button>
          </header>

          <div ref="listRef" class="qxai-chat-list">
            <div v-if="!messages.length" class="qxai-chat-welcome">
              <div class="qxai-chat-wave" aria-hidden="true">👋</div>
              <h3>Hi，我可以帮你做些什么</h3>
              <p>选择左侧模型，输入内容开始对话。</p>
              <div class="qxai-chat-suggestions">
                <button
                  v-for="item in SUGGESTIONS"
                  :key="item"
                  type="button"
                  class="qxai-chat-suggestion"
                  @click="useSuggestion(item)"
                >
                  {{ item }}
                </button>
              </div>
            </div>

            <div
              v-for="(item, index) in messages"
              :key="index"
              class="qxai-chat-row"
              :class="`qxai-chat-row-${item.role}`"
            >
              <div v-if="item.role !== 'system'" class="qxai-chat-avatar" :class="`qxai-chat-avatar-${item.role}`">
                <AiRobotLogo v-if="item.role === 'assistant'" :size="34" />
                <span v-else>我</span>
              </div>
              <div class="qxai-chat-bubble" :class="`qxai-chat-bubble-${item.role}`">{{ item.content }}</div>
            </div>

            <div v-if="sending" class="qxai-chat-row qxai-chat-row-assistant">
              <div class="qxai-chat-avatar qxai-chat-avatar-assistant">
                <AiRobotLogo :size="34" />
              </div>
              <div class="qxai-chat-bubble qxai-chat-bubble-assistant qxai-chat-typing">
                <span></span><span></span><span></span>
              </div>
            </div>
          </div>

          <div class="qxai-chat-input-bar">
            <textarea
              ref="textareaRef"
              v-model="input"
              class="qxai-chat-input"
              rows="1"
              placeholder="请输入想了解的内容，Enter 发送，Shift+Enter 换行"
              @keydown="onKeydown"
            ></textarea>
            <button
              type="button"
              class="qxai-chat-send"
              :class="{ active: canSend }"
              :disabled="!canSend"
              aria-label="发送"
              @click="send"
            >
              <svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true">
                <path d="M3 11.5 21 3l-8.5 18-2.4-7.1L3 11.5Z" fill="currentColor" />
              </svg>
            </button>
          </div>
        </div>
      </section>
    </div>
  </Teleport>
</template>

<style scoped>
.qxai-chat-mask {
  position: fixed;
  inset: 0;
  z-index: 1100;
  display: flex;
  justify-content: flex-end;
  align-items: stretch;
  padding: 24px;
  background: rgba(20, 38, 66, 0.34);
  backdrop-filter: blur(5px);
  -webkit-backdrop-filter: blur(5px);
}

.qxai-chat-panel {
  display: flex;
  width: min(880px, 100%);
  height: 100%;
  border-radius: 22px;
  overflow: hidden;
  background: linear-gradient(180deg, #ffffff 0%, #f3f8ff 100%);
  border: 1px solid rgba(117, 169, 255, 0.38);
  box-shadow: 0 30px 70px rgba(34, 70, 124, 0.3);
  animation: qxai-chat-slide 0.26s ease;
}

@keyframes qxai-chat-slide {
  from {
    opacity: 0;
    transform: translateX(28px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.qxai-chat-side {
  width: 220px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: 18px;
  padding: 20px 16px;
  background: linear-gradient(180deg, rgba(106, 160, 255, 0.14), rgba(117, 169, 255, 0.05));
  border-right: 1px solid rgba(159, 188, 224, 0.4);
}

.qxai-chat-side-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 700;
  color: #1f3556;
}

.qxai-chat-mark {
  margin: -4px -2px -4px -4px;
}

.qxai-chat-model-label {
  display: block;
  font-size: 12.5px;
  color: #5a6d8c;
  margin-bottom: 7px;
}

.qxai-chat-main {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
}

.qxai-chat-main-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 20px;
  border-bottom: 1px solid rgba(159, 188, 224, 0.35);
}

.qxai-chat-head-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.qxai-chat-main-head h2 {
  margin: 0;
  font-size: 16px;
  color: #1f3556;
}

/* 账号主页 */
.qxai-profile-wrap {
  position: relative;
}

.qxai-profile-btn {
  width: 40px;
  height: 40px;
  border-radius: 14px;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
  background: rgba(255, 255, 255, 0.72);
  box-shadow: 0 6px 14px rgba(63, 140, 255, 0.16);
  transition: transform 0.15s;
}

.qxai-profile-btn:hover {
  transform: scale(1.06);
}

.qxai-profile-btn.guest {
  background: rgba(255, 255, 255, 0.58);
  box-shadow: 0 6px 14px rgba(63, 140, 255, 0.1);
}

.qxai-profile-backdrop {
  position: fixed;
  inset: 0;
  z-index: 1;
}

.qxai-profile-pop {
  position: absolute;
  top: 46px;
  left: 0;
  z-index: 2;
  width: 248px;
  padding: 16px;
  border-radius: 14px;
  background: #fff;
  border: 1px solid rgba(117, 169, 255, 0.4);
  box-shadow: 0 18px 40px rgba(34, 70, 124, 0.24);
  animation: qxai-profile-pop 0.16s ease;
}

@keyframes qxai-profile-pop {
  from {
    opacity: 0;
    transform: translateY(-6px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.qxai-profile-top {
  display: flex;
  align-items: center;
  gap: 11px;
  padding-bottom: 12px;
  border-bottom: 1px solid rgba(159, 188, 224, 0.35);
}

.qxai-profile-bigavatar {
  width: 48px;
  height: 48px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: -3px 0 -3px -3px;
}

.qxai-profile-id strong {
  display: block;
  font-size: 15px;
  color: #1f3556;
}

.qxai-profile-id small {
  font-size: 12px;
  color: #6d7f98;
}

.qxai-profile-info {
  margin: 12px 0 14px;
  display: flex;
  flex-direction: column;
  gap: 9px;
}

.qxai-profile-info div {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
}

.qxai-profile-info dt {
  color: #6d7f98;
  margin: 0;
}

.qxai-profile-info dd {
  color: #20344f;
  margin: 0;
  font-weight: 600;
}

.qxai-profile-logout {
  width: 100%;
  height: 40px;
  border: 1px solid rgba(212, 56, 13, 0.4);
  border-radius: 11px;
  background: rgba(212, 56, 13, 0.06);
  color: #c4310d;
  font-size: 14px;
  cursor: pointer;
  transition: background 0.16s;
}

.qxai-profile-logout:hover {
  background: rgba(212, 56, 13, 0.12);
}

.qxai-profile-login {
  width: 100%;
  height: 40px;
  border: none;
  border-radius: 11px;
  margin-top: 12px;
  background: linear-gradient(135deg, #6aa0ff, #3f8cff);
  color: #fff;
  font-size: 14px;
  cursor: pointer;
}

.qxai-chat-close {
  border: none;
  background: transparent;
  color: #8aa0bf;
  font-size: 22px;
  line-height: 1;
  cursor: pointer;
  padding: 2px 8px;
  border-radius: 8px;
}

.qxai-chat-close:hover {
  background: rgba(117, 169, 255, 0.16);
  color: #3f8cff;
}

.qxai-chat-list {
  flex: 1;
  overflow-y: auto;
  padding: 18px 20px;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.qxai-chat-welcome {
  margin: auto;
  text-align: center;
  color: #41557a;
}

.qxai-chat-wave {
  font-size: 34px;
}

.qxai-chat-welcome h3 {
  margin: 10px 0 6px;
  font-size: 18px;
  color: #1f3556;
}

.qxai-chat-welcome p {
  margin: 0 0 16px;
  font-size: 13px;
  color: #6d7f98;
}

.qxai-chat-suggestions {
  display: flex;
  flex-direction: column;
  gap: 10px;
  align-items: center;
}

.qxai-chat-suggestion {
  width: min(320px, 100%);
  border: 1px solid rgba(117, 169, 255, 0.4);
  background: rgba(255, 255, 255, 0.7);
  color: #2f456a;
  border-radius: 12px;
  padding: 11px 14px;
  font-size: 13.5px;
  cursor: pointer;
  transition: background 0.16s, border-color 0.16s;
}

.qxai-chat-suggestion:hover {
  background: rgba(106, 160, 255, 0.14);
  border-color: #6aa0ff;
}

.qxai-chat-row {
  display: flex;
  gap: 10px;
  align-items: flex-start;
}

.qxai-chat-row-user {
  flex-direction: row-reverse;
}

.qxai-chat-row-system {
  justify-content: center;
}

.qxai-chat-avatar {
  flex-shrink: 0;
  width: 32px;
  height: 32px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 700;
  color: #fff;
}

.qxai-chat-avatar-user {
  background: linear-gradient(135deg, #9bbcff, #6aa0ff);
}

.qxai-chat-avatar-assistant {
  background: transparent;
}

.qxai-chat-bubble {
  max-width: 78%;
  padding: 10px 14px;
  border-radius: 14px;
  font-size: 14px;
  line-height: 1.6;
  white-space: pre-wrap;
  word-break: break-word;
}

.qxai-chat-bubble-user {
  background: linear-gradient(135deg, #6aa0ff, #3f8cff);
  color: #fff;
  border-top-right-radius: 4px;
}

.qxai-chat-bubble-assistant {
  background: #eef4ff;
  color: #20344f;
  border-top-left-radius: 4px;
}

.qxai-chat-bubble-system {
  max-width: 90%;
  background: rgba(212, 56, 13, 0.08);
  color: #b4310d;
  font-size: 12.5px;
  text-align: center;
}

.qxai-chat-typing {
  display: inline-flex;
  gap: 5px;
  align-items: center;
}

.qxai-chat-typing span {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #9bb4d8;
  animation: qxai-chat-blink 1.1s infinite ease-in-out;
}

.qxai-chat-typing span:nth-child(2) {
  animation-delay: 0.18s;
}

.qxai-chat-typing span:nth-child(3) {
  animation-delay: 0.36s;
}

@keyframes qxai-chat-blink {
  0%, 80%, 100% {
    opacity: 0.3;
    transform: translateY(0);
  }
  40% {
    opacity: 1;
    transform: translateY(-3px);
  }
}

.qxai-chat-input-bar {
  display: flex;
  gap: 10px;
  align-items: flex-end;
  padding: 14px 18px 18px;
  border-top: 1px solid rgba(159, 188, 224, 0.35);
}

.qxai-chat-input {
  flex: 1;
  min-height: 46px;
  max-height: 140px;
  resize: none;
  border-radius: 14px;
  border: 1px solid rgba(159, 188, 224, 0.7);
  background: #fff;
  padding: 12px 14px;
  font-size: 14.5px;
  line-height: 1.5;
  color: #20344f;
  outline: none;
  transition: border-color 0.18s, box-shadow 0.18s;
}

.qxai-chat-input:focus {
  border-color: #6aa0ff;
  box-shadow: 0 0 0 3px rgba(106, 160, 255, 0.16);
}

.qxai-chat-send {
  flex-shrink: 0;
  width: 46px;
  height: 46px;
  border: none;
  border-radius: 13px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  background: #b9c6da;
  cursor: not-allowed;
  transition: background 0.2s, box-shadow 0.2s, transform 0.1s;
}

.qxai-chat-send.active {
  cursor: pointer;
  background: linear-gradient(135deg, #6aa0ff, #3f8cff);
  box-shadow: 0 10px 20px rgba(63, 140, 255, 0.34);
}

.qxai-chat-send.active:active {
  transform: translateY(1px);
}

@media (max-width: 720px) {
  .qxai-chat-mask {
    padding: 0;
  }

  .qxai-chat-panel {
    width: 100%;
    height: 100%;
    border-radius: 0;
    flex-direction: column;
  }

  .qxai-chat-side {
    width: 100%;
    flex-direction: row;
    align-items: center;
    gap: 12px;
    padding: 12px 16px;
    border-right: none;
    border-bottom: 1px solid rgba(159, 188, 224, 0.4);
  }

  .qxai-chat-model-label {
    display: none;
  }
}
</style>
