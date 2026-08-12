# 琦湘工具集合无数据库反馈方案（历史）

> ⚠️ 已被取代：项目引入数据库后，反馈改为**主后端 MySQL 落库** + 独立后台管理页查看（见 [反馈遗留事项整理](./反馈遗留事项整理.md)、[数据库和数据表说明](../数据库和数据表说明.md) 与 [AI 助手与登录系统说明](../技术架构和代码功能说明/AI助手与登录系统说明.md)）。本文保留作历史参考。

## 当时的目标

- 保留当前自定义反馈页 UI
- 不接传统数据库
- 可写入第三方表格，方便直接查看
- 可选同时发通知到 QQ / 钉钉 / 飞书

## 当时已有的入口

- 独立反馈页：`/feedback?tool=<slug>&name=<toolName>&from=<toolUrl>`
- 统一打赏页：`/support`
- 历史方案曾计划通过 `VITE_FEEDBACK_ENDPOINT` 指向外部 Worker；当前提交模块 `frontend/src/api/feedback.js` 不再读取该变量。`FeedbackPage.vue` 的 `deliveryHint` 仍用它生成旧 Serverless 提示，但这段提示不改变实际提交地址。
- 当前 `frontend/src/api/feedback.js` 固定提交 `POST /api/feedback`，请求失败时才暂存到浏览器 `localStorage`。

## 推荐落地方式

### 方案 A：Cloudflare Workers + Google Sheets / Airtable

推荐原因：

- 轻量
- 无数据库
- 容易查看反馈列表
- 不需要自建后台

流程：

1. 前端反馈页提交表单
2. 请求发送到 Cloudflare Worker
3. Worker 负责校验、限流、脱敏
4. 写入 Google Sheets 或 Airtable
5. 可选发一条通知

### 方案 B：Cloudflare Workers + 飞书多维表格

优点：

- 中文团队使用顺手
- 结构化字段管理友好

缺点：

- 初次配置一般会比 Google Sheets / Airtable 稍复杂

### 方案 C：只做通知，不做落表

优点：

- 上线最快

缺点：

- 后续查看历史反馈不方便

## 建议字段

| 字段 | 说明 |
| --- | --- |
| `id` | 唯一反馈 ID |
| `submitted_at` | 提交时间 |
| `tool_slug` | 工具 slug |
| `tool_name` | 工具名称 |
| `tool_url` | 工具地址 |
| `feedback_type` | `bug / suggestion / content / other` |
| `content` | 反馈正文 |
| `contact_type` | `email / qq / wechat` |
| `contact_value` | 联系方式 |
| `submitted_page` | 页面 URL |
| `user_agent` | 浏览器标识 |
| `source` | 固定写项目来源 |
| `status` | 默认 `new` |

## 前端提交结构

```json
{
  "toolSlug": "text-statistics",
  "toolName": "文本统计",
  "toolUrl": "https://example.com/tool/text-statistics",
  "feedbackType": "bug",
  "content": "移动端点击后无响应",
  "contactType": "qq",
  "contactValue": "123456789",
  "submittedPage": "https://example.com/feedback?tool=text-statistics",
  "userAgent": "Mozilla/5.0 ..."
}
```

## Worker 接口建议

### `POST /feedback/submit`

成功返回：

```json
{
  "ok": true,
  "id": "fb_20260413_xxxx",
  "message": "反馈已提交，我们会尽快查看。"
}
```

失败返回：

```json
{
  "ok": false,
  "message": "反馈提交失败，请稍后再试。"
}
```

## 推荐防护

- `content` 必填
- 联系方式必填
- 白名单校验 `feedbackType`
- 白名单校验 `contactType`
- 同一 IP 做轻量限流
- 可接 Turnstile

## 当前实现

本文前面的 Worker、第三方表格和 `VITE_FEEDBACK_ENDPOINT` 内容只用于保留历史设计思路，不能作为当前部署步骤。反馈页目前仍有一段受该变量控制的旧提示文字，但提交逻辑不会因此切换到 Worker。

当前链路为：

1. 反馈页调用 `POST /api/feedback`。
2. 主后端把反馈写入 MySQL 的 `feedback` 表。
3. 独立后台通过 `GET /api/backoffice/feedback` 查看最近反馈。
4. 主后端请求失败时，前端把草稿暂存在当前浏览器，避免内容丢失。

如果以后重新采用 Worker 或第三方表格，需要新增明确的前端分流和服务端同步逻辑，不能只配置一个现已不使用的环境变量。
