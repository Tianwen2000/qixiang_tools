# GitHub 上传与配置模板说明

> 目标：尽量把项目源码、文档、静态资源、配置模板都放到 GitHub；真实密钥、真实密码、数据库数据和大多数本地生成产物不提交。当前项目为配合现有 nginx/手动上传部署流程，例外地把 `frontend/dist` 纳入 Git 跟踪。

## 建议提交到 GitHub 的内容

```text
README.md
docs/
backend/app/
backend/tests/
backend/requirements.txt
backend/pytest.ini
backend/conftest.py
backend/.env.example
frontend/src/
frontend/public/
frontend/dist/
frontend/index.html
frontend/package.json
frontend/package-lock.json
frontend/vite.config.js
frontend/.env.example
```

除 `frontend/dist` 外，这些文件属于源码、文档、静态素材或可公开模板。`frontend/dist` 是构建产物，但当前部署流程依赖仓库内产物，因此修改前端后要先运行 `npm run build`，再一起提交更新后的 `dist`。

## 不建议提交的内容

```text
.env
backend/.env
frontend/.env
backend/.mysql-*
backend/.venv/
frontend/node_modules/
backend/app/temp/
__pycache__/
*.pyc
*.log
.DS_Store
.idea/
```

原因：

- `.env.local`、`.mysql-*` 可能包含数据库账号、后台密码、Cookie 配置。
- `.venv`、`node_modules` 可以通过依赖文件重新安装。
- `dist` 通常可以不提交，但本项目当前把它作为部署交付物跟踪；不要在未同步修改部署流程前单独取消跟踪。
- `backend/app/temp` 是上传和转换输出的临时文件。
- 缓存、日志、系统文件和 IDE 配置没有长期维护价值。

## 当前仓库状态说明

截至 2026-08-10，仓库中已经跟踪 `frontend/dist`、`frontend/node_modules` 和部分 `.idea` 文件；当前 `.gitignore` 没有忽略这三个目录。

- `frontend/dist`：与现有部署指南一致，当前视为有意跟踪的部署产物。
- `frontend/node_modules`、`.idea`：属于历史遗留跟踪，不代表推荐做法。清理它们需要单独修改 `.gitignore` 并从 Git 索引移除，本文档调整不会代替该仓库清理操作。

## 当前 .gitignore 重点

```gitignore
.DS_Store
.vscode/
__pycache__/
*.py[cod]
.venv/
backend/app/temp/
log/
*.log
.env
backend/.env
backend/.mysql-*
```

上面是当前 `.gitignore` 的实际内容摘要，不包含 `frontend/node_modules/`、`frontend/dist/` 或 `.idea/`。这套规则已经保护真实配置和部分本地生成文件；如果后续决定清理依赖目录和 IDE 配置，需要同时更新 `.gitignore` 和 Git 索引。

## 后端配置模板

后端已经有 `backend/.env.example`。新机器运行时复制一份：

```bash
cp backend/.env.local.example backend/.env.local
```

然后按实际环境修改：

```env
APP_ENV=dev
APP_HOST=0.0.0.0
APP_PORT=8000
API_PREFIX=/api
TEMP_DIR=./app/temp
MAX_UPLOAD_SIZE_MB=50
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173

DATABASE_URL=mysql+pymysql://qixiang:换成应用数据库密码@127.0.0.1:3306/qixiang_tools?charset=utf8mb4
SESSION_EXPIRE_DAYS=30
SESSION_COOKIE_NAME=qx_session
SESSION_COOKIE_SECURE=false

BACKOFFICE_ACCOUNT=admin
BACKOFFICE_PASSWORD=你的后台密码
BACKOFFICE_ENTRY_QUESTION=如果时间忘记了名字，它会把前三个音节藏在哪里？
BACKOFFICE_ENTRY_ANSWER=你的入口答案
BACKOFFICE_COOKIE_NAME=qx_backoffice_session
BACKOFFICE_SESSION_HOURS=12
```

注意：上面只是模板示例。真实密码不要提交到 GitHub。

## 前端配置模板

前端已经有 `frontend/.env.example`。新机器运行时复制一份：

```bash
cp frontend/.env.local.example frontend/.env.local
```

本地开发常用：

```env
VITE_API_BASE_URL=http://127.0.0.1:8000/api
```

服务器部署时通常由 Nginx 反代 `/api`，可按实际部署改为：

```env
VITE_API_BASE_URL=/api
```

## 数据库不能直接靠 GitHub 保存

GitHub 适合保存代码和模板，不适合保存真实数据库数据。数据库应该用下面方式迁移：

```bash
# 备份
docker exec qixiang-mysql mysqldump -uroot -p"$ROOT_PW" qixiang_tools > qixiang_tools.sql

# 恢复
docker exec -i qixiang-mysql mysql -uroot -p"$ROOT_PW" qixiang_tools < qixiang_tools.sql
```

如果只需要新环境能启动，不需要带历史数据，就只提交 `backend/.env.example` 和建表代码即可；后端启动后会自动建表。

## 新机器拉代码后的基本步骤

```bash
git clone git@github.com:用户名/仓库名.git
cd qixiang_tools

cp backend/.env.local.example backend/.env.local
cp frontend/.env.local.example frontend/.env.local

cd backend
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python -c "from app.db.init_db import ensure_schema; ensure_schema(); print('db ok')"

cd ../frontend
npm install
npm run build
```

## 提交前自检

```bash
git status
git diff -- .gitignore backend/.env.local.example frontend/.env.local.example
git ls-files | grep -E '(^|/)(\\.env.local|\\.mysql-|node_modules|\\.venv|__pycache__|app/temp)'
```

最后一条如果输出真实 `.env.local`、密码文件或临时目录，必须立即处理。当前它也会输出已经被历史提交跟踪的 `frontend/node_modules`；这是已知仓库遗留，不应误判为本次新提交才引入。

## 处理误提交密钥

如果真实配置已经被 `git add` 但还没提交：

```bash
git restore --staged backend/.env.local frontend/.env.local
```

如果已经提交到 GitHub，需要立刻更换密码或密钥；历史提交里的密钥不能只靠删除文件解决。
