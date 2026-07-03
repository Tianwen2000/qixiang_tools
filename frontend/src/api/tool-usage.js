// 文件说明：封装工具使用行为日志的前端静默上报。
const TOOL_USAGE_DEVICE_ID_KEY = "tw-tool-usage-device-id-v1";

function getDeviceId() {
  if (typeof window === "undefined") {
    return "";
  }
  try {
    const existing = window.localStorage.getItem(TOOL_USAGE_DEVICE_ID_KEY);
    if (existing) {
      return existing;
    }
    const randomPart =
      typeof crypto !== "undefined" && crypto.randomUUID
        ? crypto.randomUUID()
        : `${Date.now()}-${Math.random().toString(16).slice(2)}`;
    const deviceId = `web-${randomPart}`;
    window.localStorage.setItem(TOOL_USAGE_DEVICE_ID_KEY, deviceId);
    return deviceId;
  } catch {
    return "";
  }
}

function apiUrl() {
  if (typeof window === "undefined") {
    return "/api/tool-usage-logs";
  }
  return new URL("/api/tool-usage-logs", window.location.origin).toString();
}

function cleanNumber(value) {
  const number = Number(value || 0);
  return Number.isFinite(number) && number > 0 ? Math.round(number) : 0;
}

function normalizePayload(data = {}) {
  return {
    toolId: data.toolId || "",
    toolName: data.toolName || "",
    category: data.category || "",
    action: data.action || "",
    success: typeof data.success === "boolean" ? data.success : null,
    durationMs: cleanNumber(data.durationMs),
    inputLength: cleanNumber(data.inputLength),
    outputLength: cleanNumber(data.outputLength),
    errorCode: data.errorCode || "",
    errorMessage: data.errorMessage ? String(data.errorMessage).slice(0, 512) : "",
    sourcePage: data.sourcePage || (typeof window === "undefined" ? "" : `${window.location.pathname}${window.location.search}`),
    deviceId: data.deviceId || getDeviceId(),
  };
}

export function reportToolUsageLog(data = {}) {
  if (typeof window === "undefined") {
    return;
  }
  const payload = normalizePayload(data);
  const body = JSON.stringify(payload);
  try {
    if (navigator.sendBeacon) {
      const blob = new Blob([body], { type: "application/json" });
      if (navigator.sendBeacon(apiUrl(), blob)) {
        return;
      }
    }
  } catch {
    // 上报失败不能影响工具使用。
  }
  fetch(apiUrl(), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body,
    keepalive: true,
  }).catch(() => {});
}

export function buildToolUsageBase(tool) {
  return {
    toolId: tool?.slug || "",
    toolName: tool?.name || "",
    category: tool?.category || "",
  };
}
