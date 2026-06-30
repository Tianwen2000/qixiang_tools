<script setup>
// 文件说明：定义 AI 助手的 AuthDialog 组件或辅助逻辑。
import { computed, onMounted, ref, watch } from "vue";

import {
  ACCOUNT_PATTERN,
  PASSWORD_PATTERN,
  login as loginRequest,
  register as registerRequest,
  sanitizeAccount,
  sanitizePassword,
} from "./service.js";
import AiRobotLogo from "./AiRobotLogo.vue";

const props = defineProps({
  initialMode: { type: String, default: "login" },
});

const emit = defineEmits(["close", "success"]);

const mode = ref(props.initialMode === "register" ? "register" : "login");
const account = ref("");
const password = ref("");
const submitting = ref(false);
const touched = ref(false);
const banner = ref("");
const showPassword = ref(false);
const accountRef = ref(null);

function togglePassword() {
  showPassword.value = !showPassword.value;
}

const accountValid = computed(() => ACCOUNT_PATTERN.test(account.value));
const passwordValid = computed(() => PASSWORD_PATTERN.test(password.value));
const passwordOk = computed(() => (mode.value === "register" ? passwordValid.value : password.value.length > 0));
const canSubmit = computed(() => accountValid.value && passwordOk.value && !submitting.value);

const title = computed(() => (mode.value === "register" ? "注册账号" : "登录"));
const switchHint = computed(() => (mode.value === "register" ? "已有账号？去登录" : "没有账号？去注册"));

function onAccountInput(event) {
  account.value = sanitizeAccount(event.target.value);
}

function onPasswordInput(event) {
  password.value = sanitizePassword(event.target.value);
}

function switchMode() {
  mode.value = mode.value === "register" ? "login" : "register";
  touched.value = false;
  banner.value = "";
}

async function submit() {
  touched.value = true;
  banner.value = "";
  if (!canSubmit.value) return;
  submitting.value = true;
  try {
    if (mode.value === "register") {
      await registerRequest(account.value, password.value);
    } else {
      await loginRequest(account.value, password.value);
    }
    emit("success");
  } catch (error) {
    banner.value = error?.message || "操作失败，请稍后再试";
  } finally {
    submitting.value = false;
  }
}

watch(
  () => props.initialMode,
  (value) => {
    mode.value = value === "register" ? "register" : "login";
  },
);

onMounted(() => {
  accountRef.value?.focus();
});
</script>

<template>
  <Teleport to="body">
    <div class="qxai-auth-mask" @click.self="emit('close')">
      <section class="qxai-auth-card" role="dialog" aria-modal="true" :aria-label="title">
        <header class="qxai-auth-head">
          <div class="qxai-auth-brand">
            <AiRobotLogo class="qxai-auth-logo" :size="58" />
            <div>
              <h2>{{ title }}</h2>
              <p>登录后即可使用 AI 助手对话</p>
            </div>
          </div>
          <button type="button" class="qxai-auth-close" aria-label="关闭" @click="emit('close')">×</button>
        </header>

        <p v-if="banner" class="qxai-auth-banner">{{ banner }}</p>

        <form class="qxai-auth-form" @submit.prevent="submit">
          <label class="qxai-auth-field">
            <span class="qxai-auth-flabel">账号</span>
            <input
              ref="accountRef"
              :value="account"
              type="text"
              inputmode="numeric"
              autocomplete="username"
              maxlength="11"
              placeholder="11 位纯数字（可用手机号）"
              @input="onAccountInput"
            />
            <small v-if="touched && !accountValid" class="qxai-auth-err">账号必须是 11 位纯数字</small>
          </label>

          <label class="qxai-auth-field">
            <span class="qxai-auth-flabel">密码</span>
            <div class="qxai-auth-pwd">
              <input
                :value="password"
                :type="showPassword ? 'text' : 'password'"
                :autocomplete="mode === 'register' ? 'new-password' : 'current-password'"
                maxlength="16"
                placeholder="8-16 位，至少含字母和数字"
                @input="onPasswordInput"
              />
              <button
                type="button"
                class="qxai-auth-eye"
                :aria-label="showPassword ? '隐藏密码' : '显示密码'"
                :aria-pressed="showPassword"
                @click="togglePassword"
              >
                <svg v-if="showPassword" viewBox="0 0 24 24" width="19" height="19" aria-hidden="true">
                  <path
                    d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7-10-7-10-7Z"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="1.8"
                  />
                  <circle cx="12" cy="12" r="3" fill="none" stroke="currentColor" stroke-width="1.8" />
                </svg>
                <svg v-else viewBox="0 0 24 24" width="19" height="19" aria-hidden="true">
                  <path
                    d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7-10-7-10-7Z"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="1.8"
                  />
                  <circle cx="12" cy="12" r="3" fill="none" stroke="currentColor" stroke-width="1.8" />
                  <line x1="4" y1="20" x2="20" y2="4" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" />
                </svg>
              </button>
            </div>
            <small v-if="mode === 'register' && touched && !passwordValid" class="qxai-auth-err">
              密码需 8-16 位，且至少同时包含字母和数字（区分大小写）
            </small>
            <small v-else-if="touched && !passwordOk" class="qxai-auth-err">请输入密码</small>
          </label>

          <button type="submit" class="qxai-auth-submit" :class="{ active: canSubmit }" :disabled="!canSubmit">
            {{ submitting ? "处理中…" : title }}
          </button>
        </form>

        <footer class="qxai-auth-foot">
          <button type="button" class="qxai-auth-switch" @click="switchMode">{{ switchHint }}</button>
        </footer>
      </section>
    </div>
  </Teleport>
</template>

<style scoped>
.qxai-auth-mask {
  position: fixed;
  inset: 0;
  z-index: 1200;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  background: transparent;
  backdrop-filter: none;
  -webkit-backdrop-filter: none;
}

.qxai-auth-card {
  width: min(420px, 100%);
  border-radius: 20px;
  background: linear-gradient(180deg, #ffffff 0%, #f4f9ff 100%);
  border: 1px solid rgba(117, 169, 255, 0.4);
  box-shadow: 0 26px 60px rgba(34, 70, 124, 0.28);
  padding: 22px 22px 18px;
  animation: qxai-auth-pop 0.22s ease;
}

@keyframes qxai-auth-pop {
  from {
    opacity: 0;
    transform: translateY(12px) scale(0.97);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.qxai-auth-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.qxai-auth-brand {
  display: flex;
  gap: 12px;
  align-items: center;
}

.qxai-auth-logo {
  margin: -7px -4px -7px -7px;
}

.qxai-auth-head h2 {
  margin: 0;
  font-size: 19px;
  color: #1f3556;
}

.qxai-auth-head p {
  margin: 2px 0 0;
  font-size: 12.5px;
  color: #6d7f98;
}

.qxai-auth-close {
  border: none;
  background: transparent;
  color: #8aa0bf;
  font-size: 22px;
  line-height: 1;
  cursor: pointer;
  padding: 2px 6px;
  border-radius: 8px;
}

.qxai-auth-close:hover {
  background: rgba(117, 169, 255, 0.16);
  color: #3f8cff;
}

.qxai-auth-banner {
  margin: 16px 0 0;
  padding: 10px 12px;
  border-radius: 10px;
  background: rgba(212, 56, 13, 0.09);
  color: #b4310d;
  font-size: 13px;
}

.qxai-auth-form {
  margin-top: 18px;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.qxai-auth-field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.qxai-auth-flabel {
  font-size: 13px;
  color: #41557a;
  font-weight: 600;
}

.qxai-auth-field input {
  height: 44px;
  border-radius: 12px;
  border: 1px solid rgba(159, 188, 224, 0.7);
  background: #fff;
  padding: 0 14px;
  font-size: 15px;
  color: #1f3556;
  outline: none;
  transition: border-color 0.18s, box-shadow 0.18s;
}

.qxai-auth-field input:focus {
  border-color: #6aa0ff;
  box-shadow: 0 0 0 3px rgba(106, 160, 255, 0.18);
}

.qxai-auth-pwd {
  position: relative;
}

.qxai-auth-pwd input {
  width: 100%;
  padding-right: 44px;
}

.qxai-auth-eye {
  position: absolute;
  right: 6px;
  top: 50%;
  transform: translateY(-50%);
  width: 34px;
  height: 34px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  background: transparent;
  color: #8aa0bf;
  cursor: pointer;
  border-radius: 8px;
  transition: color 0.16s, background 0.16s;
}

.qxai-auth-eye:hover {
  color: #3f8cff;
  background: rgba(117, 169, 255, 0.14);
}

.qxai-auth-err {
  color: #d4380d;
  font-size: 12px;
}

.qxai-auth-submit {
  margin-top: 4px;
  height: 46px;
  border: none;
  border-radius: 12px;
  font-size: 15.5px;
  font-weight: 600;
  color: #fff;
  cursor: not-allowed;
  background: #b9c6da;
  transition: background 0.2s, box-shadow 0.2s, transform 0.1s;
}

.qxai-auth-submit.active {
  cursor: pointer;
  background: linear-gradient(135deg, #6aa0ff, #3f8cff);
  box-shadow: 0 12px 24px rgba(63, 140, 255, 0.34);
}

.qxai-auth-submit.active:active {
  transform: translateY(1px);
}

.qxai-auth-foot {
  margin-top: 14px;
  text-align: center;
}

.qxai-auth-switch {
  border: none;
  background: transparent;
  color: #3f8cff;
  font-size: 13.5px;
  cursor: pointer;
}

.qxai-auth-switch:hover {
  text-decoration: underline;
}
</style>
