from pathlib import Path

from app.core.exceptions import AppException
from app.utils.image_utils import IMAGE_FORMATS, load_image, save_image


TOOL_META = {
    "slug": "id-photo-cropper",
    "name": "证件照裁剪",
    "category": "image",
    "input_mode": "file",
    "result_type": "file",
}


PRESETS = {
    "one_inch": (295, 413),
    "two_inch": (413, 579),
    "small_one_inch": (260, 378),
}


def run(input_path: str, output_dir: str, filename: str = "", preset: str = "one_inch", **_: dict) -> str:
    if preset not in PRESETS:
        raise AppException(message="不支持的证件照尺寸", code=4001, status_code=400)
    target_width, target_height = PRESETS[preset]
    image = load_image(input_path)

    target_ratio = target_width / target_height
    current_ratio = image.width / image.height
    if current_ratio > target_ratio:
        crop_width = int(image.height * target_ratio)
        crop_height = image.height
        left = (image.width - crop_width) // 2
        top = 0
    else:
        crop_width = image.width
        crop_height = int(image.width / target_ratio)
        left = 0
        top = (image.height - crop_height) // 2

    cropped = image.crop((left, top, left + crop_width, top + crop_height)).resize((target_width, target_height))
    suffix = Path(filename or input_path).suffix.lower().lstrip(".") or "jpg"
    target_format = IMAGE_FORMATS.get(suffix, "JPEG")
    target_path = Path(output_dir) / f"id-photo.{suffix}"
    return save_image(cropped, target_path, target_format, quality=92)
