"""文件说明：实现「SVG 动图拆分和合成」工具的后端逻辑。"""

import base64
from pathlib import Path

from PIL import Image

from app.core.exceptions import AppException
from app.tools.animated_frames_converter import (
    MAX_ANIMATION_PIXELS,
    MAX_COMPOSE_IMAGES,
    _normalize_image_sequence,
    _safe_extract_image_zip,
)
from app.tools.svg_image_converter import (
    _capture_animated_svg_frames,
    _format_playwright_error,
    _normalize_duration,
    _normalize_fps,
    _svg_canvas_size,
    _svg_has_animation,
)
from app.utils.image_utils import list_image_files, zip_output_files


TOOL_META = {
    "slug": "svg-animation-converter",
    "name": "SVG 动图拆分和合成",
    "category": "format",
    "input_mode": "file",
    "result_type": "file",
}


def run(
    input_path: str,
    output_dir: str,
    action: str = "split",
    duration_seconds: str | int | float = 2,
    fps: str | int = 12,
    **_: dict,
) -> str:
    if action == "split":
        return _split_svg_animation(input_path, output_dir, duration_seconds, fps)
    if action == "compose":
        return _compose_svg_animation(input_path, output_dir, fps)
    raise AppException(message="不支持的操作类型", code=4001, status_code=400)


def _split_svg_animation(input_path: str, output_dir: str, duration_seconds: str | int | float, fps: str | int) -> str:
    source = Path(input_path)
    if source.suffix.lower() != ".svg":
        raise AppException(message="SVG 动图拆分请上传 .svg 文件。", code=4002, status_code=400)

    svg_text = source.read_text(encoding="utf-8", errors="replace")
    if not _svg_has_animation(svg_text):
        raise AppException(message="未检测到 SVG 动画内容，无法拆分。", code=4002, status_code=400)

    duration = _normalize_duration(duration_seconds)
    frame_rate = _normalize_fps(fps)
    width, height = _svg_canvas_size(svg_text)
    if width * height > MAX_ANIMATION_PIXELS:
        raise AppException(message="SVG 画布尺寸过大，请压缩后再上传。", code=4002, status_code=400)

    frame_count = max(1, min(int(duration * frame_rate), 120))
    frame_delay_ms = max(20, round(1000 / frame_rate))
    html = (
        "<!doctype html><html><head><meta charset='utf-8'>"
        "<style>html,body{margin:0;padding:0;background:transparent;overflow:hidden;}"
        f"svg{{display:block;width:{width}px;height:{height}px;}}</style>"
        "</head><body>"
        f"{svg_text}"
        "</body></html>"
    )

    sync_playwright = None
    playwright_error_type: type[Exception] = Exception
    # 生产运行使用真实 Playwright；测试会替换捕获函数，此时不提前要求本机安装浏览器依赖。
    if getattr(_capture_animated_svg_frames, "__module__", "") == "app.tools.svg_image_converter":
        try:
            from playwright.sync_api import Error as PlaywrightError
            from playwright.sync_api import sync_playwright as playwright_factory
        except ImportError as exc:
            raise AppException(
                message="SVG 动图拆分需要安装 Playwright：pip install playwright && python -m playwright install chromium",
                code=5004,
                status_code=500,
            ) from exc
        sync_playwright = playwright_factory
        playwright_error_type = PlaywrightError

    try:
        frames = _capture_animated_svg_frames(sync_playwright, html, width, height, frame_count, frame_delay_ms)
    except playwright_error_type as exc:
        raise AppException(message=f"SVG 动图拆分浏览器渲染失败：{_format_playwright_error(exc)}", code=5004, status_code=500) from exc
    except Exception as exc:
        raise AppException(message=f"SVG 动图拆分失败：{_format_playwright_error(exc)}", code=5004, status_code=500) from exc

    frame_dir = Path(output_dir) / "svg-frames"
    frame_dir.mkdir(parents=True, exist_ok=True)
    for index, frame in enumerate(frames, start=1):
        frame.save(frame_dir / f"frame-{index:04d}.png", format="PNG")

    return zip_output_files(frame_dir, Path(output_dir) / "svg-animation-frames.zip", "*.png")


def _compose_svg_animation(input_path: str, output_dir: str, fps: str | int) -> str:
    source = Path(input_path)
    if source.suffix.lower().lstrip(".") != "zip":
        raise AppException(message="合成 SVG 动图请上传包含多张图片的 ZIP 压缩包。", code=4002, status_code=400)

    frame_rate = _normalize_compose_fps(fps)
    extracted = _safe_extract_image_zip(source, Path(output_dir) / "svg-compose-src")
    image_paths = sorted(list_image_files(extracted), key=lambda path: path.name.lower())
    if len(image_paths) < 2:
        raise AppException(message="请上传至少包含 2 张图片的 ZIP 压缩包。", code=4002, status_code=400)
    if len(image_paths) > MAX_COMPOSE_IMAGES:
        raise AppException(message=f"图片数量过多，最多支持 {MAX_COMPOSE_IMAGES} 张图片合成。", code=4002, status_code=400)

    sequence_dir = Path(output_dir) / "svg-compose-frames"
    sequence_dir.mkdir(parents=True, exist_ok=True)
    _normalize_image_sequence(image_paths, sequence_dir)
    frame_paths = sorted(sequence_dir.glob("*.png"))
    if len(frame_paths) < 2:
        raise AppException(message="请上传至少包含 2 张图片的 ZIP 压缩包。", code=4002, status_code=400)

    with Image.open(frame_paths[0]) as first_frame:
        width, height = first_frame.size
    if width * height > MAX_ANIMATION_PIXELS:
        raise AppException(message="图片尺寸过大，请压缩后再上传。", code=4002, status_code=400)

    target_path = Path(output_dir) / "generated.svg"
    target_path.write_text(_build_animated_svg(frame_paths, width, height, frame_rate), encoding="utf-8")
    return str(target_path)


def _normalize_compose_fps(value: str | int) -> int:
    try:
        fps = int(value)
    except (TypeError, ValueError) as exc:
        raise AppException(message="FPS 必须是有效整数。", code=4001, status_code=400) from exc
    if fps < 1 or fps > 24:
        raise AppException(message="FPS 建议设置在 1 到 24 之间。", code=4001, status_code=400)
    return fps


def _build_animated_svg(frame_paths: list[Path], width: int, height: int, fps: int) -> str:
    frame_count = len(frame_paths)
    total_duration = frame_count / fps
    key_times = ";".join(_format_ratio(index / frame_count) for index in range(frame_count))
    key_times = f"{key_times};1"
    image_nodes: list[str] = []

    for frame_index, frame_path in enumerate(frame_paths):
        encoded = base64.b64encode(frame_path.read_bytes()).decode("ascii")
        values = ["1" if position % frame_count == frame_index else "0" for position in range(frame_count + 1)]
        opacity_values = ";".join(values)
        image_nodes.append(
            f'  <image width="{width}" height="{height}" href="data:image/png;base64,{encoded}" opacity="0">\n'
            f'    <animate attributeName="opacity" dur="{total_duration:.6f}s" repeatCount="indefinite" '
            f'calcMode="discrete" keyTimes="{key_times}" values="{opacity_values}" />\n'
            "  </image>"
        )

    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}">\n'
        + "\n".join(image_nodes)
        + "\n</svg>\n"
    )


def _format_ratio(value: float) -> str:
    if value <= 0:
        return "0"
    if value >= 1:
        return "1"
    return f"{value:.6f}".rstrip("0").rstrip(".")
