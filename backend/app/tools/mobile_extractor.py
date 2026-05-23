import re

from app.utils.text_utils import unique_preserve_order


TOOL_META = {
    "slug": "mobile-extractor",
    "name": "文本提取手机号码",
    "category": "text",
    "input_mode": "text",
    "result_type": "text",
}


MOBILE_PATTERN = re.compile(r"(?<!\d)(?:\+?86[-\s]?)?(1[3-9]\d)[-\s]?(\d{4})[-\s]?(\d{4})(?!\d)")


def run(text: str, unique: bool = True, **_: dict) -> str:
    matches = ["".join(match) for match in MOBILE_PATTERN.findall(text)]
    results = unique_preserve_order(matches) if unique else matches
    return "\n".join(results)
