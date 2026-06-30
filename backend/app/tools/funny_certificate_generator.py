"""文件说明：实现「搞笑奖状批量生成器」工具的后端逻辑。"""

from pathlib import Path

from PIL import Image, ImageDraw

from app.core.exceptions import AppException
from app.utils.image_utils import load_font, zip_output_files


TOOL_META = {
    "slug": "funny-certificate-generator",
    "name": "搞笑奖状批量生成器",
    "category": "image",
    "input_mode": "text",
    "result_type": "file",
}


def _draw_certificate(name: str, title: str, reason: str, signer: str, target_path: Path) -> None:
    width, height = 1600, 1100
    canvas = Image.new("RGB", (width, height), (255, 251, 235))
    draw = ImageDraw.Draw(canvas)
    outer = (186, 142, 72)
    inner = (224, 180, 92)
    draw.rounded_rectangle((40, 40, width - 40, height - 40), radius=32, outline=outer, width=8)
    draw.rounded_rectangle((82, 82, width - 82, height - 82), radius=24, outline=inner, width=3)

    title_font = load_font(118)
    name_font = load_font(92)
    body_font = load_font(48)
    signer_font = load_font(40)

    draw.text((width / 2, 190), title, font=title_font, fill=(164, 91, 32), anchor="mm")
    draw.text((width / 2, 360), "特此颁发给", font=body_font, fill=(96, 68, 32), anchor="mm")
    draw.text((width / 2, 500), name, font=name_font, fill=(210, 38, 38), anchor="mm")
    draw.text((width / 2, 650), reason, font=body_font, fill=(96, 68, 32), anchor="mm")
    draw.text((width / 2, 760), "望继续保持，笑傲江湖。", font=body_font, fill=(96, 68, 32), anchor="mm")
    draw.text((width - 220, height - 180), signer, font=signer_font, fill=(96, 68, 32), anchor="mm")
    draw.text((width - 220, height - 120), "琦湘工具集合", font=signer_font, fill=(96, 68, 32), anchor="mm")

    for pos in ((180, 160), (width - 180, 160), (180, height - 180), (width - 180, height - 180)):
        draw.text(pos, "★", font=load_font(52), fill=(234, 179, 8), anchor="mm")

    canvas.save(target_path, format="PNG")


def run(
    text: str,
    output_dir: str,
    title: str = "沙雕奖状",
    reason: str = "因表现过于优秀，特授予“人间清醒选手”称号",
    signer: str = "摸鱼委员会",
    **_: dict,
) -> str:
    names = [line.strip() for line in text.splitlines() if line.strip()]
    if not names:
        raise AppException(message="请至少输入一个姓名", code=4001, status_code=400)

    result_dir = Path(output_dir) / "certificates"
    result_dir.mkdir(parents=True, exist_ok=True)
    for index, name in enumerate(names, start=1):
        _draw_certificate(name, title.strip() or "沙雕奖状", reason.strip(), signer.strip(), result_dir / f"certificate-{index}-{name}.png")
    return zip_output_files(result_dir, Path(output_dir) / "funny-certificates.zip")
