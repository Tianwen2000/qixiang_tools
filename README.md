# 琦湘工具集合

一个基于 `FastAPI + Vue 3 + Vite` 的在线工具站项目。

项目采用“配置驱动 + 一工具一模块 + 前后端分离”的方式组织。普通工具主要由后端 `tools.json` 注册并自动展示；复杂交互工具由前端专用组件承载。适合继续手工扩展小工具，也适合按现有规范批量补工具。

## 功能概览

- 在线工具站：开发、测试运维、格式转换、文本、编码、图片、图表、时间、益智游戏、其他等分类。
- 配置驱动工具：工具名称、说明、参数和组件大多由后端配置控制，前端刷新即可同步。
- 文件与格式转换：支持常见文档、图片、动图、音视频等转换场景，部分能力依赖 `FFmpeg`、`Playwright Chromium`。
- AI 助手与登录：独立用户登录体系，使用服务端会话和 Cookie。
- 独立后台管理：后台账号与工具站用户体系分离，当前包含反馈系统、账号活动日志和后台配置管理入口。
- 反馈系统：用户可提交反馈，后台可查看。
- 本地收藏：收藏数据保存在当前浏览器本地。
- 纯前端小游戏：如 2048、贪吃蛇、扫雷、推箱子、颜色排序等，进度保存在浏览器 `localStorage`。

## 技术栈

- 后端：`Python`、`FastAPI`、`SQLAlchemy`
- 前端：`Vue 3`、`Vite`
- 数据库：普通工具不依赖数据库；登录、反馈、后台相关功能使用 `MySQL`
- 可选运行环境：`Docker` 可用于本地或服务器启动 MySQL
- 可选系统能力：`FFmpeg`、`Playwright Chromium` 用于部分音视频、动图、SVG 动画转换工具

## 仓库结构

```text
qixiang_tools/
├── backend/        # FastAPI 后端源码、工具模块、接口和测试
├── frontend/       # Vue 3 前端源码、页面、组件和静态资源
├── docs/           # 项目文档、部署笔记、问题解决记录
├── README.md       # 项目入口说明
└── .gitignore      # Git 忽略规则
```

更完整的文件职责说明见：[项目代码文件总体说明](./docs/项目代码文件总体说明.md)。

## 环境准备

建议版本：

- Python：`3.11+`，当前本地常用 `3.12`
- Node.js：建议 `18+` 或 `20+`
- MySQL：`8.0`
- npm：随 Node 安装即可

部分工具需要额外安装：

```bash
# 音视频、动图、部分图片处理
ffmpeg -version

# SVG 动画渲染相关工具
python -m playwright install chromium
```

如果只开发普通文本工具、命令工具或纯前端工具，可以暂时不装 `FFmpeg` 和 `Playwright Chromium`。

## 配置文件

真实配置不要提交到 GitHub。新环境先复制模板：

```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
```

后端常见配置：

- `DATABASE_URL`：MySQL 连接串
- `SESSION_EXPIRE_DAYS`：AI 登录会话有效期
- `SESSION_COOKIE_NAME`：AI 登录 Cookie 名称
- `SESSION_COOKIE_SECURE`：HTTPS 环境建议为 `true`
- `BACKOFFICE_*`：独立后台入口、账号和会话配置

前端常见配置：

- `VITE_API_BASE_URL`：后端 API 地址，本地常用 `http://127.0.0.1:8000/api`

GitHub 上传、`.gitignore` 和配置模板说明见：[GitHub 上传与配置模板说明](./docs/GitHub上传与配置模板说明.md)。

## 本地启动

### 后端

```bash
cd backend
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

访问：

- 接口文档：`http://127.0.0.1:8000/docs`
- 健康检查：`http://127.0.0.1:8000/api/health`

### 前端

```bash
cd frontend
npm install
npm run dev
```

访问：

- 前端页面：`http://127.0.0.1:5173/`

如果 `5173` 被占用，Vite 会自动切到下一个端口，比如 `5174`。

## 数据库

普通工具不依赖数据库；登录、反馈、后台管理相关功能需要 MySQL。

本地可以用 Docker 启动 MySQL，详细步骤见：[Docker 部署命令笔记](./docs/Docker部署命令笔记.md)。

初始化表结构可执行：

```bash
cd backend
.venv/bin/python -c "from app.db.init_db import ensure_schema; ensure_schema(); print('db ok')"
```

## 测试与构建

后端测试：

```bash
cd backend
.venv/bin/python -m pytest
```

前端构建：

```bash
cd frontend
npm run build
```

如果只是改文档，不需要重新构建；如果改了前端页面、组件或样式，建议跑一次 `npm run build`。

## 新增工具

普通后端工具通常改：

```text
backend/app/tools/<module>.py
backend/app/configs/tools.json
```

复杂前端工具通常还要改：

```text
frontend/src/components/<Component>.vue
frontend/src/pages/ToolPage.vue
```

详细流程见：[新增小工具开发指南](./docs/新增小工具开发指南.md)。

工具分类和展示顺序主要由以下文件控制：

```text
backend/app/configs/categories.json
backend/app/configs/tools.json
backend/app/services/tool_loader.py
```

## 部署与更新

服务器部署、Nginx、systemd、rsync 更新和常见问题见：

- [部署与更新指南](./docs/部署与更新指南.md)
- [项目常用命令汇总](./docs/项目常用命令汇总.md)
- [Playwright 和 FFmpeg 动图视频转换部署记录](./docs/问题解决记录/Playwright和FFmpeg动图视频转换部署记录.md)

## 安全注意

- 不提交 `backend/.env`、`frontend/.env`、数据库密码文件和真实密钥。
- 后台账号、后台入口答案、数据库密码只放服务端环境变量或服务器 `.env`。
- `backend/app/temp/` 是临时上传和输出目录，不提交。
- 数据库数据不靠 GitHub 保存，需要用 `mysqldump` 备份和恢复。
- 如果误提交密钥，需要立即更换密钥或密码，不能只删除文件。

## 核心文档

- [文档总览](./docs/README.md)
- [项目代码文件总体说明](./docs/项目代码文件总体说明.md)
- [GitHub 上传与配置模板说明](./docs/GitHub上传与配置模板说明.md)
- [前后端架构与联动原理](./docs/前后端架构与联动原理.md)
- [新增小工具开发指南](./docs/新增小工具开发指南.md)
- [部署与更新指南](./docs/部署与更新指南.md)
- [AI 助手与登录系统说明](./docs/AI助手与登录系统说明.md)
- [后续项目扩展研究点](./docs/后续项目扩展研究点.md)

## 开发原则

- 工具元信息优先维护在 `tools.json` 和 `categories.json`。
- 后端工具遵循“一工具一 Python 模块”。
- 前端优先复用通用组件，简单文本工具走 `ToolTextForm`，文件工具走 `ToolFileForm`。
- 本地交互型工具优先写独立前端组件。
- 新增控件优先复用现有 UI 风格，不回退到浏览器原生控件。
- 真实配置、依赖目录、构建缓存、临时文件不进 Git。
