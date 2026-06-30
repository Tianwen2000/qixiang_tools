"""文件说明：实现「火星文转换器」工具的后端逻辑。"""

from app.core.exceptions import AppException


TOOL_META = {
    "slug": "mars-text-converter",
    "name": "火星文转换器",
    "category": "text",
    "input_mode": "text",
    "result_type": "text",
}


ENCODE_MAP = {
    "你": "伱",
    "我": "莪",
    "他": "怹",
    "们": "們",
    "是": "媞",
    "的": "の",
    "了": "叻",
    "不": "吥",
    "很": "狠",
    "还": "還",
    "说": "説",
    "这": "這",
    "么": "庅",
    "吗": "嗎",
    "爱": "噯",
    "个": "個",
    "宝": "寳",
    "再": "洅",
    "见": "笕",
    "啊": "錒",
    "哦": "噢",
}
DECODE_MAP = {value: key for key, value in ENCODE_MAP.items()}


def _to_fullwidth(char: str) -> str:
    if char == " ":
        return "　"
    code = ord(char)
    if 33 <= code <= 126:
        return chr(code + 65248)
    return char


def _to_halfwidth(char: str) -> str:
    if char == "　":
        return " "
    code = ord(char)
    if 65281 <= code <= 65374:
        return chr(code - 65248)
    return char


def _encode(text: str) -> str:
    result: list[str] = []
    for char in text:
        if char in ENCODE_MAP:
            result.append(ENCODE_MAP[char])
        elif char.isascii() and not char.isspace():
            result.append(_to_fullwidth(char))
        else:
            result.append(char)
    return "".join(result)


def _decode(text: str) -> str:
    result: list[str] = []
    for char in text:
        if char in DECODE_MAP:
            result.append(DECODE_MAP[char])
        else:
            result.append(_to_halfwidth(char))
    return "".join(result)


def run(text: str, action: str = "encode", **_: dict) -> str:
    if action == "encode":
        return _encode(text)
    if action == "decode":
        return _decode(text)
    raise AppException(message="操作方式必须是 encode 或 decode", code=4001, status_code=400)
