"""文件说明：实现「文本反转」工具的后端逻辑。"""

from app.core.exceptions import AppException


TOOL_META = {
    "slug": "text-reverser",
    "name": "文本反转",
    "category": "text",
    "input_mode": "text",
    "result_type": "text",
}


def run(text: str, mode: str = "chars", **_: dict) -> str:
    if mode == "chars":
        return text[::-1]
    if mode == "lines":
        return "\n".join(reversed(text.splitlines()))
    if mode == "chars_per_line":
        return "\n".join(line[::-1] for line in text.splitlines())
    raise AppException(message="不支持的反转方式", code=4001, status_code=400)
