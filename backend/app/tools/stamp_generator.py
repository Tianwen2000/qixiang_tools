"""文件说明：实现「印章生成器」工具的后端逻辑。"""

import math
from pathlib import Path

from PIL import Image, ImageDraw

from app.core.exceptions import AppException
from app.utils.image_utils import load_font, parse_hex_color


TOOL_META = {
    "slug": "stamp-generator",
    "name": "印章生成器",
    "category": "image",
    "input_mode": "text",
    "result_type": "file",
}


def _draw_arc_text(canvas: Image.Image, text: str, radius: int, color: tuple[int, int, int]) -> None:
    if not text:
        return
    center_x, center_y = canvas.width // 2, canvas.height // 2
    char_font = load_font(42 if len(text) <= 10 else 34)
    start_angle = 200
    end_angle = -20
    step = (start_angle - end_angle) / max(len(text) - 1, 1)
    for index, char in enumerate(text):
        angle = start_angle - step * index
        radians = math.radians(angle)
        x = center_x + radius * math.cos(radians)
        y = center_y - radius * math.sin(radians)
        char_image = Image.new("RGBA", (80, 80), (255, 255, 255, 0))
        drawer = ImageDraw.Draw(char_image)
        box = drawer.textbbox((0, 0), char, font=char_font)
        drawer.text(((80 - (box[2] - box[0])) / 2, (80 - (box[3] - box[1])) / 2), char, font=char_font, fill=color)
        rotated = char_image.rotate(angle - 90, resample=Image.BICUBIC, expand=True)
        canvas.alpha_composite(rotated, (int(x - rotated.width / 2), int(y - rotated.height / 2)))


def run(
    text: str,
    output_dir: str,
    center_text: str = "专用章",
    subtitle: str = "",
    color: str = "#d40000",
    **_: dict,
) -> str:
    main_text = text.strip()
    if not main_text:
        raise AppException(message="请输入印章主文字", code=4001, status_code=400)

    seal_color = parse_hex_color(color)
    canvas = Image.new("RGBA", (640, 640), (255, 255, 255, 0))
    draw = ImageDraw.Draw(canvas)
    draw.ellipse((40, 40, 600, 600), outline=seal_color, width=14)
    draw.ellipse((78, 78, 562, 562), outline=seal_color, width=4)
    _draw_arc_text(canvas, main_text, 220, seal_color)

    star_font = load_font(116)
    center_font = load_font(58)
    sub_font = load_font(32)
    draw.text((canvas.width / 2, 250), "★", font=star_font, fill=seal_color, anchor="mm")
    draw.text((canvas.width / 2, 355), center_text.strip() or "专用章", font=center_font, fill=seal_color, anchor="mm")
    if subtitle.strip():
        draw.text((canvas.width / 2, 455), subtitle.strip(), font=sub_font, fill=seal_color, anchor="mm")

    target_path = Path(output_dir) / "stamp.png"
    canvas.save(target_path, format="PNG")
    return str(target_path)
