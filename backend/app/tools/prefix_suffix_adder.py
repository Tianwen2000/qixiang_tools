"""文件说明：实现「文本加前后缀」工具的后端逻辑。"""

TOOL_META = {
    "slug": "prefix-suffix-adder",
    "name": "文本加前后缀",
    "category": "text",
    "input_mode": "text",
    "result_type": "text",
}


def run(text: str, prefix: str = "", suffix: str = "", skip_empty: bool = True, **_: dict) -> str:
    result: list[str] = []
    for line in text.splitlines():
        if skip_empty and not line.strip():
            result.append(line)
            continue
        result.append(f"{prefix}{line}{suffix}")
    return "\n".join(result)
