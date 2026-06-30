"""文件说明：实现「汉字转拼音」工具的后端逻辑。"""

from functools import lru_cache

from pypinyin import Style, lazy_pinyin

from app.core.exceptions import AppException


TOOL_META = {
    "slug": "pinyin-converter",
    "name": "汉字转拼音",
    "category": "text",
    "input_mode": "text",
    "result_type": "text",
}


STYLE_MAP = {
    "normal": Style.NORMAL,
    "tone": Style.TONE3,
    "first_letter": Style.FIRST_LETTER,
}

SEPARATOR_MAP = {
    "space": " ",
    "empty": "",
    "newline": "\n",
}


@lru_cache
def _supported_styles() -> set[str]:
    return set(STYLE_MAP)


def run(text: str, style: str = "normal", separator: str = "space", **_: dict) -> str:
    if style not in _supported_styles():
        raise AppException(message="不支持的拼音格式", code=4001, status_code=400)
    if separator not in SEPARATOR_MAP:
        raise AppException(message="不支持的分隔方式", code=4001, status_code=400)

    parts = lazy_pinyin(text, style=STYLE_MAP[style], errors=lambda value: list(value))
    return SEPARATOR_MAP[separator].join(part for part in parts if part != "")
