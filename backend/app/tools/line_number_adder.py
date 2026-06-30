"""文件说明：实现「文本添加序号」工具的后端逻辑。"""

from app.core.exceptions import AppException


TOOL_META = {
    "slug": "line-number-adder",
    "name": "文本添加序号",
    "category": "text",
    "input_mode": "text",
    "result_type": "text",
}


def _format_prefix(number: int, style: str) -> str:
    if style == "dot":
        return f"{number}."
    if style == "right_paren":
        return f"{number})"
    if style == "wrap_paren":
        return f"({number})"
    raise AppException(message="序号格式不支持", code=4001, status_code=400)


def run(text: str, start_number: int = 1, style: str = "dot", keep_empty: bool = False, **_: dict) -> str:
    if start_number < 0:
        raise AppException(message="起始序号不能小于 0", code=4001, status_code=400)

    current = start_number
    results: list[str] = []
    for line in text.splitlines():
        if not line.strip() and not keep_empty:
            results.append("")
            continue
        prefix = _format_prefix(current, style)
        current += 1
        content = line if line else ""
        results.append(f"{prefix} {content}".rstrip())
    return "\n".join(results)
