"""文件说明：实现「文本规则生成器」工具的后端逻辑。"""

import re

from app.core.exceptions import AppException
from app.utils.text_utils import split_non_empty_lines, unique_preserve_order


TOOL_META = {
    "slug": "text-rule-generator",
    "name": "文本规则生成器",
    "category": "text",
    "input_mode": "text",
    "result_type": "text",
}


def run(text: str, mode: str = "exact_line", ignore_case: bool = False, **_: dict) -> str:
    items = unique_preserve_order(split_non_empty_lines(text))
    if not items:
        raise AppException(message="请至少输入一条文本规则", code=4001, status_code=400)

    body = "|".join(re.escape(item) for item in items)
    if mode == "exact_line":
        pattern = f"^(?:{body})$"
    elif mode == "contains":
        pattern = f"(?:{body})"
    elif mode == "starts_with":
        pattern = f"^(?:{body})"
    elif mode == "ends_with":
        pattern = f"(?:{body})$"
    else:
        raise AppException(message="规则模式不支持", code=4001, status_code=400)

    return f"(?i){pattern}" if ignore_case else pattern
