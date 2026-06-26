# AI 助手与登录系统说明

> 本文以当前仓库真实实现为准，记录“悬浮 AI 助手 + 登录/注册体系”的架构、接口、配置、上线步骤与后续扩展点。
> 这是项目里**第一个引入数据库**的功能；其余 200+ 工具仍不依赖数据库、互不影响。

## 1. 这套东西是什么

- 全站右侧中部一个**悬浮 AI 机器人**（GIF），点击弹出**自适应对话窗**（蓝白科技风、左侧模型选择、发送按钮置灰↔蓝）。
- 点发送时若未登录 → 弹出**登录/注册**。
- 登录态采用**服务端会话表 + httpOnly Cookie**，有效期 30 天；主动退出登录会**立即删除服务端会话**并清 Cookie。
- 对话窗左上角是**账号主页**入口（头像按钮）：查看账号、有效期、退出登录。
- AI 对话目前是**占位回复**（桩），模型列表是假数据（天问一号~四号），待接入真实模型。
- 反馈与账号活动日志已经迁移到**独立后台管理系统**，不再通过 AI 登录账号暴露管理员入口。

设计原则：**前端整体是一个自包含独立模块，不与工具体系耦合**；后端登录/会话相关异常一律降级，**数据库不可用时只影响登录功能，其它工具照常**。

## 2. 目录与改动清单

### 后端（全部新增，对现有工具零改动逻辑）

```text
backend/app/
├── db/
│   ├── session.py      # 引擎懒加载（连不上不崩）、自动适配 SQLite/MySQL、会话上下文
│   ├── models.py       # users / sessions / feedback / logs 四张表
│   └── init_db.py      # 首次用到时懒建表
├── schemas/
│   ├── auth.py         # 登录/注册请求体
│   └── feedback.py     # 反馈提交请求体
├── services/
│   ├── auth_service.py      # 注册/登录/会话签发校验删除、bcrypt、校验规则
│   ├── feedback_service.py  # 反馈落库/读取
│   ├── activity_service.py  # 账号活动日志写入（尽力而为）/读取
│   └── backoffice_service.py # 独立后台入口与后台登录态
└── api/routes/
    ├── auth.py         # /auth/register /auth/login /auth/me /auth/logout（含 Cookie 收发 + 活动日志）
    ├── chat.py         # /chat/models /chat（占位回复 + history 校验）
    ├── feedback.py     # /feedback（落库，匿名可提交）
    └── backoffice.py   # /backoffice/*（独立后台入口、登录、只读数据）
```

仅以下现有文件是**小增量改动**：`core/config.py`（加会话/独立后台配置）、`api/routes/__init__.py`（挂路由）、`requirements.txt`（加 SQLAlchemy、pymysql）、`.env.example`。

### 前端（独立模块，仅 `App.vue` 挂一行）

```text
frontend/src/components/ai-assistant/   # 自包含模块，只依赖 vue 与本模块自身
├── AiAssistantWidget.vue   # 悬浮机器人 + 编排面板/登录弹窗（挂在 App.vue）
├── AiChatPanel.vue         # 对话窗（账号主页、模型选择、消息流、输入发送）
├── AuthDialog.vue          # 登录/注册弹窗（输入校验 + 明文/密文切换）
├── ModelSelect.vue         # 模型下拉（名称 + 右侧倍率徽标 + 选中✓）
├── AiRobotLogo.vue         # 复用的机器人 logo（/ai-robot-logo.png）
└── service.js              # 自带 HTTP（带 Cookie）、登录态、校验规则、对话/反馈管理接口
```

独立后台页面在 `frontend/src/pages/BackofficePage.vue`，入口接口封装在 `frontend/src/api/backoffice.js`。

静态资源（构建时随 `public/` 原样进 `dist/`）：
`frontend/public/ai-robot-logo.png`、`frontend/public/ai-robot-tianwen-smooth-animation.gif`。

> 主应用侧改动：`App.vue` 挂悬浮组件；`router/index.js` 加独立后台路由；`api/feedback.js` 提交主后端 `/api/feedback`。

> 模块独立性：`ai-assistant/` 下所有文件只 import `vue` 和 `./` 本模块，不依赖工具侧的 `api/`、`utils/`、其它 `components/*`；也没有工具页面反向依赖它。除 `App.vue` 挂载一行外，对现有前端零侵入。

## 3. 数据库设计

四张表（MySQL `utf8mb4`），首次调用相关接口时**自动创建，无需手动建表**：

| 表 | 字段 | 说明 |
|---|---|---|
| `users` | `id` / `account` / `password_hash` / `created_at` / `last_login_at` | `account` 唯一；`password_hash` 为 bcrypt |
| `sessions` | `id` / `token` / `user_id` / `account` / `created_at` / `expires_at` | `token` 写进 Cookie；退出登录即删行 |
| `feedback` | `id` / `feedback_type` / `content` / `tool_*` / `contact_*` / `submitted_page` / `user_agent` / `account` / `created_at` | 反馈落库；匿名 `account` 为空 |
| `logs` | `id` / `event` / `account` / `ip` / `user_agent` / `created_at` | 账号活动日志（register/login/logout） |

- 主键在 MySQL 是 `BIGINT`、在 SQLite 落为 `INTEGER`（兼容测试）。
- 会话令牌 = `secrets.token_urlsafe(32)`；过期判断按 `expires_at`。

## 4. 接口清单

| 方法 | 路径 | 鉴权 | 返回 `data` |
|---|---|---|---|
| POST | `/api/auth/register` | 否 | `{user:{id,account,expires_at}}`，并下发会话 Cookie |
| POST | `/api/auth/login` | 否 | 同上 |
| GET | `/api/auth/me` | Cookie | `{user:{id,account,expires_at}}`，未登录/失效 401 |
| POST | `/api/auth/logout` | Cookie | 删服务端会话 + 清 Cookie（尽力而为，DB 故障也清 Cookie） |
| GET | `/api/chat/models` | 否 | `{models:[{id,name,description,badge}],default}` |
| POST | `/api/chat` | Cookie | `{reply,model}`；`history` 仅允许 `user/assistant`、≤20 条 |
| POST | `/api/feedback` | 否（登录则记账号） | `{id}`；落库到 `feedback` 表，空内容 400 |
| GET | `/api/backoffice/challenge` | 否 | `{question}`，后台入口问题 |
| POST | `/api/backoffice/entry` | 否 | `{path}`，答案正确后返回一次性后台入口路径 |
| POST | `/api/backoffice/entry/consume` | 否 | 消费一次性入口 ticket |
| POST | `/api/backoffice/login` | 否 | `{user:{account,expires_at}}`，下发后台专用 Cookie |
| GET | `/api/backoffice/me` | 后台 Cookie | `{user:{account,expires_at}}` |
| POST | `/api/backoffice/logout` | 后台 Cookie | 清理后台登录态 |
| GET | `/api/backoffice/feedback` | 后台 Cookie | `{items:[...]}`，反馈只读 |
| GET | `/api/backoffice/logs` | 后台 Cookie | `{items:[...]}`，账号活动日志只读 |

统一响应壳 `{code,message,data}`，成功 `code=0`。错误码：`4001` 入参、`4010/4012/4013` 未登录/过期/无效、`4011` 账号或密码错、`4090` 账号已注册、`503x` 数据库不可用或后台未配置。

## 5. 校验与登录态规则

- **账号**：`^\d{11}$`（11 位纯数字，可填手机号，但不做短信验证）。前端输入即过滤非数字。
- **密码**：`^(?=.*[A-Za-z])(?=.*\d).{8,16}$`（8-16 位，**必须同时含字母和数字**，区分大小写，允许特殊字符）。前后端同规则。
- **登录有效期 / Cookie 过期**：均 30 天（`SESSION_EXPIRE_DAYS`）。
- **Cookie**：`httpOnly`（JS 读不到，降低 XSS 盗取）、`SameSite=Lax`、`Max-Age=30天`、`Secure` 可配。前端所有请求带 `credentials:"include"`，是否登录以 `/auth/me` 为准。
- **退出登录**：删 `sessions` 行 → 旧令牌**立即失效**（已有测试验证：退登后拿旧令牌仍 401）。

## 6. 配置项（`backend/.env`，参考 `.env.example`）

```ini
# 生产必填真实账号密码；连不上时仅登录功能降级，其它工具不受影响
DATABASE_URL=mysql+pymysql://用户名:密码@127.0.0.1:3306/qixiang_tools?charset=utf8mb4
# 登录有效期 / Cookie 过期（天）
SESSION_EXPIRE_DAYS=30
# 会话 Cookie 名（一般不用改）
SESSION_COOKIE_NAME=qx_session
# 生产 HTTPS 下设 true（Cookie 仅经 https 发送）；本地 http 调试保持 false
SESSION_COOKIE_SECURE=false
# 独立后台管理系统。生产环境必须配置，不写进前端。
BACKOFFICE_ACCOUNTS=admin:换成管理员密码:admin,view:换成观察员密码:viewer
BACKOFFICE_ENTRY_QUESTION=如果时间忘记了名字，它会把前三个音节藏在哪里？
BACKOFFICE_ENTRY_ANSWER=
BACKOFFICE_COOKIE_NAME=qx_backoffice_session
BACKOFFICE_SESSION_HOURS=12
```

不配 `.env` 时，`config.py` 默认指向 `mysql+pymysql://root:root@127.0.0.1:3306/qixiang_tools`。

## 7. 本地开发跑通

1. 装依赖：`backend/.venv/bin/pip install -r backend/requirements.txt`（新增 SQLAlchemy、pymysql）。
2. 数据库二选一：
   - 本地有 MySQL：建库 `CREATE DATABASE qixiang_tools DEFAULT CHARACTER SET utf8mb4;`，在 `backend/.env` 填 `DATABASE_URL`。
   - 本地没 MySQL 想快速验证：把 `DATABASE_URL=sqlite:///./local_ai.db`（引擎无关，自动建表）。
3. 起后端、起前端（`npm run dev`），右侧机器人即可用。

> 单测无需任何 MySQL：`backend/conftest.py` 已强制测试走临时 SQLite。`cd backend && .venv/bin/python -m pytest -q`。

## 8. 上线步骤（接现有部署架构）

服务器：Ubuntu，`/home/ubuntu/qixiang_tools`，nginx 托管 `frontend/dist` 并反代 `/api`，后端 systemd `qixiang-backend`（venv `backend/.server-venv`）。详见 [部署与更新指南](./部署与更新指南.md)。

1. **装 MySQL**：`sudo apt install mysql-server`，建库建账号：
   ```sql
   CREATE DATABASE IF NOT EXISTS qixiang_tools DEFAULT CHARACTER SET utf8mb4;
   CREATE USER 'qixiang'@'localhost' IDENTIFIED BY '换成强密码';
   GRANT ALL PRIVILEGES ON qixiang_tools.* TO 'qixiang'@'localhost';
   FLUSH PRIVILEGES;
   ```
2. **装新依赖**：`./backend/.server-venv/bin/pip install -r backend/requirements.txt`
3. **写 `backend/.env`**：填真实 `DATABASE_URL`；站点是 HTTPS 就设 `SESSION_COOKIE_SECURE=true`。
4. **前端**：本地先 `cd frontend && npm run build`，上传 `frontend/dist`（**含 `public` 里的机器人 png/gif**，构建后已在 `dist/`）。
5. **重启后端**：`sudo systemctl restart qixiang-backend`。表会在首次登录时自动建。
6. 注意 [部署与更新指南](./部署与更新指南.md) 里的**文件权限修正**（Mac 上传文件常带 600，nginx 读不了会 403）。

## 9. 反馈系统（落库）与独立后台查看

反馈不再走 serverless/外部表格，而是**直接落库主后端 MySQL**（取代旧的「无数据库 / Worker 落表」方案）。

- **提交**：反馈页照旧，`api/feedback.js` 改为 `POST /api/feedback`，**匿名即可提交**；若带有效会话 Cookie，则顺带记下提交者账号。请求失败时仍会**暂存本浏览器**兜底，不丢内容。
- **后台账号**：在 `backend/.env` 配置 `BACKOFFICE_ACCOUNTS`，格式为 `账号:密码:角色`，多个账号用英文逗号分隔；`admin` 可看全部，`viewer` 只能看反馈，不复用 AI 用户登录态。
- **隐藏入口**：连续点击站点左上角「琦湘工具集合」品牌热区 5 次，弹出入口问答；答案正确后由后端返回一次性后台路径并新标签页打开。
- **后台页面**：`BackofficePage.vue` 是独立后台，不显示工具站壁纸、导航、AI 机器人；左侧账号中心 + 菜单，右侧显示反馈与账号活动日志。
- **后端鉴权**：`/api/backoffice/*` 使用后台专用 Cookie，不依赖 AI 用户，也没有 `is_admin` 字段。
- **日志**：`logs` 表记录 register/login/logout（时间、账号、IP、UA），由 `auth.py` 路由在登录流程里**尽力而为**写入（写失败只告警，不影响登录）。

> 后台入口 ticket 仅用于打开后台登录页，不等于后台登录态；真正查看数据仍需后台账号密码登录。

## 10. 后续接入真实模型

1. 改 `backend/app/api/routes/chat.py` 的 `MODELS`（`id/name/description/badge`，`badge` 是下拉右侧倍率徽标）。
2. 把 `chat()` 里的占位 `reply` 换成真实模型调用（按 `payload.model` 路由到对应模型；`payload.history` 已过滤为 `user/assistant`、≤20 条）。
3. 前端无需改动——模型列表与对话都走现有接口。

## 11. 已知项 / 取舍

- **过期会话清理**：`resolve_session` 读取路径只读，遇到过期会话会用 `destroy_session` 尽力删除该过期行并返回 401（清理失败也不影响 401）；不会再残留过期行。
- **无登录失败次数限制**：用户量低暂不做限流/锁定；后续如需可在 `auth_service.login` 加。
- **CORS**：`main.py` 仍是 `allow_origins=["*"] + allow_credentials=True`。当前部署是**同源**（nginx 同时托管前端与 `/api`），Cookie 流正常、无安全问题；若将来前端跨域直连后端，需收紧为白名单并注意 `SameSite`。
- **AI 回复为占位桩**，模型未接入。
