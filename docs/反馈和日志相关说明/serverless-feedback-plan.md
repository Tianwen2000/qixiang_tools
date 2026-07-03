# 琦湘工具集合无数据库反馈方案

> ⚠️ 已被取代：项目引入数据库后，反馈改为**主后端 MySQL 落库** + 独立后台管理页查看（见 [反馈遗留事项整理](./反馈遗留事项整理.md)、[数据库和数据表说明](../数据库和数据表说明.md) 与 [AI 助手与登录系统说明](../技术架构和代码功能说明/AI助手与登录系统说明.md)）。本文保留作历史参考。

## 目标

- 保留当前自定义反馈页 UI
- 不接传统数据库
- 可写入第三方表格，方便直接查看
- 可选同时发通知到 QQ / 钉钉 / 飞书

## 当前已经接好的入口

- 独立反馈页：`/feedback?tool=<slug>&name=<toolName>&from=<toolUrl>`
- 统一打赏页：`/support`
- 前端环境变量：
  - `VITE_FEEDBACK_ENDPOINT`
- 如果没有配置：
  - 前端会把反馈先暂存到浏览器 `localStorage`

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

## 当前项目里的最佳接入方式

1. 保留现有反馈页不动
2. 配置 `VITE_FEEDBACK_ENDPOINT`
3. 远端用 Worker 落到表格
4. 需要时再加通知

这样不会污染主后端，也符合当前无数据库原则。
