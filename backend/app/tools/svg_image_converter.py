import base64
from io import BytesIO
from pathlib import Path

import fitz
from PIL import Image
from resvg_py import svg_to_bytes

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
}


def convert_svg_image(input_path: str, output_dir: str, direction: str, pair: str) -> str:
    if pair not in PAIR_CONFIG:
        raise AppException(message="不支持的图片格式", code=4001, status_code=400)

    if direction == f"{pair}_to_svg":
        return _raster_to_svg(input_path, output_dir, pair)
    if direction == f"svg_to_{pair}":
        return _svg_to_raster(input_path, output_dir, pair)

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


def _svg_to_raster(input_path: str, output_dir: str, pair: str) -> str:
    source = Path(input_path)
    if source.suffix.lower() != ".svg":
        raise AppException(message="当前方向请上传 .svg 文件", code=4002, status_code=400)

    png_bytes = _render_svg_to_png_bytes(source)
    target_path = Path(output_dir) / f"converted.{pair}"
    return _save_rendered_png_bytes(png_bytes, target_path, pair)


def _render_svg_to_png_bytes(source: Path) -> bytes:
    svg_text = source.read_text(encoding="utf-8", errors="replace")
    try:
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


def _save_rendered_png_bytes(png_bytes: bytes, target_path: Path, pair: str) -> str:
    image = Image.open(BytesIO(png_bytes))
    image.load()
    if pair == "jpg":
        return save_image(ensure_rgb(image), target_path, "JPEG", quality=92)
    return save_image(image.convert("RGBA"), target_path, "PNG")
