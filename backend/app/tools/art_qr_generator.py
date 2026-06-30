"""文件说明：实现「艺术二维码生成」工具的后端逻辑。"""

from pathlib import Path

import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.colormasks import RadialGradiantColorMask, SolidFillColorMask, VerticalGradiantColorMask
from qrcode.image.styles.moduledrawers import CircleModuleDrawer, RoundedModuleDrawer, SquareModuleDrawer

from app.core.exceptions import AppException
from app.utils.image_utils import parse_hex_color


TOOL_META = {
    "slug": "art-qr-generator",
    "name": "艺术二维码生成",
    "category": "image",
    "input_mode": "text",
    "result_type": "file",
}


DRAWER_MAP = {
    "rounded": RoundedModuleDrawer,
    "circle": CircleModuleDrawer,
    "square": SquareModuleDrawer,
}


def run(
    text: str,
    output_dir: str,
    style: str = "rounded",
    color_mode: str = "gradient",
    fill_color: str = "#1d4ed8",
    accent_color: str = "#14b8a6",
    back_color: str = "#ffffff",
    box_size: int = 10,
    border: int = 4,
    **_: dict,
) -> str:
    if not text.strip():
        raise AppException(message="请输入二维码内容", code=4001, status_code=400)
    if style not in DRAWER_MAP:
        raise AppException(message="不支持的艺术样式", code=4001, status_code=400)

    qr = qrcode.QRCode(box_size=max(1, int(box_size)), border=max(0, int(border)))
    qr.add_data(text)
    qr.make(fit=True)

    drawer = DRAWER_MAP[style]()
    if color_mode == "gradient":
        color_mask = RadialGradiantColorMask(
            back_color=parse_hex_color(back_color),
            center_color=parse_hex_color(fill_color),
            edge_color=parse_hex_color(accent_color),
        )
    elif color_mode == "vertical":
        color_mask = VerticalGradiantColorMask(
            back_color=parse_hex_color(back_color),
            top_color=parse_hex_color(fill_color),
            bottom_color=parse_hex_color(accent_color),
        )
    else:
        color_mask = SolidFillColorMask(
            back_color=parse_hex_color(back_color),
            front_color=parse_hex_color(fill_color),
        )

    image = qr.make_image(image_factory=StyledPilImage, module_drawer=drawer, color_mask=color_mask).convert("RGBA")
    target_path = Path(output_dir) / "art-qrcode.png"
    image.save(target_path, format="PNG")
    return str(target_path)
