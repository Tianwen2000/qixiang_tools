// 文件说明：定义 AI 助手的 service 组件或辅助逻辑。
// AI 助手 + 登录体系的自包含服务层。
// 刻意不依赖工具侧的 api/client.js、utils/*，只依赖 Vue，便于整体独立维护或迁移。
//
// 登录态：服务端会话 + httpOnly Cookie。前端读不到也不存令牌，
// 仅凭 Cookie 自动随请求发送；是否登录以 /auth/me 为准，本地只缓存用户信息用于即时展示。
import { computed, reactive } from "vue";

// ---------------------------------------------------------------------------
// HTTP：自带 API 基址解析（与站点同域 /api，或 VITE_API_BASE_URL 覆盖）。
// 所有请求带 credentials: "include"，确保会话 Cookie 正常收发。
// ---------------------------------------------------------------------------
function isLocalHost(hostname) {
  return ["localhost", "127.0.0.1", "::1"].includes(hostname) || hostname.endsWith(".localhost");
}

function resolveApiBase() {
  const envBase = (import.meta.env.VITE_API_BASE_URL || "").trim();
  if (typeof window !== "undefined") {
    const { hostname } = window.location;
    if (envBase) {
      if (!/^https?:\/\//i.test(envBase)) {
        return envBase.startsWith("/") ? envBase : `/${envBase}`;
      }
      try {
        const parsed = new URL(envBase);
        // 外部设备访问却配了 localhost，强制回退同域，避免连不上。
        if (!isLocalHost(hostname) && isLocalHost(parsed.hostname)) {
          return "/api";
        }
        return envBase;
      } catch {
        return "/api";
      }
    }
    return "/api";
  }
  // return envBase || "http://127.0.0.1:8000/api"; // 这样容易造成跨域请求失败loclhost和127.0.0.1
  return envBase || "/api";
}

const API_BASE = resolveApiBase();

function apiUrl(path) {
  const normalized = path.startsWith("/") ? path : `/${path}`;
  if (/^https?:\/\//i.test(API_BASE)) {
    return `${API_BASE.replace(/\/$/, "")}${normalized}`;
  }
  return `${API_BASE}${normalized}`;
}

async function parseResponse(response) {
  const payload = await response.json().catch(() => null);
  if (!payload) {
    throw new Error("服务端返回的不是有效 JSON 数据");
  }
  if (!response.ok || payload.code !== 0) {
    throw new Error(payload.message || "请求失败");
  }
  return payload.data;
}

async function apiGet(path) {
  const response = await fetch(apiUrl(path), { credentials: "include" });
  return parseResponse(response);
}

async function apiPost(path, body) {
  const response = await fetch(apiUrl(path), {
    method: "POST",
    credentials: "include",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body || {}),
  });
  return parseResponse(response);
}

// ---------------------------------------------------------------------------
// 本地存储（仅缓存用户信息用于即时展示，不存令牌）。
// ---------------------------------------------------------------------------
function readStore(key, fallback) {
  if (typeof window === "undefined") return fallback;
  try {
    const raw = window.localStorage.getItem(key);
    return raw ? JSON.parse(raw) : fallback;
  } catch {
    return fallback;
  }
}

function writeStore(key, value) {
  if (typeof window === "undefined") return;
  try {
    if (value === null || value === undefined) {
      window.localStorage.removeItem(key);
    } else {
      window.localStorage.setItem(key, JSON.stringify(value));
    }
  } catch {
    /* 忽略配额/序列化异常，不影响使用 */
  }
}

const USER_KEY = "qx-ai-auth-user-v1";
export const AUTH_STATE_CHANGED_EVENT = "qx-ai-auth-state-changed";

// ---------------------------------------------------------------------------
// 校验规则：账号 11 位纯数字；密码 8-16 位、任意合法字符但必须同时含字母和数字（区分大小写）。
// ---------------------------------------------------------------------------
export const ACCOUNT_PATTERN = /^\d{11}$/;
export const PASSWORD_PATTERN = /^(?=.*[A-Za-z])(?=.*\d).{8,16}$/;

export function sanitizeAccount(value) {
  return String(value || "").replace(/\D/g, "").slice(0, 11);
}

export function sanitizePassword(value) {
  // 密码允许任意合法字符，仅做长度上限（16）与换行剔除。
  return String(value || "").replace(/[\r\n]/g, "").slice(0, 16);
}

// ---------------------------------------------------------------------------
// 登录态（响应式单例）。
// ---------------------------------------------------------------------------
const state = reactive({
  user: readStore(USER_KEY, null),
});

function getAccount(user) {
  return user?.account ? String(user.account) : "";
}

let tabBaseAccount = getAccount(state.user);

function emitAuthStateChanged(previousUser, nextUser, external = false) {
  if (typeof window === "undefined") return;
  window.dispatchEvent(
    new CustomEvent(AUTH_STATE_CHANGED_EVENT, {
      detail: {
        previousAccount: getAccount(previousUser),
        account: getAccount(nextUser),
        external,
      },
    }),
  );
}

function setUser(user, options = {}) {
  const previousUser = state.user;
  const nextUser = user || null;
  const nextAccount = getAccount(nextUser);
  const changedFromTabBase = tabBaseAccount !== nextAccount;

  state.user = nextUser;
  if (options.writeStore !== false) {
    writeStore(USER_KEY, state.user);
  }

  if (options.detectExternalChange && changedFromTabBase) {
    emitAuthStateChanged(previousUser, nextUser, true);
    return;
  }

  if (options.updateTabBase !== false) {
    tabBaseAccount = nextAccount;
  }
}

if (typeof window !== "undefined") {
  window.addEventListener("storage", (event) => {
    if (event.key !== USER_KEY) return;
    const previousUser = state.user;
    let nextUser = null;
    try {
      nextUser = event.newValue ? JSON.parse(event.newValue) : null;
    } catch {
      nextUser = null;
    }
    const nextAccount = getAccount(nextUser);
    state.user = nextUser;
    if (tabBaseAccount !== nextAccount) {
      emitAuthStateChanged(previousUser, nextUser, true);
    }
  });
}

export async function register(account, password) {
  const data = await apiPost("/auth/register", { account, password });
  setUser(data?.user || null);
  return data;
}

export async function login(account, password) {
  const data = await apiPost("/auth/login", { account, password });
  setUser(data?.user || null);
  return data;
}

export async function logout() {
  // 通知服务端删除会话并清 Cookie；即便请求失败也清掉本地登录态。
  try {
    await apiPost("/auth/logout", {});
  } catch {
    /* 忽略：本地登录态照常清除 */
  }
  setUser(null);
}

export function clearLocalUser() {
  setUser(null);
}

export async function refreshCurrentUser(options = {}) {
  try {
    const data = await apiGet("/auth/me");
    setUser(data?.user || null, { detectExternalChange: Boolean(options.notifyOnChange) });
    return state.user;
  } catch {
    // 未登录 / 会话失效 / 服务降级：按未登录处理。
    setUser(null, { detectExternalChange: Boolean(options.notifyOnChange) });
    return null;
  }
}

export function useAuth() {
  return {
    user: computed(() => state.user),
    isLoggedIn: computed(() => Boolean(state.user)),
  };
}

// ---------------------------------------------------------------------------
// 对话接口。
// ---------------------------------------------------------------------------
export async function listChatModels() {
  return apiGet("/chat/models");
}

export async function sendChatMessage({ message, model, history = [] }) {
  return apiPost("/chat", { message, model, history });
}
