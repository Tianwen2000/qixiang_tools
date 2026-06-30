"""文件说明：实现「国旗头像生成器」工具的后端逻辑。"""

from pathlib import Path

from PIL import Image, ImageDraw

from app.core.exceptions import AppException
from app.utils.image_utils import load_image, save_image


TOOL_META = {
    "slug": "flag-avatar-generator",
    "name": "国旗头像生成器",
    "category": "image",
    "input_mode": "file",
    "result_type": "file",
}


def _draw_flag(canvas: Image.Image, flag_code: str) -> Image.Image:
    draw = ImageDraw.Draw(canvas)
    w, h = canvas.size
    if flag_code == "cn":
        draw.rectangle((0, 0, w, h), fill=(222, 38, 38, 255))
        draw.ellipse((w * 0.14, h * 0.16, w * 0.26, h * 0.28), fill=(255, 215, 0, 255))
    elif flag_code == "jp":
        draw.rectangle((0, 0, w, h), fill=(255, 255, 255, 255))
        draw.ellipse((w * 0.3, h * 0.3, w * 0.7, h * 0.7), fill=(220, 38, 38, 255))
    elif flag_code == "fr":
        draw.rectangle((0, 0, w / 3, h), fill=(37, 99, 235, 255))
        draw.rectangle((w / 3, 0, 2 * w / 3, h), fill=(255, 255, 255, 255))
        draw.rectangle((2 * w / 3, 0, w, h), fill=(220, 38, 38, 255))
    elif flag_code == "de":
        draw.rectangle((0, 0, w, h / 3), fill=(0, 0, 0, 255))
        draw.rectangle((0, h / 3, w, 2 * h / 3), fill=(220, 38, 38, 255))
        draw.rectangle((0, 2 * h / 3, w, h), fill=(255, 215, 0, 255))
    elif flag_code == "us":
        stripe = h / 13
        for index in range(13):
            fill = (220, 38, 38, 255) if index % 2 == 0 else (255, 255, 255, 255)
            draw.rectangle((0, index * stripe, w, (index + 1) * stripe), fill=fill)
        draw.rectangle((0, 0, w * 0.45, stripe * 7), fill=(30, 64, 175, 255))
    else:
        raise AppException(message="不支持的国旗样式", code=4001, status_code=400)
    return canvas


def run(input_path: str, output_dir: str, flag_code: str = "cn", opacity: int = 45, **_: dict) -> str:
    avatar = load_image(input_path).convert("RGBA")
    edge = min(avatar.width, avatar.height)
    left = (avatar.width - edge) // 2
    top = (avatar.height - edge) // 2
    avatar = avatar.crop((left, top, left + edge, top + edge)).resize((640, 640))

    mask = Image.new("L", avatar.size, 0)
    ImageDraw.Draw(mask).ellipse((0, 0, avatar.width, avatar.height), fill=255)
    result = Image.new("RGBA", avatar.size, (255, 255, 255, 0))
    result.paste(avatar, (0, 0), mask)

    flag = _draw_flag(Image.new("RGBA", avatar.size, (255, 255, 255, 0)), flag_code)
    alpha = max(0, min(int(opacity), 100)) * 255 // 100
    flag.putalpha(alpha)
    result = Image.alpha_composite(result, flag)

    border = ImageDraw.Draw(result)
    border.ellipse((8, 8, result.width - 8, result.height - 8), outline=(255, 255, 255, 220), width=18)
    target_path = Path(output_dir) / "flag-avatar.png"
    return save_image(result, target_path, "PNG")
