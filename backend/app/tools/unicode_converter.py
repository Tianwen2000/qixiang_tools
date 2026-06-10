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
CODEPOINT_LIST_PATTERN = re.compile(r"^\s*(?:\d+|U\+[0-9a-fA-F]{1,6}|0x[0-9a-fA-F]{1,6})(?:[\s,，]+(?:\d+|U\+[0-9a-fA-F]{1,6}|0x[0-9a-fA-F]{1,6}))*\s*$")
CODEPOINT_TOKEN_PATTERN = re.compile(r"\d+|U\+[0-9a-fA-F]{1,6}|0x[0-9a-fA-F]{1,6}")


def _codepoint_to_char(value: str) -> str:
    codepoint = int(value, 16)
    try:
        return chr(codepoint)
    except ValueError as exc:
        raise AppException(message=f"Unicode 码点无效：{value}", code=4001, status_code=400) from exc


def _parse_codepoint_token(token: str) -> str:
    if token.startswith(("U+", "u+")):
        return _codepoint_to_char(token[2:])
    if token.startswith(("0x", "0X")):
        return _codepoint_to_char(token[2:])
    try:
        return chr(int(token, 10))
    except ValueError as exc:
        raise AppException(message=f"Unicode 码点无效：{token}", code=4001, status_code=400) from exc


def _codepoint_list_to_text(text: str) -> str:
    return "".join(_parse_codepoint_token(token.group(0)) for token in CODEPOINT_TOKEN_PATTERN.finditer(text))


def _format_codepoint_details(text: str) -> str:
    if not text:
        return "（空字符串）"
    return "\n".join(f"字符显示：{char}\n10进制码点：{ord(char)}" for char in text)


def _format_text_result(text: str) -> str:
    return f"字符串：{text}\n\n码点明细：\n{_format_codepoint_details(text)}"


def _unicode_to_text(text: str) -> str:
    if CODEPOINT_LIST_PATTERN.fullmatch(text):
        return _format_text_result(_codepoint_list_to_text(text))

    decoded = UNICODE_ESCAPE_PATTERN.sub(
        lambda match: _codepoint_to_char(next(group for group in match.groups() if group)),
        text,
    )
    try:
        return _format_text_result(decoded.encode("utf-16", "surrogatepass").decode("utf-16"))
    except UnicodeDecodeError as exc:
        raise AppException(message="Unicode 代理对文本无效", code=4001, status_code=400) from exc


def run(text: str, action: str = "to_text", **_: dict) -> str:
    if action == "to_unicode":
        return _format_codepoint_details(text)

    if action == "to_text":
        return _unicode_to_text(text)

    raise AppException(message="操作方式无效", code=4001, status_code=400)
