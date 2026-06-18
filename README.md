# 琦湘工具集合

一个基于 `FastAPI + Vue 3 + Vite` 的在线工具站项目。

当前版本已经是可持续扩展的工程化实现，不再只是骨架。项目采用“配置驱动 + 一工具一模块 + 前后端分离”的方式组织，适合继续手工补工具，也适合按现有规范批量扩展小工具。

## 当前快照

- 后端：`FastAPI`
- 前端：`Vue 3 + Vite`
- 数据库：`工具无库；登录/AI 模块用 MySQL`
- 当前启用分类：`10`
- 当前启用工具：`206`
- 工具分类：`开发 / 测试运维 / 格式转换 / 文本 / 编码 / 图片 / 图表 / 时间 / 益智游戏 / 其他`

## 仓库结构

```text
qixiang_tools/
├── backend/        # FastAPI 后端
├── frontend/       # Vue 3 前端
└── docs/           # 当前项目文档
```

## 启动方式（输入启动命令前都需要cd到各自文件的根目录）

### 后端

```bash
cd /Users/a123/PycharmProjects/qixiang_tools/backend
/Library/Frameworks/Python.framework/Versions/3.12/bin/python3 -m pip install -r requirements.txt
/Library/Frameworks/Python.framework/Versions/3.12/bin/python3 /Users/a123/PycharmProjects/qixiang_tools/backend/app/main.py
或者
cd /Users/a123/PycharmProjects/qixiang_tools/backend
python3 -m uvicorn app.main:app --host 127.0.0.1 --port 8000

```

访问：

- 接口文档：`http://127.0.0.1:8000/docs`
- 健康检查：`http://127.0.0.1:8000/api/health`

### 前端

```bash
cd /Users/a123/PycharmProjects/qixiang_tools/frontend
npm install
npm run dev # 启动前端开发服务器，如果没启动这个就访问http://127.0.0.1:5173/会报错：127.0.0.1 拒绝了我们的连接请求。
```

访问：

- 前端：`http://127.0.0.1:5173/`

如果 `5173` 被占用，Vite 会自动切到下一个端口，比如 `5174`。

## 核心文档

- [文档总览](./docs/README.md)
- [项目常用命令汇总](./docs/项目常用命令汇总.md)
- [前后端架构与联动原理](./docs/前后端架构与联动原理.md)
- [新增小工具开发指南](./docs/新增小工具开发指南.md)
- [反馈系统整理](./docs/feedback/README.md)
- [当前实现版技术设计文档](./docs/技术设计文档_FastAPI_Vue.md)
- [部署与更新指南](./docs/部署与更新指南.md)
- [AI 助手与登录系统说明](./docs/AI助手与登录系统说明.md)

## 当前开发原则

- 工具本身不依赖数据库、不做服务端历史记录；仅登录/AI 模块使用 MySQL（见 [AI 助手与登录系统说明](./docs/AI助手与登录系统说明.md)）。
- 工具元信息由 `backend/app/configs/tools.json` 和 `categories.json` 维护。
- 后端工具遵循“一工具一 Python 模块”的约束。
- 前端优先复用通用组件，能不写定制组件就不写。
- 站点视觉统一使用透明卡片、统一下拉组件、四季动态背景和轻动效体系。
