import re

from app.utils.text_utils import unique_preserve_order


TOOL_META = {
    "slug": "link-extractor",
    "name": "文本提取链接",
    "category": "text",
    "input_mode": "text",
    "result_type": "text",
}


LINK_PATTERN = re.compile(r"(?i)\b((?:https?://|ftp://|www\.)[^\s<>'\"]+)")


def run(text: str, unique: bool = True, **_: dict) -> str:
    matches = [match.rstrip(".,;:!?)]}") for match in LINK_PATTERN.findall(text)]
    results = unique_preserve_order(matches) if unique else matches
    return "\n".join(results)
