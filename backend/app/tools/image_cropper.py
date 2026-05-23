from pathlib import Path

from app.core.exceptions import AppException
from app.utils.image_utils import IMAGE_FORMATS, load_image, save_image


TOOL_META = {
    "slug": "image-cropper",
    "name": "图片裁剪",
    "category": "image",
    "input_mode": "file",
    "result_type": "file",
}


def run(
    input_path: str,
    output_dir: str,
    filename: str = "",
    mode: str = "center_square",
    x: int = 0,
    y: int = 0,
    width: int = 0,
    height: int = 0,
    **_: dict,
) -> str:
    image = load_image(input_path)
    if mode == "center_square":
        edge = min(image.width, image.height)
        left = (image.width - edge) // 2
        top = (image.height - edge) // 2
        box = (left, top, left + edge, top + edge)
    elif mode == "manual":
        width = int(width)
        height = int(height)
        if width <= 0 or height <= 0:
            raise AppException(message="裁剪宽高必须大于 0", code=4001, status_code=400)
        left = max(0, int(x))
        top = max(0, int(y))
        right = min(image.width, left + width)
        bottom = min(image.height, top + height)
        if right <= left or bottom <= top:
            raise AppException(message="裁剪区域无效", code=4001, status_code=400)
        box = (left, top, right, bottom)
    else:
        raise AppException(message="不支持的裁剪方式", code=4001, status_code=400)

    cropped = image.crop(box)
    suffix = Path(filename or input_path).suffix.lower().lstrip(".") or "png"
    target_format = IMAGE_FORMATS.get(suffix, "PNG")
    target_path = Path(output_dir) / f"cropped.{suffix}"
    return save_image(cropped, target_path, target_format)
