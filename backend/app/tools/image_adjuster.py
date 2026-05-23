from pathlib import Path

from PIL import ImageEnhance, ImageOps

from app.utils.image_utils import IMAGE_FORMATS, load_image, save_image


TOOL_META = {
    "slug": "image-adjuster",
    "name": "图片调整",
    "category": "image",
    "input_mode": "file",
    "result_type": "file",
}


def run(
    input_path: str,
    output_dir: str,
    filename: str = "",
    brightness: int = 100,
    contrast: int = 100,
    sharpness: int = 100,
    saturation: int = 100,
    rotate: int = 0,
    flip: str = "none",
    **_: dict,
) -> str:
    image = load_image(input_path)
    processed = ImageEnhance.Brightness(image).enhance(max(0, int(brightness)) / 100)
    processed = ImageEnhance.Contrast(processed).enhance(max(0, int(contrast)) / 100)
    processed = ImageEnhance.Sharpness(processed).enhance(max(0, int(sharpness)) / 100)
    processed = ImageEnhance.Color(processed).enhance(max(0, int(saturation)) / 100)
    if int(rotate):
        processed = processed.rotate(-int(rotate), expand=True)
    if flip == "horizontal":
        processed = ImageOps.mirror(processed)
    elif flip == "vertical":
        processed = ImageOps.flip(processed)

    suffix = Path(filename or input_path).suffix.lower().lstrip(".") or "png"
    target_format = IMAGE_FORMATS.get(suffix, "PNG")
    target_path = Path(output_dir) / f"adjusted.{suffix}"
    return save_image(processed, target_path, target_format)
