"""文件说明：实现「Punycode 编码/解码」工具的后端逻辑。"""

from app.core.exceptions import AppException


TOOL_META = {
    "slug": "punycode-codec",
    "name": "Punycode 编码/解码",
    "category": "encode",
    "input_mode": "text",
    "result_type": "text",
}


def run(text: str, action: str = "encode", **_: dict) -> str:
    if action == "encode":
        try:
            return text.encode("punycode").decode("ascii")
        except Exception as exc:
            raise AppException(message="Punycode 编码失败", code=4001, status_code=400) from exc

    if action == "decode":
        try:
            return text.encode("ascii").decode("punycode")
        except Exception as exc:
            raise AppException(message="Punycode 文本无效", code=4001, status_code=400) from exc

    raise AppException(message="操作方式无效", code=4001, status_code=400)
