import base64
import shutil
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageSequence

from app.core.exceptions import AppException
from app.tools.svg_image_converter import _render_svg_to_png_bytes
from app.utils.image_utils import load_image, save_image, zip_output_files


TOOL_META = {
    "slug": "image-format-converter",
    "name": "常见图片格式互转",
    "category": "format",
    "input_mode": "file",
    "result_type": "file",
}

COMMON_OUTPUT_FORMATS = {
    "jpg": "JPEG",
    "png": "PNG",
    "webp": "WEBP",
    "bmp": "BMP",
    "tiff": "TIFF",
    "gif": "GIF",
}
COMMON_INPUT_SUFFIXES = {"jpg", "jpeg", "png", "webp", "bmp", "tif", "tiff", "gif", "svg"}
RASTER_INPUT_SUFFIXES = COMMON_INPUT_SUFFIXES - {"svg"}
MIME_TYPES = {
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "png": "image/png",
    "webp": "image/webp",
    "bmp": "image/bmp",
    "tif": "image/tiff",
    "tiff": "image/tiff",
    "gif": "image/gif",
}


def run(input_path: str, output_dir: str, output_format: str = "png", **_: dict) -> str:
    try:
        return _run(input_path, output_dir, output_format)
    except AppException:
        raise
    except Exception as exc:
        raise AppException(
            message="图片格式转换失败：当前图片格式与目标格式可能不兼容，请尝试改用 PNG、JPG 或 WebP 输出。",
            code=4002,
            status_code=400,
        ) from exc


def _run(input_path: str, output_dir: str, output_format: str = "png") -> str:
    source = Path(input_path)
    suffix = _normalize_output_format(output_format)
    source_suffix = _normalize_source_suffix(source)

    if source_suffix != "svg" and _is_multi_frame_image(source):
        return _animated_image_to_zip(source, output_dir, suffix)

    if suffix == "svg":
        if source_suffix == "svg":
            target_path = Path(output_dir) / "converted.svg"
            shutil.copyfile(source, target_path)
            return str(target_path)
        return _raster_to_svg(source, output_dir, source_suffix)

    image = _load_static_image(source, source_suffix)
    target_path = Path(output_dir) / f"converted.{suffix}"
    quality = 92 if suffix in {"jpg", "webp"} else None
    return save_image(image, target_path, COMMON_OUTPUT_FORMATS[suffix], quality=quality)


def _normalize_output_format(output_format: str) -> str:
    normalized = str(output_format or "png").strip().lower()
    if normalized == "jpeg":
        return "jpg"
    if normalized == "tif":
        return "tiff"
    if normalized not in {*COMMON_OUTPUT_FORMATS, "svg"}:
        raise AppException(message="不支持的图片输出格式", code=4001, status_code=400)
    return normalized


def _normalize_source_suffix(source: Path) -> str:
    suffix = source.suffix.lower().lstrip(".")
    if suffix == "jpeg":
        return "jpg"
    if suffix not in COMMON_INPUT_SUFFIXES:
        raise AppException(
            message="常见图片格式互转仅支持 PNG、JPG、WebP、BMP、TIFF、GIF、SVG，请使用对应专用工具处理 ICO、ICNS 等格式。",
            code=4002,
            status_code=400,
        )
    return suffix


def _load_static_image(source: Path, source_suffix: str) -> Image.Image:
    if source_suffix == "svg":
        rendered = Image.open(BytesIO(_render_svg_to_png_bytes(source)))
        rendered.load()
        return rendered
    if source_suffix not in RASTER_INPUT_SUFFIXES:
        raise AppException(message="不支持的图片输入格式", code=4002, status_code=400)
    return load_image(source)


def _raster_to_svg(source: Path, output_dir: str, source_suffix: str) -> str:
    if source_suffix not in RASTER_INPUT_SUFFIXES:
        raise AppException(message="当前方向请上传普通静态图片文件", code=4002, status_code=400)

    image = load_image(source)
    width, height = image.size
    encoded = base64.b64encode(source.read_bytes()).decode("ascii")
    mime_type = MIME_TYPES[source_suffix]
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}">\n'
        f'  <image width="{width}" height="{height}" href="data:{mime_type};base64,{encoded}" />\n'
        "</svg>\n"
    )

    target_path = Path(output_dir) / "converted.svg"
    target_path.write_text(svg, encoding="utf-8")
    return str(target_path)


def _is_multi_frame_image(source: Path) -> bool:
    try:
        with Image.open(source) as image:
            return bool(getattr(image, "is_animated", False)) and int(getattr(image, "n_frames", 1)) > 1
    except Exception:
        return False


def _animated_image_to_zip(source: Path, output_dir: str, suffix: str) -> str:
    frames_dir = Path(output_dir) / "frames"
    frames_dir.mkdir(parents=True, exist_ok=True)
    try:
        with Image.open(source) as image:
            for index, frame in enumerate(ImageSequence.Iterator(image), start=1):
                frame_image = frame.convert("RGBA")
                target_path = frames_dir / f"frame-{index:03d}.{suffix}"
                if suffix == "svg":
                    _image_frame_to_svg(frame_image, target_path)
                else:
                    quality = 92 if suffix in {"jpg", "webp"} else None
                    save_image(frame_image, target_path, COMMON_OUTPUT_FORMATS[suffix], quality=quality)
    except AppException:
        raise
    except Exception as exc:
        raise AppException(
            message="动图逐帧转换失败：当前动图帧与目标格式可能不兼容，请尝试输出 PNG 或 JPG 序列帧。",
            code=4002,
            status_code=400,
        ) from exc

    return zip_output_files(frames_dir, Path(output_dir) / "converted_frames.zip")


def _image_frame_to_svg(image: Image.Image, target_path: Path) -> None:
    stream = BytesIO()
    image.save(stream, format="PNG")
    encoded = base64.b64encode(stream.getvalue()).decode("ascii")
    width, height = image.size
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}">\n'
        f'  <image width="{width}" height="{height}" href="data:image/png;base64,{encoded}" />\n'
        "</svg>\n"
    )
    target_path.write_text(svg, encoding="utf-8")
