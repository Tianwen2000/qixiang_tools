// 文件说明：封装用户反馈提交接口。
import { post } from "./client.js";
import { readJsonCache, writeJsonCache } from "../utils/page-cache.js";

const FEEDBACK_DRAFT_STORAGE_KEY = "tw-feedback-outbox-v1";

function saveLocalDraft(payload) {
  const drafts = readJsonCache(FEEDBACK_DRAFT_STORAGE_KEY, []);
  drafts.unshift({
    id: `local-${Date.now()}`,
    submittedAt: new Date().toISOString(),
    ...payload,
  });
  writeJsonCache(FEEDBACK_DRAFT_STORAGE_KEY, drafts);
}

export async function submitFeedback(payload) {
  // 直接提交到主后端落库（MySQL）。失败则暂存到本浏览器，避免内容丢失。
  try {
    const data = await post("/feedback", payload);
    return {
      mode: "remote",
      message: "反馈已提交，感谢你的反馈。",
      id: data?.id ?? null,
    };
  } catch (error) {
    saveLocalDraft(payload);
    return {
      mode: "local",
      message: `提交未成功（${error?.message || "网络异常"}），已先暂存到当前浏览器，联网后可重试。`,
    };
  }
}

export function getFeedbackDrafts() {
  return readJsonCache(FEEDBACK_DRAFT_STORAGE_KEY, []);
}
