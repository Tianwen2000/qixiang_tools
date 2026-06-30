"""文件说明：实现「图片加水印」工具的后端逻辑。"""

from pathlib import Path

from app.core.exceptions import AppException
from app.utils.image_utils import IMAGE_FORMATS, draw_text_overlay, load_image, save_image


TOOL_META = {
    "slug": "image-watermarker",
    "name": "图片加水印",
    "category": "image",
    "input_mode": "file",
    "result_type": "file",
}


def run(
    input_path: str,
    output_dir: str,
    filename: str = "",
    text: str = "",
    position: str = "bottom_right",
    opacity: int = 45,
    font_size: int = 32,
    color: str = "#ffffff",
    **_: dict,
) -> str:
    if not text.strip():
        raise AppException(message="请输入水印文字", code=4001, status_code=400)
    image = load_image(input_path)
    processed = draw_text_overlay(image, text.strip(), position, int(font_size), color, int(opacity))
    suffix = Path(filename or input_path).suffix.lower().lstrip(".") or "png"
    target_format = IMAGE_FORMATS.get(suffix, "PNG")
    target_path = Path(output_dir) / f"watermarked.{suffix}"
    return save_image(processed, target_path, target_format)
