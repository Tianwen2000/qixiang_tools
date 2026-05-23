import re


TOOL_META = {
    "slug": "whitespace-cleaner",
    "name": "空白字符清理",
    "category": "text",
    "input_mode": "text",
    "result_type": "text",
}


def run(
    text: str,
    trim_each_line: bool = True,
    remove_empty_lines: bool = False,
    collapse_spaces: bool = False,
    **_: dict,
) -> str:
    lines = text.splitlines()
    cleaned_lines: list[str] = []

    for line in lines:
        current = line.strip() if trim_each_line else line
        if collapse_spaces:
            current = re.sub(r"[ \t\u3000]+", " ", current)
        if remove_empty_lines and not current.strip():
            continue
        cleaned_lines.append(current)

    return "\n".join(cleaned_lines)
