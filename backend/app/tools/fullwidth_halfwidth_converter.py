"""文件说明：实现「全角半角转换」工具的后端逻辑。"""

from app.core.exceptions import AppException


TOOL_META = {
    "slug": "fullwidth-halfwidth-converter",
    "name": "全角半角转换",
    "category": "text",
    "input_mode": "text",
    "result_type": "text",
}


def _to_fullwidth(text: str) -> str:
    result: list[str] = []
    for char in text:
        if char == " ":
            result.append("　")
            continue
        code = ord(char)
        if 33 <= code <= 126:
            result.append(chr(code + 65248))
        else:
            result.append(char)
    return "".join(result)


def _to_halfwidth(text: str) -> str:
    result: list[str] = []
    for char in text:
        if char == "　":
            result.append(" ")
            continue
        code = ord(char)
        if 65281 <= code <= 65374:
            result.append(chr(code - 65248))
        else:
            result.append(char)
    return "".join(result)


def run(text: str, action: str = "to_halfwidth", **_: dict) -> str:
    if action == "to_halfwidth":
        return _to_halfwidth(text)
    if action == "to_fullwidth":
        return _to_fullwidth(text)
    raise AppException(message="操作方式必须是 to_halfwidth 或 to_fullwidth", code=4001, status_code=400)
