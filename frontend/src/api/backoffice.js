// 文件说明：封装独立后台入口、登录、反馈和日志接口。
import { get, post } from "./client.js";

export function getBackofficeChallenge() {
  return get("/backoffice/challenge");
}

export function requestBackofficeEntry(answer) {
  return post("/backoffice/entry", { answer });
}

export function consumeBackofficeTicket(ticket) {
  return post("/backoffice/entry/consume", { ticket });
}

export function loginBackoffice(account, password) {
  return post("/backoffice/login", { account, password });
}

export function getBackofficeMe() {
  return get("/backoffice/me");
}

export function logoutBackoffice() {
  return post("/backoffice/logout", {});
}

export function listBackofficeFeedback() {
  return get("/backoffice/feedback");
}

export function listBackofficeLogs() {
  return get("/backoffice/logs");
}
