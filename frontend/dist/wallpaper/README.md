# 动态背景视频素材

全站背景已改为视频驱动（`SiteWallpaper.vue`）。把四季视频和静态兜底图放在本目录即可，文件名固定如下：

## 需要的文件（文件名必须一致）

| 季节 | 视频（必需） | 兜底静态图（强烈建议） |
|------|--------------|------------------------|
| 春   | `spring.mp4` | `spring.jpg` |
| 夏   | `summer.mp4` | `summer.jpg` |
| 秋   | `autumn.mp4` | `autumn.jpg` |
| 冬   | `winter.mp4` | `winter.jpg` |

- 引用路径是 `/wallpaper/<season>.mp4`，无需改代码，放进来就生效。
- `poster`（`.jpg`）用于视频加载前、解码失败、以及 **iOS 低电量模式禁止自动播放** 时的静态兜底，务必提供。

## 压缩 / 规格建议（关键，关系到流量和流畅度）

- 分辨率：**1080p（1920×1080）** 足够；竖屏手机用 `object-fit: cover` 裁切，无需单独出竖版。
- 编码：**H.264 (yuv420p)** + faststart，兼容性最好；可另出 `.webm`（VP9）做更小体积（需要的话告诉我加 `<source>`）。
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

## 没放视频时会怎样

视频缺失 / 格式不支持时，背景会**自动回退到原来的 CSS 动态背景**（不会白屏）。
所以放进来之前页面照常工作，放进来之后全平台（含手机）就切到流畅的视频背景。
