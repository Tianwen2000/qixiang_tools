# GitHub 上传与配置模板说明

> 目标：尽量把项目源码、文档、静态资源、配置模板都放到 GitHub；真实密钥、真实密码、数据库数据和本地生成产物不提交。这样别人 clone 后，按 example 文件补齐配置就能运行。

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
frontend/index.html
frontend/package.json
frontend/package-lock.json
frontend/vite.config.js
frontend/.env.example
```

这些文件属于源码、文档、静态素材或可公开模板，应该提交。

## 不建议提交的内容

```text
.env
backend/.env
frontend/.env
backend/.mysql-*
backend/.venv/
frontend/node_modules/
frontend/dist/
backend/app/temp/
__pycache__/
*.pyc
*.log
.DS_Store
```

原因：

- `.env`、`.mysql-*` 可能包含数据库账号、后台密码、Cookie 配置。
- `.venv`、`node_modules` 可以通过依赖文件重新安装。
- `dist` 是构建产物，代码仓库里一般只保留源码；部署服务器上可保留。
- `backend/app/temp` 是上传和转换输出的临时文件。
- 缓存、日志、系统文件没有长期维护价值。

## 当前 .gitignore 重点

```gitignore
.DS_Store
.vscode/
__pycache__/
*.py[cod]
.venv/
backend/app/temp/
*.log
.env
backend/.env
backend/.mysql-*
```

这套规则的核心是保护真实配置和本地生成文件。后续如果新增本地密钥文件，也要追加到 `.gitignore`。

## 后端配置模板

后端已经有 `backend/.env.example`。新机器运行时复制一份：

```bash
cp backend/.env.example backend/.env
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
cp frontend/.env.example frontend/.env
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

cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env

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
git diff -- .gitignore backend/.env.example frontend/.env.example
git ls-files | grep -E '(^|/)(\\.env|\\.mysql-|node_modules|\\.venv|__pycache__|app/temp)'
```

最后一条如果输出了真实 `.env`、密码文件、依赖目录或临时目录，就说明 `.gitignore` 或暂存区需要处理。

## 处理误提交密钥

如果真实配置已经被 `git add` 但还没提交：

```bash
git restore --staged backend/.env frontend/.env
```

如果已经提交到 GitHub，需要立刻更换密码或密钥；历史提交里的密钥不能只靠删除文件解决。
