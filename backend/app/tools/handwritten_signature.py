"""文件说明：实现「在线手写签名」工具的后端逻辑。"""

from pathlib import Path

from PIL import Image, ImageDraw

from app.core.exceptions import AppException
from app.utils.image_utils import load_font, parse_hex_color


TOOL_META = {
    "slug": "handwritten-signature",
    "name": "在线手写签名",
    "category": "image",
    "input_mode": "text",
    "result_type": "file",
}


def run(
    text: str,
    output_dir: str,
    color: str = "#111111",
    font_size: int = 120,
    transparent_bg: bool = True,
    **_: dict,
) -> str:
    value = text.strip()
    if not value:
        raise AppException(message="请输入签名内容", code=4001, status_code=400)

    font = load_font(max(36, int(font_size)))
    temp = Image.new("RGBA", (1600, 500), (255, 255, 255, 0))
    draw = ImageDraw.Draw(temp)
    bbox = draw.textbbox((0, 0), value, font=font)
    width = bbox[2] - bbox[0]
    height = bbox[3] - bbox[1]
    canvas_width = width + 180
    canvas_height = height + 180
    background = (255, 255, 255, 0) if transparent_bg else (255, 255, 255, 255)
    canvas = Image.new("RGBA", (canvas_width, canvas_height), background)
    draw = ImageDraw.Draw(canvas)
    ink = parse_hex_color(color)

    x = 70
    y = (canvas_height - height) // 2 - 12
    for index, char in enumerate(value):
        char_box = draw.textbbox((0, 0), char, font=font)
        char_width = char_box[2] - char_box[0]
        offset_y = (index % 3 - 1) * 6
        draw.text((x, y + offset_y), char, font=font, fill=(*ink, 255))
        x += char_width - 6

    sheared = canvas.transform(
        (canvas.width + 80, canvas.height),
        Image.AFFINE,
        (1, -0.22, 40, 0, 1, 0),
        resample=Image.BICUBIC,
    )
    rotated = sheared.rotate(-5, expand=True, resample=Image.BICUBIC)
    target_path = Path(output_dir) / "signature.png"
    rotated.save(target_path, format="PNG")
    return str(target_path)
