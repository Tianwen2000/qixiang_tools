"""文件说明：实现「英文字母大小写转换」工具的后端逻辑。"""

import re

from app.core.exceptions import AppException


TOOL_META = {
    "slug": "english-case-converter",
    "name": "英文字母大小写转换",
    "category": "text",
    "input_mode": "text",
    "result_type": "text",
}


def _sentence_case(text: str) -> str:
    lowered = text.lower()
    return re.sub(
        r"(^|[.!?。！？]\s*)([a-z])",
        lambda match: f"{match.group(1)}{match.group(2).upper()}",
        lowered,
    )


def run(text: str, action: str = "upper", **_: dict) -> str:
    if action == "upper":
        return text.upper()
    if action == "lower":
        return text.lower()
    if action == "title":
        return text.title()
    if action == "sentence":
        return _sentence_case(text)
    if action == "swap":
        return text.swapcase()
    raise AppException(message="不支持的大小写转换方式", code=4001, status_code=400)
