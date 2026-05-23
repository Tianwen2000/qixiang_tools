import codecs

from app.core.exceptions import AppException


TOOL_META = {
    "slug": "unicode-chinese-converter",
    "name": "Unicode 中文互转",
    "category": "encode",
    "input_mode": "text",
    "result_type": "text",
}


def run(text: str, action: str = "to_unicode", **_: dict) -> str:
    if action == "to_unicode":
        return text.encode("unicode_escape").decode("ascii")

    if action == "to_text":
        try:
            return codecs.decode(text, "unicode_escape")
        except Exception as exc:
            raise AppException(message="Unicode 转义文本无效", code=4001, status_code=400) from exc

    raise AppException(message="操作方式无效", code=4001, status_code=400)
