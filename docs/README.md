# 文档总览

这套文档以当前仓库的真实实现为准，不再写抽象方案。

如果你后面继续维护 `琦湘工具集合`，建议把这里当成第一入口。

## 建议阅读顺序

1. [前后端架构与联动原理](./前后端架构与联动原理.md)
2. [项目常用命令汇总](./项目常用命令汇总.md)
3. [新增小工具开发指南](./新增小工具开发指南.md)
4. [反馈系统整理](./feedback/README.md)
5. [当前实现版技术设计文档](./技术设计文档_无数据库_FastAPI_Vue.md)

## 这套文档解决什么问题

- 想知道当前项目是怎么跑起来的：看“前后端架构与联动原理”
- 想快速复制启动、构建、测试和排查命令：看“项目常用命令汇总”
- 想自己继续手搓小工具：看“新增小工具开发指南”
- 想知道反馈系统当前怎么接、还缺什么：看 `docs/feedback`
- 想看完整的当前架构快照、视觉体系和工程边界：看技术设计文档

## 当前工程快照

截至 `2026-04-30`：

- 启用分类：`10`
- 启用工具：`206`
- 后端入口：`backend/app/main.py`
- 前端入口：`frontend/src/main.js`
- 数据模式：`无数据库`
- 工具元信息维护方式：`categories.json + tools.json`
- 当前视觉体系：
  - 透明卡片
  - 统一 `GlassSelect`
  - 四季动态森林背景
  - 固定顶部导航与稳定滚动条
  - 品牌静态 logo、滑动 logo 与独立 favicon

当前分类：

- `开发`
- `测试运维`
- `格式转换`
- `文本`
- `编码`
- `图片`
- `图表`
- `时间`
- `益智游戏`
- `其他`

## 当前文档目录

```text
docs/
├── README.md
├── 项目常用命令汇总.md
├── 前后端架构与联动原理.md
├── 新增小工具开发指南.md
├── 技术设计文档_无数据库_FastAPI_Vue.md
├── serverless-feedback-plan.md
└── feedback/
    ├── README.md
    ├── serverless-feedback-plan.md
    └── 反馈遗留事项整理.md
```

## 你后面最常会改到的地方

### 新增一个普通文本工具

通常只需要改：

1. `backend/app/tools/<module>.py`
2. `backend/app/configs/tools.json`

### 新增一个文件工具

通常只需要改：

1. `backend/app/tools/<module>.py`
2. `backend/app/configs/tools.json`
3. `backend/app/utils/validators.py`

### 新增一个本地工具

通常只需要改：

1. `frontend/src/components/<Component>.vue`
2. `frontend/src/pages/ToolPage.vue`
3. `backend/app/configs/tools.json`

### 新增一个分类

通常只需要改：

1. `backend/app/configs/categories.json`
2. `frontend/src/data/ui-mapping.js`
3. 如有首页展示顺序变化，再看 `Home.vue`

## 维护建议

- 优先复用现有通用组件，不要为简单工具反复造轮子
- 文本工具优先走 `ToolTextForm`
- 文件工具优先走 `ToolFileForm`
- 本地逻辑型工具优先走独立前端组件
- 新增控件不要回退到浏览器原生下拉，统一走 `GlassSelect`
- 视觉层不要破坏现有的透明化和背景体系
