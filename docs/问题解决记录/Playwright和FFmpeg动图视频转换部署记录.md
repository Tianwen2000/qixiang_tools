# Playwright 和 FFmpeg 动图视频转换部署记录

## 背景

SVG 动图转 GIF、动图截图、音视频转换会用到浏览器渲染能力和 FFmpeg 能力：

- Playwright：启动 Chromium，渲染动画 SVG 并逐帧截图。
- imageio-ffmpeg：提供完整 ffmpeg 二进制，处理 MP3、FLAC、WAV、MOV、MP4、GIF 等音视频转换。

如果服务器缺少 Chromium 内核，工具会提示需要安装：

```bash
python -m playwright install chromium
```

## 本地或服务器安装依赖

进入项目根目录：

```bash
cd /home/ubuntu/qixiang_tools
```

安装 Python 依赖：

```bash
./backend/.server-venv/bin/pip install -r backend/requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

安装 Playwright 浏览器内核：

```bash
PLAYWRIGHT_DOWNLOAD_HOST=https://npmmirror.com/mirrors/playwright \
./backend/.server-venv/bin/python -m playwright install chromium
```

说明：

- 当前项目依赖里固定了 `playwright==1.48.0`，对应 Chromium build `1140`，国内镜像可以正常下载。
- Playwright 会同时下载一个自带 FFmpeg，但这个版本偏浏览器辅助用途，不作为音视频转换工具的主要 ffmpeg。
- 音视频转换工具优先使用系统 `ffmpeg`；系统没有时，自动使用 `imageio-ffmpeg` 随 Python 依赖安装的 ffmpeg。

## 推荐服务器缓存目录

如果希望浏览器内核放到项目目录，先指定缓存路径再安装：

```bash
cd /home/ubuntu/qixiang_tools
mkdir -p /home/ubuntu/qixiang_tools/.playwright-browsers

PLAYWRIGHT_BROWSERS_PATH=/home/ubuntu/qixiang_tools/.playwright-browsers \
PLAYWRIGHT_DOWNLOAD_HOST=https://npmmirror.com/mirrors/playwright \
./backend/.server-venv/bin/python -m playwright install chromium
```

安装后应能看到类似目录：

```bash
ls -la /home/ubuntu/qixiang_tools/.playwright-browsers
```

常见结果：

```text
chromium-1140
ffmpeg-1010
.links
```

这里的 `ffmpeg-1010` 属于 Playwright 缓存；MP3、MP4 等音视频转换实际优先使用系统 `ffmpeg` 或 `imageio-ffmpeg`。

## systemd 环境变量

如果后端由 systemd 启动，需要让服务进程也能读到同一个浏览器缓存目录。

编辑服务覆盖配置：

```bash
sudo EDITOR=vim systemctl edit qixiang-backend
```

在文件顶部可编辑区域写入：

```ini
[Service]
Environment=PLAYWRIGHT_BROWSERS_PATH=/home/ubuntu/qixiang_tools/.playwright-browsers
```

保存后执行：

```bash
sudo systemctl daemon-reload
sudo systemctl restart qixiang-backend
```

确认环境变量已经进入服务进程：

```bash
systemctl show qixiang-backend -p Environment --no-pager
```

还可以直接看进程环境：

```bash
PID=$(systemctl show -p MainPID --value qixiang-backend)
sudo tr '\0' '\n' < /proc/$PID/environ | grep PLAYWRIGHT
```

## 验证 Chromium 是否可用

在服务器上执行：

```bash
cd /home/ubuntu/qixiang_tools

PLAYWRIGHT_BROWSERS_PATH=/home/ubuntu/qixiang_tools/.playwright-browsers \
./backend/.server-venv/bin/python - <<'PY'
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()
    browser.close()

print("ok")
PY
```

输出 `ok` 表示 Chromium 可以被当前 Python 环境调用。

## 验证音视频 FFmpeg 是否可用

音视频转换工具会优先找系统 `ffmpeg`，找不到时使用 `imageio-ffmpeg`。

```bash
cd /home/ubuntu/qixiang_tools

./backend/.server-venv/bin/python - <<'PY'
from app.tools.media_converter import _resolve_ffmpeg_path

print(_resolve_ffmpeg_path())
PY
```

输出非空路径表示音视频转换工具可以调用 ffmpeg。

## 同步和异步问题

FastAPI 接口运行在 asyncio 事件循环里，不能直接在接口协程里调用 Playwright 的 Sync API，否则会报：

```text
It looks like you are using Playwright Sync API inside the asyncio loop.
Please use the Async API instead.
```

当前项目处理方式：

- 后端接口仍保持现有同步工具函数结构。
- 动画 SVG 转 GIF 时，把 Playwright Sync API 放到独立线程里执行。
- 线程里完成 Chromium 启动、逐帧截图，再回到主流程用 PIL 写出 GIF。

开发时注意：

- 不要在 FastAPI async 调用链里直接执行 `sync_playwright()`。
- 要么改用 Playwright Async API，要么像当前实现一样放进独立线程。

## 接口级验证命令

用 curl 或 Python 请求真实接口，确认返回的是 GIF 文件，而不是 JSON 报错。

```bash
cd /home/ubuntu/qixiang_tools

cat > /tmp/animated.svg <<'SVG'
<svg xmlns="http://www.w3.org/2000/svg" width="80" height="40" viewBox="0 0 80 40">
  <circle cx="12" cy="20" r="10" fill="#f5a22f">
    <animate attributeName="cx" values="12;68;12" dur="1s" repeatCount="indefinite"/>
  </circle>
</svg>
SVG

curl -sS -D /tmp/headers.txt \
  --form 'file=@/tmp/animated.svg;type=image/svg+xml' \
  --form-string 'params={"direction":"svg_to_gif","duration_seconds":1,"fps":8}' \
  http://127.0.0.1:8000/api/tools/gif-svg-converter/upload \
  -o /tmp/out.gif

cat /tmp/headers.txt
file /tmp/out.gif
ls -lh /tmp/out.gif
```

正常结果应包含：

```text
HTTP/1.1 200 OK
content-type: image/gif
/tmp/out.gif: GIF image data
```

如果 `/tmp/out.gif` 是 JSON text data，说明接口返回了错误信息，继续执行：

```bash
cat /tmp/out.gif
```

## 常见问题

### 国内镜像 404

如果 `npmmirror` 下载某个新版 Chromium 404，优先确认 `backend/requirements.txt` 里的 Playwright 版本是否和服务器一致。

当前推荐：

```text
playwright==1.48.0
```

然后重新安装依赖和 Chromium。

### systemd 里可执行文件找不到浏览器

命令行测试能启动 Chromium，但网页接口仍提示未安装时，优先检查：

```bash
systemctl show qixiang-backend -p Environment --no-pager
```

确认包含：

```text
PLAYWRIGHT_BROWSERS_PATH=/home/ubuntu/qixiang_tools/.playwright-browsers
```

### 上传测试文件为空

如果接口报：

```text
Cannot open empty stream
```

先检查测试文件是否为空：

```bash
wc -c /tmp/animated.svg
cat /tmp/animated.svg
```

文件大小为 `0` 时，需要重新写入 SVG 测试内容。

## 更新部署简版流程

代码同步到服务器后：

```bash
cd /home/ubuntu/qixiang_tools

./backend/.server-venv/bin/pip install -r backend/requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

PLAYWRIGHT_BROWSERS_PATH=/home/ubuntu/qixiang_tools/.playwright-browsers \
PLAYWRIGHT_DOWNLOAD_HOST=https://npmmirror.com/mirrors/playwright \
./backend/.server-venv/bin/python -m playwright install chromium

sudo systemctl daemon-reload
sudo systemctl restart qixiang-backend
sudo systemctl status qixiang-backend --no-pager
```

最后用接口级验证命令确认 SVG 动图转 GIF 和音视频转换可用。
