from pathlib import Path

import barcode
from barcode.writer import ImageWriter

from app.core.exceptions import AppException


TOOL_META = {
    "slug": "barcode-generator",
    "name": "条形码生成器",
    "category": "image",
    "input_mode": "text",
    "result_type": "file",
}


def run(text: str, output_dir: str, barcode_type: str = "code128", **_: dict) -> str:
    value = text.strip()
    if not value:
        raise AppException(message="请输入条形码内容", code=4001, status_code=400)
    if barcode_type not in {"code128", "ean13"}:
        raise AppException(message="不支持的条形码类型", code=4001, status_code=400)
    if barcode_type == "ean13" and (len(value) != 12 or not value.isdigit()):
        raise AppException(message="EAN-13 需要输入 12 位数字", code=4001, status_code=400)

    barcode_class = barcode.get_barcode_class(barcode_type)
    code = barcode_class(value, writer=ImageWriter())
    base_path = Path(output_dir) / "barcode"
    saved = code.save(str(base_path))
    return str(Path(saved))
