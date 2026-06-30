"""文件说明：实现「二维码生成」工具的后端逻辑。"""

from pathlib import Path

import qrcode

from app.core.exceptions import AppException


TOOL_META = {
    "slug": "qr-code-generator",
    "name": "二维码生成",
    "category": "image",
    "input_mode": "text",
    "result_type": "file",
}


def run(
    text: str,
    output_dir: str,
    box_size: int = 10,
    border: int = 4,
    fill_color: str = "#000000",
    back_color: str = "#ffffff",
    **_: dict,
) -> str:
    if not text.strip():
        raise AppException(message="请输入二维码内容", code=4001, status_code=400)
    qr = qrcode.QRCode(box_size=max(1, int(box_size)), border=max(0, int(border)))
    qr.add_data(text)
    qr.make(fit=True)
    image = qr.make_image(fill_color=fill_color, back_color=back_color).convert("RGB")
    target_path = Path(output_dir) / "qrcode.png"
    image.save(target_path, format="PNG")
    return str(target_path)
