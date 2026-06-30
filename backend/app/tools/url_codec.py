"""文件说明：实现「URL 编码/解码」工具的后端逻辑。"""

from urllib.parse import quote, unquote

from app.core.exceptions import AppException


TOOL_META = {
    "slug": "url-codec",
    "name": "URL 编码/解码",
    "category": "encode",
    "input_mode": "text",
    "result_type": "text",
}


def run(text: str, action: str = "encode", **_: dict) -> str:
    if action == "encode":
        return quote(text, safe="")
    if action == "decode":
        return unquote(text)
    raise AppException(message="操作方式无效", code=4001, status_code=400)
