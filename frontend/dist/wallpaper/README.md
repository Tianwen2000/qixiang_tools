# 四季壁纸素材

全站四季背景由 `SiteWallpaper.vue` 统一管理。当前策略是：手机端始终使用静态图；桌面端先显示静态图，页面加载完成并进入空闲阶段后再加载视频，视频预热后淡入。开启 `prefers-reduced-motion` 时只使用静态图。

## 需要的文件（文件名必须一致）

| 季节 | 桌面视频 | 静态图（必需） |
|------|----------|----------------|
| 春   | `spring.mp4` | `spring.jpg` |
| 夏   | `summer.mp4` | `summer.jpg` |
| 秋   | `autumn.mp4` | `autumn.jpg` |
| 冬   | `winter.mp4` | `winter.jpg` |

- 固定引用路径为 `/wallpaper/<season>.mp4` 和 `/wallpaper/<season>.jpg`，文件名无需配置。
- `.jpg` 是手机端常驻背景，也是桌面端首屏、视频预热、加载失败、解码失败或自动播放受限时的兜底，因此四张静态图必须提供。
- `.mp4` 只在桌面端、未开启减少动态效果时延迟加载；缺少视频不会影响页面使用。

## 压缩 / 规格建议（关键，关系到流量和流畅度）

- 分辨率：**1080p（1920×1080）** 足够；背景使用覆盖裁切，不需要单独提供竖版视频。
- 编码：**H.264 (yuv420p)** + faststart。当前组件只引用 MP4，没有配置 WebM source。
- 时长：**6–12 秒无缝循环**即可，循环点要接得上。
- 码率：尽量压到 **每段 ≤ 1.5–2.5MB**（CRF 26–30）。背景视频不需要高码率。
- 必须静音（背景无声），代码已设 `muted / loop / playsinline / autoplay`。

参考 ffmpeg 压缩命令：

```bash
ffmpeg -i 原始.mp4 -t 10 -an -vf "scale=1920:-2" \
  -c:v libx264 -profile:v high -pix_fmt yuv420p -crf 28 -movflags +faststart spring.mp4
# 顺手导出 poster 首帧
ffmpeg -i spring.mp4 -frames:v 1 -q:v 3 spring.jpg
```

## 加载与回退行为

- 手机端不创建 `<video>`，也不会下载 MP4。
- 桌面端首屏显示 JPG，浏览器空闲后才开始加载 MP4；视频完成预热后再淡入。
- 视频缺失、格式不支持、解码失败或自动播放受限时继续保留 JPG，不会白屏。
- `prefers-reduced-motion: reduce` 下不加载视频，只显示 JPG。
- 代码中仍保留 CSS 季节场景组件，但当前常规四季模式始终启用静态图，因此 CSS 动态场景不会进入实际回退链。
