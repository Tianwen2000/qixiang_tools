import re

from app.core.exceptions import AppException


TOOL_META = {
    "slug": "unicode-chinese-converter",
    "name": "Unicode 转字符串",
    "category": "encode",
    "input_mode": "text",
    "result_type": "text",
}

UNICODE_ESCAPE_PATTERN = re.compile(r"\\u\{([0-9a-fA-F]{1,6})\}|\\U([0-9a-fA-F]{8})|\\u([0-9a-fA-F]{4})")


def _codepoint_to_char(value: str) -> str:
    codepoint = int(value, 16)
    try:
        return chr(codepoint)
    except ValueError as exc:
        raise AppException(message=f"Unicode 码点无效：{value}", code=4001, status_code=400) from exc


def _unicode_to_text(text: str) -> str:
    decoded = UNICODE_ESCAPE_PATTERN.sub(
        lambda match: _codepoint_to_char(next(group for group in match.groups() if group)),
        text,
    )
    try:
        return decoded.encode("utf-16", "surrogatepass").decode("utf-16")
    except UnicodeDecodeError as exc:
        raise AppException(message="Unicode 代理对文本无效", code=4001, status_code=400) from exc


def run(text: str, action: str = "to_text", **_: dict) -> str:
    if action == "to_unicode":
        return text.encode("unicode_escape").decode("ascii")

    if action == "to_text":
        return _unicode_to_text(text)

    raise AppException(message="操作方式无效", code=4001, status_code=400)
