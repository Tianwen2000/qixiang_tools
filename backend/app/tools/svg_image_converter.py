import base64
import threading
from io import BytesIO
from pathlib import Path
from xml.etree import ElementTree

import fitz
from PIL import Image

from app.core.exceptions import AppException
from app.utils.image_utils import ensure_rgb, load_image, save_image


PAIR_CONFIG = {
    "jpg": {
        "input_suffixes": {"jpg", "jpeg"},
        "mime_type": "image/jpeg",
        "suffix_label": ".jpg/.jpeg",
    },
    "png": {
        "input_suffixes": {"png"},
        "mime_type": "image/png",
        "suffix_label": ".png",
    },
    "gif": {
        "input_suffixes": {"gif"},
        "mime_type": "image/gif",
        "suffix_label": ".gif",
    },
}


def convert_svg_image(input_path: str, output_dir: str, direction: str, pair: str, **params: object) -> str:
    if pair not in PAIR_CONFIG:
        raise AppException(message="不支持的图片格式", code=4001, status_code=400)

    if direction == f"{pair}_to_svg":
        return _raster_to_svg(input_path, output_dir, pair)
    if direction == f"svg_to_{pair}":
        return _svg_to_raster(input_path, output_dir, pair, **params)

    raise AppException(message="不支持的转换方向", code=4001, status_code=400)


def _raster_to_svg(input_path: str, output_dir: str, pair: str) -> str:
    source = Path(input_path)
    config = PAIR_CONFIG[pair]
    source_suffix = source.suffix.lower().lstrip(".")
    if source_suffix not in config["input_suffixes"]:
        raise AppException(message=f"当前方向请上传 {config['suffix_label']} 文件", code=4002, status_code=400)

    image = load_image(source)
    width, height = image.size
    encoded = base64.b64encode(source.read_bytes()).decode("ascii")
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}">\n'
        f'  <image width="{width}" height="{height}" href="data:{config["mime_type"]};base64,{encoded}" />\n'
        "</svg>\n"
    )

    target_path = Path(output_dir) / "converted.svg"
    target_path.write_text(svg, encoding="utf-8")
    return str(target_path)


def _svg_to_raster(input_path: str, output_dir: str, pair: str, **params: object) -> str:
    source = Path(input_path)
    if source.suffix.lower() != ".svg":
        raise AppException(message="当前方向请上传 .svg 文件", code=4002, status_code=400)

    target_path = Path(output_dir) / f"converted.{pair}"
    svg_text = source.read_text(encoding="utf-8", errors="replace")
    if pair == "gif" and _svg_has_animation(svg_text):
        return _render_animated_svg_to_gif(
            source,
            target_path,
            duration_seconds=_normalize_duration(params.get("duration_seconds", 2)),
            fps=_normalize_fps(params.get("fps", 12)),
        )

    png_bytes = _render_svg_to_png_bytes(source)
    return _save_rendered_png_bytes(png_bytes, target_path, pair)


def _svg_has_animation(svg_text: str) -> bool:
    lowered = svg_text.lower()
    return any(
        marker in lowered
        for marker in (
            "<animate",
            "<animatemotion",
            "<animatetransform",
            "<set",
            "@keyframes",
            "animation:",
            "animation-name:",
        )
    )


def _normalize_duration(value: object) -> float:
    try:
        duration = float(value)
    except (TypeError, ValueError):
        raise AppException(message="动画时长参数无效", code=4001, status_code=400)
    if duration < 0.5 or duration > 8:
        raise AppException(message="动画时长需在 0.5 到 8 秒之间", code=4001, status_code=400)
    return duration


def _normalize_fps(value: object) -> int:
    try:
        fps = int(value)
    except (TypeError, ValueError):
        raise AppException(message="动画帧率参数无效", code=4001, status_code=400)
    if fps < 4 or fps > 24:
        raise AppException(message="动画帧率需在 4 到 24 FPS 之间", code=4001, status_code=400)
    return fps


def _render_svg_to_png_bytes(source: Path) -> bytes:
    svg_text = source.read_text(encoding="utf-8", errors="replace")
    try:
        from resvg_py import svg_to_bytes

        return svg_to_bytes(svg_string=svg_text)
    except Exception:
        return _render_svg_with_fitz(source.read_bytes())


def _render_svg_with_fitz(svg_bytes: bytes) -> bytes:
    try:
        document = fitz.open(stream=svg_bytes, filetype="svg")
        if document.page_count < 1:
            raise ValueError("SVG 中没有可渲染页面")
        pixmap = document[0].get_pixmap(alpha=True)
        return pixmap.tobytes("png")
    except Exception as exc:
        raise AppException(message=f"无法渲染 SVG 文件：{exc}", code=4002, status_code=400) from exc


def _render_animated_svg_to_gif(source: Path, target_path: Path, duration_seconds: float, fps: int) -> str:
    try:
        from playwright.sync_api import Error as PlaywrightError
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise AppException(
            message="动画 SVG 转 GIF 需要安装 Playwright：pip install playwright && python -m playwright install chromium",
            code=5004,
            status_code=500,
        ) from exc

    svg_text = source.read_text(encoding="utf-8", errors="replace")
    width, height = _svg_canvas_size(svg_text)
    frame_count = max(1, min(int(duration_seconds * fps), 120))
    frame_delay_ms = max(20, round(1000 / fps))
    html = (
        "<!doctype html><html><head><meta charset='utf-8'>"
        "<style>html,body{margin:0;padding:0;background:transparent;overflow:hidden;}"
        f"svg{{display:block;width:{width}px;height:{height}px;}}</style>"
        "</head><body>"
        f"{svg_text}"
        "</body></html>"
    )

    try:
        frames = _capture_animated_svg_frames(sync_playwright, html, width, height, frame_count, frame_delay_ms)
    except PlaywrightError as exc:
        raise AppException(
            message=f"动画 SVG 转 GIF 浏览器渲染失败：{_format_playwright_error(exc)}",
            code=5004,
            status_code=500,
        ) from exc
    except Exception as exc:
        raise AppException(
            message=f"动画 SVG 转 GIF 处理失败：{_format_playwright_error(exc)}",
            code=5004,
            status_code=500,
        ) from exc

    return save_image(
        frames[0],
        target_path,
        "GIF",
        preserve_animation=True,
        frames=frames,
        durations=[frame_delay_ms] * len(frames),
        loop=0,
    )


def _capture_animated_svg_frames(
    sync_playwright,
    html: str,
    width: int,
    height: int,
    frame_count: int,
    frame_delay_ms: int,
) -> list[Image.Image]:
    result: dict[str, object] = {}

    def worker() -> None:
        browser = None
        frames: list[Image.Image] = []
        try:
            with sync_playwright() as playwright:
                browser = playwright.chromium.launch(args=["--no-sandbox", "--disable-dev-shm-usage"])
                page = browser.new_page(viewport={"width": width, "height": height}, device_scale_factor=1)
                page.set_content(html, wait_until="load")
                for index in range(frame_count):
                    if index:
                        page.wait_for_timeout(frame_delay_ms)
                    frame = Image.open(BytesIO(page.screenshot(type="png", omit_background=True)))
                    frame.load()
                    frames.append(frame.convert("RGBA"))
            result["frames"] = frames
        except Exception as exc:
            result["error"] = exc
        finally:
            if browser is not None:
                try:
                    browser.close()
                except Exception:
                    pass

    thread = threading.Thread(target=worker)
    thread.start()
    thread.join()

    error = result.get("error")
    if isinstance(error, Exception):
        raise error
    frames = result.get("frames")
    if not isinstance(frames, list) or not frames:
        raise RuntimeError("未生成有效动画帧")
    return frames


def _format_playwright_error(exc: Exception) -> str:
    detail = str(exc).strip() or exc.__class__.__name__
    detail = " ".join(detail.split())
    if len(detail) > 500:
        detail = f"{detail[:500]}..."
    return detail


def _svg_canvas_size(svg_text: str) -> tuple[int, int]:
    try:
        root = ElementTree.fromstring(svg_text)
    except ElementTree.ParseError:
        return 512, 512

    width = _svg_length_to_int(root.attrib.get("width", ""))
    height = _svg_length_to_int(root.attrib.get("height", ""))
    if width and height:
        return _clamp_canvas_size(width, height)

    view_box = root.attrib.get("viewBox") or root.attrib.get("viewbox") or ""
    parts = view_box.replace(",", " ").split()
    if len(parts) == 4:
        try:
            return _clamp_canvas_size(int(float(parts[2])), int(float(parts[3])))
        except ValueError:
            pass

    return 512, 512


def _svg_length_to_int(value: str) -> int:
    cleaned = value.strip().lower().replace("px", "")
    try:
        return int(float(cleaned))
    except ValueError:
        return 0


def _clamp_canvas_size(width: int, height: int) -> tuple[int, int]:
    width = max(1, width)
    height = max(1, height)
    max_side = 2048
    if width <= max_side and height <= max_side:
        return width, height
    scale = max_side / max(width, height)
    return max(1, round(width * scale)), max(1, round(height * scale))


def _save_rendered_png_bytes(png_bytes: bytes, target_path: Path, pair: str) -> str:
    image = Image.open(BytesIO(png_bytes))
    image.load()
    if pair == "jpg":
        return save_image(ensure_rgb(image), target_path, "JPEG", quality=92)
    if pair == "gif":
        return save_image(image.convert("RGBA"), target_path, "GIF")
    return save_image(image.convert("RGBA"), target_path, "PNG")
