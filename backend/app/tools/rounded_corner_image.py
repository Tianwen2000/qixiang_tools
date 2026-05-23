from pathlib import Path

from PIL import Image, ImageDraw

from app.utils.image_utils import load_image, save_image


TOOL_META = {
    "slug": "rounded-corner-image",
    "name": "生成圆角图片",
    "category": "image",
    "input_mode": "file",
    "result_type": "file",
}


def run(input_path: str, output_dir: str, radius: int = 32, **_: dict) -> str:
    image = load_image(input_path).convert("RGBA")
    mask = Image.new("L", image.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle((0, 0, image.width, image.height), radius=max(0, int(radius)), fill=255)
    rounded = image.copy()
    rounded.putalpha(mask)
    target_path = Path(output_dir) / "rounded.png"
    return save_image(rounded, target_path, "PNG")
