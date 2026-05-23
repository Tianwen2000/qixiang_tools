import { readJsonCache, writeJsonCache } from "../utils/page-cache.js";

const FEEDBACK_DRAFT_STORAGE_KEY = "tw-feedback-outbox-v1";

function getFeedbackEndpoint() {
  return (import.meta.env.VITE_FEEDBACK_ENDPOINT || "").trim();
}

export async function submitFeedback(payload) {
  const endpoint = getFeedbackEndpoint();

  if (!endpoint) {
    const drafts = readJsonCache(FEEDBACK_DRAFT_STORAGE_KEY, []);
    drafts.unshift({
      id: `local-${Date.now()}`,
      submittedAt: new Date().toISOString(),
      ...payload,
    });
    writeJsonCache(FEEDBACK_DRAFT_STORAGE_KEY, drafts);
    return {
      mode: "local",
      message: "当前未配置线上反馈接口，已先保存在当前浏览器。",
    };
  }

  const response = await fetch(endpoint, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  const data = await response.json().catch(() => null);
  if (!response.ok || (data && data.ok === false)) {
    throw new Error(data?.message || "反馈提交失败，请稍后再试。");
  }

  return {
    mode: "remote",
    message: data?.message || "反馈已提交，我们会尽快查看。",
    id: data?.id || null,
  };
}

export function getFeedbackDrafts() {
  return readJsonCache(FEEDBACK_DRAFT_STORAGE_KEY, []);
}
