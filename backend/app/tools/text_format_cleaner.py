import re


TOOL_META = {
    "slug": "text-format-cleaner",
    "name": "文本格式清理",
    "category": "ops",
    "input_mode": "text",
    "result_type": "text",
}


ZERO_WIDTH_PATTERN = re.compile(r"[\u200b\u200c\u200d\ufeff\u2060]")
LINE_INLINE_SPACE_PATTERN = re.compile(r"[ \t\f\v\u00a0\u3000]+")


def _to_text(value: object) -> str:
    return value if isinstance(value, str) else str(value)


def _remove_zero_width(text: str) -> str:
    return ZERO_WIDTH_PATTERN.sub("", text)


def _clean_single_line(text: str) -> str:
    cleaned_text = re.sub(r"[\r\n\t\f\v]", " ", text)
    cleaned_text = re.sub(r"\s+", " ", cleaned_text)
    return cleaned_text.strip()


def _clean_keep_lines(text: str) -> str:
    cleaned_lines = []
    for line in text.splitlines():
        current = LINE_INLINE_SPACE_PATTERN.sub(" ", line).strip()
        if current:
            cleaned_lines.append(current)
    return "\n".join(cleaned_lines)


def run(text: str, mode: str = "single_line", remove_zero_width: bool = True, **_: dict) -> str:
    cleaned_text = _to_text(text)
    if remove_zero_width:
        cleaned_text = _remove_zero_width(cleaned_text)

    if mode == "keep_lines":
        return _clean_keep_lines(cleaned_text)
    return _clean_single_line(cleaned_text)
