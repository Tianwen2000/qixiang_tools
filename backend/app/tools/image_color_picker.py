"""文件说明：实现「图片取色器」工具的后端逻辑。"""

from app.core.exceptions import AppException
from app.utils.image_utils import load_image


TOOL_META = {
    "slug": "image-color-picker",
    "name": "图片取色器",
    "category": "image",
    "input_mode": "file",
    "result_type": "text",
}


def run(input_path: str, x: int = -1, y: int = -1, **_: dict) -> str:
    image = load_image(input_path).convert("RGBA")
    px = image.width // 2 if int(x) < 0 else int(x)
    py = image.height // 2 if int(y) < 0 else int(y)
    if not (0 <= px < image.width and 0 <= py < image.height):
        raise AppException(message="取色坐标超出图片范围", code=4001, status_code=400)
    color = image.getpixel((px, py))
    return "\n".join(
        [
            f"坐标：({px}, {py})",
            f"HEX：#{color[0]:02X}{color[1]:02X}{color[2]:02X}",
            f"RGBA：{color}",
        ]
    )
