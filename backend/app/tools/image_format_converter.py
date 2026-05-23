from pathlib import Path

from app.utils.image_utils import IMAGE_FORMATS, image_extension_from_format, load_image, save_image


TOOL_META = {
    "slug": "image-format-converter",
    "name": "图片格式转换",
    "category": "image",
    "input_mode": "file",
    "result_type": "file",
}


def run(input_path: str, output_dir: str, output_format: str = "png", **_: dict) -> str:
    image = load_image(input_path)
    suffix = image_extension_from_format(output_format)
    target_format = IMAGE_FORMATS[suffix]
    target_path = Path(output_dir) / f"converted.{suffix}"
    return save_image(image, target_path, target_format)
