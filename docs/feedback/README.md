# 反馈系统整理

这里整理项目里和反馈相关的实现与现状。

> 现状（已更新）：反馈**已落库主后端 MySQL**，并迁移到独立后台管理系统只读查看。
> 完整说明见 [AI 助手与登录系统说明](../AI助手与登录系统说明.md) 第 9 节。

## 当前实现

- 独立反馈页：`/feedback`
- 独立打赏页：`/support`
- 提交流程：前端 `frontend/src/api/feedback.js` → `POST /api/feedback` → 落库 `feedback` 表
- 匿名即可提交；若已登录则记录提交者账号
- 提交失败时本地浏览器暂存兜底，不丢内容
- 后台查看：从站点品牌热区进入独立后台，使用后台专用账号登录后只读查看反馈与账号活动日志

## 实现位置

### 前端

- 反馈页：`frontend/src/pages/FeedbackPage.vue`
- 提交 API：`frontend/src/api/feedback.js`
- 后台管理页：`frontend/src/pages/BackofficePage.vue`
- 后台入口 API：`frontend/src/api/backoffice.js`

### 后端

- 提交：`backend/app/api/routes/feedback.py` + `backend/app/services/feedback_service.py`
- 后台查看：`backend/app/api/routes/backoffice.py` + `backend/app/services/backoffice_service.py`
- 表：`feedback`（反馈）、`logs`（账号活动日志）

## 历史方案（已被取代）

早期为「保持无数据库」设计过一套 **serverless / Worker 落表** 方案，见 [serverless-feedback-plan](./serverless-feedback-plan.md) 与 [反馈遗留事项整理](./反馈遗留事项整理.md)（保留作参考）。项目引入数据库后，已改为主后端落库，更简单可靠。

## 仍可后续补强（非必须）

- 提交通知（邮箱 / 钉钉 / 飞书机器人）
- 反刷 / 限流（Turnstile 等）
