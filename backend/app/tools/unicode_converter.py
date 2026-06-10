import re

from app.core.exceptions import AppException


TOOL_META = {
    "slug": "unicode-chinese-converter",
    "name": "字符与unicode码点进制互转",
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


def _unicode_label(codepoint: int) -> str:
    return f"U+{codepoint:04X}"


def _unicode_escape_char(char: str) -> str:
    codepoint = ord(char)
    if codepoint <= 0xFFFF:
        return f"\\u{codepoint:04x}"
    value = codepoint - 0x10000
    high = 0xD800 + (value >> 10)
    low = 0xDC00 + (value & 0x3FF)
    return f"\\u{high:04x}\\u{low:04x}"


def _unicode_escape_text(text: str) -> str:
    return "".join(_unicode_escape_char(char) for char in text)


def _codepoint_text(text: str) -> str:
    return ", ".join(str(ord(char)) for char in text)


def _unicode_standard_text(text: str) -> str:
    return ", ".join(_unicode_label(ord(char)) for char in text)


def _display_char(char: str) -> str:
    display_map = {
        "\n": "\\n",
        "\r": "\\r",
        "\t": "\\t",
        " ": "空格",
    }
    return display_map.get(char, char)


def _format_detail_table(input_text: str) -> str:
    rows = ["输入字符进制详情表", "字符\t二进制\t八进制\t十进制\t十六进制\tUnicode"]
    for char in input_text:
        codepoint = ord(char)
        rows.append(
            "\t".join(
                [
                    _display_char(char),
                    format(codepoint, "b"),
                    format(codepoint, "o"),
                    str(codepoint),
                    format(codepoint, "X"),
                    _unicode_label(codepoint),
                ],
            ),
        )
    if len(rows) == 2:
        rows.append("（空字符串）\t\t\t\t\t")
    return "\n".join(rows)


def _format_result(label: str, value: str, input_text: str, include_detail_table: bool) -> str:
    sections = [f"{label}：{value}"]
    if include_detail_table:
        sections.extend(["", _format_detail_table(input_text)])
    return "\n".join(sections)


def _unicode_to_text(text: str) -> str:
    if CODEPOINT_LIST_PATTERN.fullmatch(text):
        return _codepoint_list_to_text(text)

    decoded = UNICODE_ESCAPE_PATTERN.sub(
        lambda match: _codepoint_to_char(next(group for group in match.groups() if group)),
        text,
    )
    try:
        return decoded.encode("utf-16", "surrogatepass").decode("utf-16")
    except UnicodeDecodeError as exc:
        raise AppException(message="Unicode 代理对文本无效", code=4001, status_code=400) from exc


def run(text: str, action: str = "to_text", include_detail_table: bool = False, **_: dict) -> str:
    if action == "to_text":
        return _format_result("字符结果", _unicode_to_text(text), text, include_detail_table)

    if action in {"to_codepoints", "to_unicode"}:
        return _format_result("Unicode 码点", _codepoint_text(text), text, include_detail_table)

    if action == "to_escape":
        return _format_result("Unicode 转义", _unicode_escape_text(text), text, include_detail_table)

    if action == "to_standard":
        return _format_result("Unicode 标准写法", _unicode_standard_text(text), text, include_detail_table)

    raise AppException(message="操作方式无效", code=4001, status_code=400)
