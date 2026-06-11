# 琦湘工具集合 技术设计文档（当前实现版）

## 文档信息

- 项目名称：`琦湘工具集合`
- 文档版本：`V3.2`
- 更新日期：`2026-04-30`
- 适用阶段：`当前实现说明 / 后续扩工具 / 自维护 / AI 协作开发`
- 后端技术栈：`FastAPI + Pydantic`
- 前端技术栈：`Vue 3 + Vite + 原生 CSS`
- 数据策略：`无数据库`

---

## 1. 项目目标

琦湘工具集合不是一个后台驱动平台，而是一套：

- 前后端分离
- 配置驱动
- 一工具一模块
- 统一视觉体系
- 持续新增小工具

的无数据库工具站工程。

当前项目目标有四条：

1. 让新增工具尽量只改少量固定文件
2. 保留统一的页面骨架、组件体系和视觉语言
3. 让自己手写工具和 AI 协助生成工具都能落到同一套结构
4. 在不引入数据库的前提下，尽量保持站点可维护、可扩展、可验证

---

## 2. 当前项目快照

截至本次文档整理，当前真实状态如下：

- 启用分类：`10`
- 启用工具：`206`
- 分类结构：
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

当前版本已经不是骨架，而是一套完整可运行站点，已具备：

- 首页
- 工具详情页
- 收藏页
- 四季背景预览页
- 独立反馈页
- 独立打赏页
- 动态背景系统
- 统一下拉组件
- 工具缓存
- 本地收藏
- 北京时间与农历信息卡片
- 多数工具的通用输入输出框架

---

## 3. 总体架构

```text
浏览器
  ├── 首页 / 收藏页 / 预览页 / 反馈页 / 打赏页
  ├── 工具详情页
  ├── 文本工具 / 文件工具 / 本地工具
  └── 背景、动画、Toast、缓存、收藏
          │
          ▼
Vue 3 + Vite
  ├── App.vue
  ├── router/index.js
  ├── pages/*.vue
  ├── components/*.vue
  ├── data/*.js
  ├── api/*.js
  └── utils/*.js
          │
          ▼
FastAPI
  ├── /api/categories
  ├── /api/tools
  ├── /api/tools/{slug}
  ├── /api/tools/{slug}/execute
  ├── /api/tools/{slug}/upload
  ├── /api/time/beijing
  └── /api/health
          │
          ▼
配置 + 工具模块 + 数据文件 + 临时目录
  ├── categories.json
  ├── tools.json
  ├── app/tools/*.py
  ├── app/data/*.json
  └── app/temp/input + output
```

---

## 4. 当前目录结构

### 4.1 仓库根目录

```text
qixiang_tools/
├── backend/    # FastAPI 后端
├── frontend/   # Vue 3 前端
└── docs/       # 当前维护文档
```

### 4.2 后端目录

```text
backend/app/
├── main.py
├── api/routes/
├── core/
├── schemas/
├── services/
├── tools/
├── utils/
├── configs/
├── data/
└── temp/
```

### 4.3 前端目录

```text
frontend/src/
├── App.vue
├── router/
├── pages/
├── components/
├── api/
├── data/
├── styles/
└── utils/
```

---

## 5. 后端设计

## 5.1 结构分层

### `main.py`

- 应用入口
- 注册路由、日志、异常处理、CORS、清理逻辑

### `api/routes`

- `health.py`：健康检查
- `meta.py`：分类、工具列表、工具详情
- `tools.py`：文本执行、文件上传、文件结果返回
- `time.py`：北京时间 + 农历

### `core`

- 配置
- 日志
- 统一异常
- 统一响应结构

### `schemas`

- 工具元信息
- 请求结构
- 时间结构

### `services`

- `tool_loader.py`：读取 `categories.json` / `tools.json`
- `tool_registry.py`：动态导入工具模块
- `time_service.py`：北京时间与农历计算
- `cleanup_service.py`：请求级临时目录清理

### `tools`

- 每个工具一个文件
- 统一 `run()` 契约

### `utils`

- 上传文件保存
- 上传类型白名单
- 常用转换与工具函数

### `configs`

- `categories.json`
- `tools.json`

### `data`

- 本地静态数据集
- 如成语、歇后语等

### `temp`

- 文件型工具的临时输入输出目录

## 5.2 后端设计原则

1. 不引入数据库
2. 工具元信息由配置文件驱动
3. 路由层尽量轻
4. 业务逻辑尽量沉到工具模块
5. 文件请求结束后及时清理临时目录
6. 错误尽量用中文返回

## 5.3 工具模块约定

### 文本工具

```python
def run(text: str, **params) -> str:
    ...
```

### 文件工具

```python
def run(input_path: str, output_dir: str, filename: str = "", content_type: str = "", **params) -> str:
    ...
```

### 约定含义

- 返回字符串：代表文本结果
- 返回文件路径：代表文件结果
- 业务错误优先抛 `AppException`

---

## 6. 前端设计

## 6.1 页面结构

当前路由：

- `/`：首页
- `/tool/:slug`：工具详情页
- `/favorites`：收藏页
- `/preview`：背景预览页
- `/feedback`：反馈页
- `/support`：打赏页

## 6.2 页面职责

### 首页 `Home.vue`

- 分类导航
- 搜索
- 工具卡片列表
- 分类说明
- 首页缓存恢复

### 工具页 `ToolPage.vue`

- 拉取工具详情
- 根据 `component` 选择组件
- 展示工具头部
- 展示北京时间 + 农历卡片
- 记录返回上一分类 / 搜索结果的上下文

### 收藏页 `FavoritesPage.vue`

- 展示本地收藏工具
- 支持清空
- 不做排序编辑

### 预览页 `PreviewPage.vue`

- 预览和切换四季背景
- 便于单独检查视觉层

### 反馈页 `FeedbackPage.vue`

- 独立反馈表单
- 支持工具来源上下文
- 可接远端，也可本地暂存

### 打赏页 `SupportPage.vue`

- 独立打赏展示页

## 6.3 前端核心组件

### 全局壳层

- `App.vue`
- `SiteWallpaper.vue`
- `ToastViewport.vue`

### 导航与品牌

- `SiteHeader.vue`
- `HeaderQXMarquee.vue`

### 工具页骨架

- `ToolDetailActions.vue`
- `ToolDateTimeCard.vue`
- `ResultPanel.vue`
- `LoadingState.vue`
- `ErrorMessage.vue`

### 通用工具组件

- `ToolTextForm.vue`
- `ToolFileForm.vue`
- `GlassSelect.vue`

### 本地工具与定制工具

- `ToolKeyboardTester.vue`
- `components/keyboard-tester-render/*.vue`
- `ToolWhiteboard.vue`
- `ToolHttpTester.vue`
- `ToolWebsocketTester.vue`
- `ToolChartStudio.vue`
- `ToolCommandCatalog.vue`
- 各种时间类本地工具组件

## 6.4 前端设计原则

1. 简单工具优先复用通用组件
2. 参数渲染优先走配置驱动
3. 复杂交互再写独立组件
4. 不引入大型 UI 库破坏统一风格
5. 页面动效轻量，不能压过工具内容

---

## 7. 工具渲染体系

## 7.1 工具输入模式

当前工具按 `input_mode` 分为：

- `text`
- `file`
- `mixed`
- `form`
- `local`

## 7.2 默认组件映射

默认映射在：

- `frontend/src/data/ui-mapping.js`

映射规则：

- `text` -> `ToolTextForm`
- `file` -> `ToolFileForm`
- `mixed` -> `ToolTextForm`
- `form` -> `ToolTextForm`
- `local` -> 指向具体本地组件

## 7.3 自定义组件机制

如果某个工具不适合通用表单，可以在 `tools.json` 中指定 `component`，再在 `ToolPage.vue` 中注册。

当前已经使用这个机制的场景包括：

- 键盘测试
- 白板
- 图表工作台
- 浏览器信息
- HTTP / WebSocket 测试
- adb / Linux / Git / Docker 命令大全
- 多个时间类本地工具

## 7.4 参数系统

当前通用参数类型：

- `text`
- `textarea`
- `select`
- `radio`

已支持：

- 默认值
- 占位文案
- 条件显示 `showWhen`

---

## 8. 配置驱动模型

## 8.1 分类配置

`categories.json` 负责：

- 分类 `slug`
- 分类名称
- 分类说明
- 排序
- 是否启用

## 8.2 工具配置

`tools.json` 负责：

- `slug`
- `module`
- `name`
- `category`
- `summary`
- `description`
- `input_mode`
- `result_type`
- `component`
- `enabled`
- `params`

这意味着：

- 后端通过它定位模块
- 前端通过它决定标题、摘要、说明、参数和组件

---

## 9. 当前接口设计

### 元信息接口

- `GET /api/categories`
- `GET /api/tools`
- `GET /api/tools/{slug}`

### 工具执行接口

- `POST /api/tools/{slug}/execute`
- `POST /api/tools/{slug}/upload`

### 辅助接口

- `GET /api/time/beijing`
- `GET /api/health`

### 当前响应原则

- JSON 结果统一走 `success_response`
- 文件结果直接返回 `FileResponse`
- 错误尽量返回中文

---

## 10. 前后端联动链路

## 10.1 工具列表链路

```text
Home.vue
  -> src/api/tools.js
  -> src/api/client.js
  -> GET /api/categories
  -> GET /api/tools
  -> tool_loader.py
  -> categories.json / tools.json
```

## 10.2 工具详情链路

```text
ToolPage.vue
  -> getTool(slug)
  -> GET /api/tools/{slug}
  -> tool_loader.get_tool_detail()
  -> tools.json
```

## 10.3 文本工具链路

```text
ToolTextForm.vue
  -> executeTextTool(slug, { text, params })
  -> POST /api/tools/{slug}/execute
  -> routes/tools.py execute_tool()
  -> get_tool_detail(slug)
  -> get_tool_module(slug)
  -> app.tools.<module>.run(text=..., **params)
```

## 10.4 文件工具链路

```text
ToolFileForm.vue
  -> uploadFileTool(slug, file, params)
  -> POST /api/tools/{slug}/upload
  -> validators.py 校验上传类型
  -> save_upload_file()
  -> app.tools.<module>.run(input_path=..., output_dir=..., filename=..., content_type=..., **params)
  -> FileResponse 或文本结果
  -> 请求结束后清理临时目录
```

## 10.5 本地工具链路

部分工具直接在浏览器执行，不依赖后端，例如：

- 键盘测试
- 浏览器信息
- 响应式布局检测
- adb / Linux / Git / Docker 命令大全
- 白板
- 部分时间工具

这类工具在 `ToolPage.vue` 中通过 `component` 映射到本地组件。

---

## 11. 视觉系统设计

当前项目已经形成统一视觉语言，后续开发必须保持。

## 11.1 页面基础风格

- 透明卡片
- 轻边框
- 统一圆角
- 轻投影
- 留白型标题区
- 统一输入框与按钮

## 11.2 透明化控件体系

当前站点统一使用：

- 透明输入框
- 透明按钮
- 透明结果卡片
- 统一玻璃下拉 `GlassSelect`

要求：

- 不允许局部回退成浏览器原生蓝色下拉
- 新增页面优先复用现有控件体系

## 11.3 动态背景体系

全站背景由 `SiteWallpaper.vue` 统一管理，季节森林和大树动效由 `SeasonalForestScene.vue` 承担。

当前四季主题：

- 春分
- 夏至
- 秋分
- 冬至

背景层级统一为：

```text
Base
Reading Veil
Atmosphere
Seasonal Forest
Motion
Noise
Vignette
```

实现文件：

- `frontend/src/components/SiteWallpaper.vue`
- `frontend/src/components/SeasonalForestScene.vue`
- `frontend/src/data/wallpaper-scenes.js`
- `frontend/src/styles/wallpaper.css`

### 当前背景设计原则

- 是辅助层，不抢正文
- 可在四季主题间切换
- 支持 `prefers-reduced-motion`
- 不使用视频背景
- 不依赖重型 3D 引擎

## 11.4 品牌与装饰层

- 顶部导航统一由 `SiteHeader.vue` 承担
- 顶部导航固定在视口顶部，页面滚动不影响导航位置
- 导航装饰层、静态品牌 logo 和滑动 logo 分离
- favicon 在 `frontend/index.html` 单独配置
- 动态装饰图不拦截交互

---

## 12. 数据与状态策略

当前项目不使用数据库，但并非完全无状态。

## 12.1 前端本地状态

- 首页缓存
- 工具详情缓存
- 收藏列表
- 背景预览模式
- 反馈本地暂存

## 12.2 后端临时状态

- 文件工具请求级临时目录
- 请求级输出文件

## 12.3 当前明确不做

- 服务端历史记录
- 用户账户
- 跨设备同步收藏
- 后台内容管理

---

## 13. 反馈系统设计

当前反馈体系采用：

- 前端入口已经完整接好
- 主后端不强耦合复杂反馈平台
- 推荐以 Worker + 表格系统落地

当前已有：

- `/feedback`
- `/support`
- `VITE_FEEDBACK_ENDPOINT`
- 未配置远端时的 localStorage 降级

详细整理请看：

- `docs/feedback/README.md`

---

## 14. 后续扩展建议

当前项目最适合继续做的，不是重构，而是稳定扩工具。

### 建议优先级

1. 继续补小工具
2. 继续补测试
3. 继续收口极个别复杂工具的 UI
4. 后续再考虑桌面打包

### 当前不建议马上做的事

- 引入数据库
- 推翻现有 UI 体系
- 重写整站框架
- 把所有本地工具强行迁回后端

---

## 15. 当前工程边界

### 文档转换

当前 `Word / PDF / TXT / EPUB / CSV / Excel / PPT` 互转是轻量转换链路，优先保留内容，不承诺复杂排版百分百还原。
格式转换分类的常见文档、表格、图片和音视频入口已收口为“XX 和 XX 互转”形式；旧的单向 slug 保持可执行但默认不在工具列表展示。

### 音视频与 GIF 转换

当前 `MP3 / FLAC / WAV / MOV / MP4 / GIF` 互转依赖服务器系统命令 `ffmpeg`，未安装时工具会返回明确错误，不会静默失败。GIF 转 PNG/JPG 会按帧导出并打包下载。

### 图片与 OCR

复杂图片抠图、OCR、无损放大等工具对输入质量和场景敏感，属于能力边界，不一定对所有图片都等价表现。当前图片抠图会优先保护已有真实 alpha 通道的透明 PNG，避免把已经处理好的透明 logo 再次误抠。

### 高交互本地工具

例如键盘测试这类页面，如果目标是“逐像素贴合参考图”，后续仍可能继续微调版式。

### 打包部署

如果后续要做桌面打包或跨平台部署，需要重点关注：

- OCR 依赖
- 文档转换依赖
- 加密依赖
- 模型和静态资源打包

---

## 16. 配套文档

- `docs/README.md`
- `docs/前后端架构与联动原理.md`
- `docs/新增小工具开发指南.md`
- `docs/feedback/README.md`

如果只看一份总览，优先看这份技术设计文档。  
如果要开始自己继续维护项目，优先看 `docs/README.md`。
