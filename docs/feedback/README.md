# 反馈系统整理

这里整理项目里和反馈相关的实现与现状。

> 现状（已更新）：反馈**已落库主后端 MySQL**，并配有 root 管理员只读查看页。
> 完整说明见 [AI 助手与登录系统说明](../AI助手与登录系统说明.md) 第 9 节。

## 当前实现

- 独立反馈页：`/feedback`
- 独立打赏页：`/support`
- 提交流程：前端 `frontend/src/api/feedback.js` → `POST /api/feedback` → 落库 `feedback` 表
- 匿名即可提交；若已登录则记录提交者账号
- 提交失败时本地浏览器暂存兜底，不丢内容
- 管理员查看：`ADMIN_ACCOUNTS` 配置的账号登录后，AI 面板出现「反馈系统」入口，新标签页打开 `/admin` 只读查看反馈与账号活动日志

## 实现位置

### 前端

- 反馈页：`frontend/src/pages/FeedbackPage.vue`
- 提交 API：`frontend/src/api/feedback.js`
- 管理查看页：`frontend/src/components/ai-assistant/AdminConsole.vue`（路由 `/admin`）

### 后端

- 提交：`backend/app/api/routes/feedback.py` + `backend/app/services/feedback_service.py`
- 查看：`backend/app/api/routes/admin.py`（管理员鉴权）
- 表：`feedback`（反馈）、`logs`（账号活动日志）

## 历史方案（已被取代）

早期为「保持无数据库」设计过一套 **serverless / Worker 落表** 方案，见 [serverless-feedback-plan](./serverless-feedback-plan.md) 与 [反馈遗留事项整理](./反馈遗留事项整理.md)（保留作参考）。项目引入数据库后，已改为主后端落库，更简单可靠。

## 仍可后续补强（非必须）

- 提交通知（邮箱 / 钉钉 / 飞书机器人）
- 反刷 / 限流（Turnstile 等）
