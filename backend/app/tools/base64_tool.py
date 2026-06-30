"""文件说明：实现「Base64 编码/解码」工具的后端逻辑。"""

import base64

from app.core.exceptions import AppException


TOOL_META = {
    "slug": "base64-codec",
    "name": "Base64 编码/解码",
    "category": "encode",
    "input_mode": "text",
    "result_type": "text",
}


def run(text: str, action: str = "encode", **_: dict) -> str:
    if action == "encode":
        return base64.b64encode(text.encode("utf-8")).decode("utf-8")

    if action == "decode":
        try:
            return base64.b64decode(text.encode("utf-8")).decode("utf-8")
        except Exception as exc:
            raise AppException(message="Base64 文本无效", code=4001, status_code=400) from exc

    raise AppException(message="操作方式无效", code=4001, status_code=400)
