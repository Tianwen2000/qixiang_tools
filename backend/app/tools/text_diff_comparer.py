import difflib

from app.core.exceptions import AppException


TOOL_META = {
    "slug": "text-diff-comparer",
    "name": "文本差异对比",
    "category": "text",
    "input_mode": "text",
    "result_type": "text",
}


def run(text: str, compare_text: str = "", context_lines: int = 3, **_: dict) -> str:
    if not compare_text:
        raise AppException(message="请先输入对比文本", code=4001, status_code=400)
    if context_lines not in {1, 3, 5}:
        raise AppException(message="上下文行数只能是 1、3 或 5", code=4001, status_code=400)

    diff_lines = list(
        difflib.unified_diff(
            text.splitlines(),
            compare_text.splitlines(),
            fromfile="原文本",
            tofile="对比文本",
            n=context_lines,
            lineterm="",
        )
    )
    if not diff_lines:
        return "两段文本内容一致"
    return "\n".join(diff_lines)
