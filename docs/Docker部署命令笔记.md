# Docker 部署命令笔记

> 适用于当前 `qixiang_tools` 项目：后端 `FastAPI`，前端 `Vue 3 + Vite`；工具不依赖数据库，登录/AI 模块使用 MySQL。  
> 文档只写命令和必要配置，服务器 IP、账号、仓库地址都用占位符。

## 1. 首版部署

### 1.1 服务器安装 Docker

```bash
ssh ubuntu@<服务器IP>

curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker $USER
newgrp docker

docker version
docker compose version
```

### 1.2 拉取项目代码

推荐服务器直接用 git：

```bash
sudo mkdir -p /opt
sudo chown -R $USER:$USER /opt

cd /opt
git clone <你的仓库地址> qixiang_tools
cd /opt/qixiang_tools
```

如果服务器暂时不用 git，就从本地同步：

```bash
rsync -av --delete \
  --exclude '.git' \
  --exclude 'frontend/node_modules' \
  --exclude 'frontend/dist' \
  --exclude 'backend/.server-venv' \
  --exclude '__pycache__' \
  /Users/a123/PycharmProjects/qixiang_tools/ \
  ubuntu@<服务器IP>:/opt/qixiang_tools/
```

### 1.3 首次补 Docker 配置文件

项目根目录新增 `Dockerfile.backend`：

```dockerfile
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update \
  && apt-get install -y --no-install-recommends \
    ffmpeg \
    fonts-noto-cjk \
    libglib2.0-0 \
    libgl1 \
  && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

COPY backend /app/backend
WORKDIR /app/backend

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

新增 `frontend/Dockerfile`：

```dockerfile
FROM node:22-alpine AS build

WORKDIR /app

COPY frontend/package*.json ./
RUN npm ci

COPY frontend ./
RUN npm run build

FROM nginx:1.27-alpine

COPY deploy/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80
```

新增 `deploy/nginx.conf`：

```nginx
server {
  listen 80;
  server_name _;

  client_max_body_size 60m;

  root /usr/share/nginx/html;
  index index.html;

  location /api/ {
    proxy_pass http://backend:8000/api/;
    proxy_http_version 1.1;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_read_timeout 300s;
    proxy_send_timeout 300s;
  }

  location / {
    try_files $uri $uri/ /index.html;
  }
}
```

新增 `docker-compose.yml`：

```yaml
services:
  backend:
    build:
      context: .
      dockerfile: Dockerfile.backend
    container_name: qixiang-backend
    restart: unless-stopped
    environment:
      APP_ENV: production
      API_PREFIX: /api
      TEMP_DIR: /tmp/qixiang-tools
      MAX_UPLOAD_SIZE_MB: 50
    volumes:
      - qixiang-temp:/tmp/qixiang-tools
    healthcheck:
      test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/api/health', timeout=3)"]
      interval: 30s
      timeout: 5s
      retries: 3
      start_period: 20s

  web:
    build:
      context: .
      dockerfile: frontend/Dockerfile
    container_name: qixiang-web
    restart: unless-stopped
    depends_on:
      backend:
        condition: service_healthy
    ports:
      - "80:80"

volumes:
  qixiang-temp:
```

### 1.4 如果服务器已有旧部署，先停旧服务

旧部署通常是 `nginx + systemd qixiang-backend`，Docker 要占用 80 端口，旧 nginx 必须停掉：

```bash
sudo systemctl stop qixiang-backend || true
sudo systemctl disable qixiang-backend || true

sudo systemctl stop nginx || true
sudo systemctl disable nginx || true
```

如果服务器还要保留宿主机 nginx 做 HTTPS，那么不要让 Docker 直接占 80，把 `docker-compose.yml` 里的端口改成：

```yaml
ports:
  - "127.0.0.1:8080:80"
```

宿主机 nginx 再反代到：

```nginx
proxy_pass http://127.0.0.1:8080;
```

### 1.5 构建并启动

```bash
cd /opt/qixiang_tools

docker compose up -d --build
docker compose ps
```

### 1.6 验证

```bash
curl -s http://127.0.0.1/api/health
curl -I http://127.0.0.1/

docker compose logs --tail=80 backend
docker compose logs --tail=80 web
```

浏览器访问：

```text
http://<服务器IP>/
```

## 2. 后续更新

### 2.1 git 方式更新

```bash
ssh ubuntu@<服务器IP>
cd /opt/qixiang_tools

git pull

docker compose up -d --build
docker compose ps

curl -s http://127.0.0.1/api/health
docker image prune -f
```

### 2.2 rsync 方式更新

本地执行：

```bash
rsync -av --delete \
  --exclude '.git' \
  --exclude 'frontend/node_modules' \
  --exclude 'frontend/dist' \
  --exclude 'backend/.server-venv' \
  --exclude '__pycache__' \
  /Users/a123/PycharmProjects/qixiang_tools/ \
  ubuntu@<服务器IP>:/opt/qixiang_tools/
```

服务器执行：

```bash
ssh ubuntu@<服务器IP>
cd /opt/qixiang_tools

docker compose up -d --build
docker compose ps

curl -s http://127.0.0.1/api/health
docker image prune -f
```

## 3. 常用运维命令

看容器状态：

```bash
cd /opt/qixiang_tools
docker compose ps
```

看日志：

```bash
docker compose logs -f backend
docker compose logs -f web
```

重启：

```bash
docker compose restart
```

只重启后端：

```bash
docker compose restart backend
```

停止：

```bash
docker compose down
```

重新完整构建：

```bash
docker compose build --no-cache
docker compose up -d
```

清理无用镜像：

```bash
docker image prune -f
```

## 4. 回滚

git 部署时：

```bash
cd /opt/qixiang_tools

git log --oneline -5
git checkout <要回滚的commit>

docker compose up -d --build
curl -s http://127.0.0.1/api/health
```

回到最新版本：

```bash
git checkout main
git pull
docker compose up -d --build
```

## 5. 注意事项

- Docker 方式不需要在服务器手动 `npm run build`，前端构建会在 `frontend/Dockerfile` 里完成。
- 音视频互转工具依赖 `ffmpeg`，所以后端镜像里必须安装 `ffmpeg`。
- 中文图片、水印、证书等工具可能用到中文字体，所以后端镜像里安装 `fonts-noto-cjk`。
- 登录/AI 模块需要 MySQL：可连宿主机已装的 MySQL，或在 `docker-compose.yml` 里新增 `mysql` 服务，并给后端配 `DATABASE_URL` 等环境变量（见 [AI 助手与登录系统说明](./AI助手与登录系统说明.md)）；其余工具不需要数据库。
- 如果以后还要缓存等能力，再按需新增 `redis` 服务。
