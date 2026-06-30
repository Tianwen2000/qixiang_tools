// 文件说明：前端 HTTP 请求基础封装，统一处理接口响应和错误。
function isBrowser() {
  return typeof window !== "undefined";
}

function isLocalHost(hostname) {
  return (
    hostname === "localhost" ||
    hostname === "127.0.0.1" ||
    hostname === "::1" ||
    hostname.endsWith(".localhost")
  );
}

function normalizePath(path) {
  if (!path) return "";
  return path.startsWith("/") ? path : `/${path}`;
}

function isAbsoluteUrl(value) {
  return /^https?:\/\//i.test(value || "");
}

function appendPathToBase(base, path) {
  const normalizedPath = normalizePath(path).slice(1);
  return new URL(normalizedPath, base.endsWith("/") ? base : `${base}/`);
}

function resolveApiBase() {
  const envBase = import.meta.env.VITE_API_BASE_URL?.trim();

  // 1. 浏览器环境
  if (isBrowser()) {
    const { hostname } = window.location;

    // 如果显式配置了环境变量
    if (envBase) {
      // 相对路径，直接用
      if (!isAbsoluteUrl(envBase)) {
        return envBase.startsWith("/") ? envBase : `/${envBase}`;
      }

      // 绝对路径时，做一层“外网访问保护”
      // 当前页面不是本地访问，但 env 却指向 localhost/127.0.0.1，
      // 那手机/外部设备一定访问不到，所以强制回退到同域 /api
      try {
        const parsed = new URL(envBase);
        if (!isLocalHost(hostname) && isLocalHost(parsed.hostname)) {
          return "/api";
        }
        return envBase;
      } catch {
        return "/api";
      }
    }

    // 未配置 env 时，默认走同域代理
    return "/api";
  }

  // 2. 非浏览器环境（SSR / Node）
  if (envBase) {
    return envBase;
  }

  // SSR 默认直连本地后端
  return "http://127.0.0.1:8000/api";
}

const API_BASE = resolveApiBase();

function buildApiUrl(path, params = {}) {
  const normalizedPath = normalizePath(path);

  let url;

  if (isBrowser()) {
    if (isAbsoluteUrl(API_BASE)) {
      // 浏览器下如果 API_BASE 本身就是绝对地址
      url = appendPathToBase(API_BASE, normalizedPath);
    } else {
      // 浏览器下默认走当前站点同域，例如：
      // https://xxxx.trycloudflare.com/api/xxx
      url = new URL(`${API_BASE}${normalizedPath}`, window.location.origin);
    }
  } else {
    // Node / SSR
    if (isAbsoluteUrl(API_BASE)) {
      url = appendPathToBase(API_BASE, normalizedPath);
    } else {
      url = new URL(`http://127.0.0.1:8000${API_BASE}${normalizedPath}`);
    }
  }

  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== "") {
      url.searchParams.set(key, String(value));
    }
  });

  return url;
}

async function parseJsonResponse(response) {
  const payload = await response.json().catch(() => null);
  if (!payload) {
    throw new Error("服务端返回的不是有效 JSON 数据");
  }
  if (!response.ok || payload.code !== 0) {
    throw new Error(payload.message || "请求失败");
  }
  return payload.data;
}

function parseFilename(disposition) {
  if (!disposition) {
    return null;
  }
  const match = disposition.match(/filename="?([^"]+)"?/i);
  return match?.[1] || null;
}

async function request(path, options = {}) {
  const response = await fetch(buildApiUrl(path), { credentials: "include", ...options });
  const contentType = response.headers.get("content-type") || "";

  if (contentType.includes("application/json")) {
    return parseJsonResponse(response);
  }

  if (!response.ok) {
    throw new Error("请求失败");
  }

  const blob = await response.blob();
  return {
    kind: "file",
    blob,
    filename: parseFilename(response.headers.get("content-disposition")) || "结果文件.bin",
    contentType,
  };
}

export async function get(path, params = {}) {
  const url = buildApiUrl(path, params);
  const response = await fetch(url, { credentials: "include" });
  return parseJsonResponse(response);
}

export function post(path, body) {
  return request(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
}

export function postForm(path, formData) {
  return request(path, {
    method: "POST",
    body: formData,
  });
}
