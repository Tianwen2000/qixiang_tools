"""文件说明：实现「文本提取邮箱」工具的后端逻辑。"""

import re

from app.utils.text_utils import unique_preserve_order


TOOL_META = {
    "slug": "email-extractor",
    "name": "文本提取邮箱",
    "category": "text",
    "input_mode": "text",
    "result_type": "text",
}


EMAIL_PATTERN = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")


def run(text: str, unique: bool = True, **_: dict) -> str:
    matches = EMAIL_PATTERN.findall(text)
    results = unique_preserve_order(matches) if unique else matches
    return "\n".join(results)
