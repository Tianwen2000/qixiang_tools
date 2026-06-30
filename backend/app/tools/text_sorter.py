"""文件说明：实现「字符串数组排序」工具的后端逻辑。"""

from app.core.exceptions import AppException


TOOL_META = {
    "slug": "text-sorter",
    "name": "字符串数组排序",
    "category": "text",
    "input_mode": "text",
    "result_type": "text",
}


def _to_number(value: str) -> float:
    try:
        return float(value)
    except ValueError as exc:
        raise AppException(message=f"发现非数字内容：{value}", code=4001, status_code=400) from exc


def run(text: str, order: str = "asc", mode: str = "text", unique: bool = False, **_: dict) -> str:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if unique:
        lines = list(dict.fromkeys(lines))

    reverse = order == "desc"
    if order not in {"asc", "desc"}:
        raise AppException(message="排序方式必须是 asc 或 desc", code=4001, status_code=400)

    if mode == "text":
        lines.sort(key=lambda item: item.lower(), reverse=reverse)
    elif mode == "number":
        lines.sort(key=_to_number, reverse=reverse)
    else:
        raise AppException(message="排序模式必须是 text 或 number", code=4001, status_code=400)

    return "\n".join(lines)
