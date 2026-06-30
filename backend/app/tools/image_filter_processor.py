"""文件说明：实现「图片滤镜处理」工具的后端逻辑。"""

from pathlib import Path

from PIL import ImageFilter, ImageOps

from app.core.exceptions import AppException
from app.utils.image_utils import IMAGE_FORMATS, load_image, save_image


TOOL_META = {
    "slug": "image-filter-processor",
    "name": "图片滤镜处理",
    "category": "image",
    "input_mode": "file",
    "result_type": "file",
}


def run(input_path: str, output_dir: str, filename: str = "", filter_name: str = "grayscale", **_: dict) -> str:
    image = load_image(input_path)
    if filter_name == "grayscale":
        processed = ImageOps.grayscale(image)
    elif filter_name == "blur":
        processed = image.filter(ImageFilter.GaussianBlur(radius=2))
    elif filter_name == "sharpen":
        processed = image.filter(ImageFilter.SHARPEN)
    elif filter_name == "detail":
        processed = image.filter(ImageFilter.DETAIL)
    elif filter_name == "contour":
        processed = image.filter(ImageFilter.CONTOUR)
    elif filter_name == "emboss":
        processed = image.filter(ImageFilter.EMBOSS)
    else:
        raise AppException(message="不支持的滤镜类型", code=4001, status_code=400)

    suffix = Path(filename or input_path).suffix.lower().lstrip(".") or "png"
    target_format = IMAGE_FORMATS.get(suffix, "PNG")
    target_path = Path(output_dir) / f"filtered.{suffix}"
    return save_image(processed, target_path, target_format)
