"""文件说明：实现「驼峰下划线互转」工具的后端逻辑。"""

import re

from app.core.exceptions import AppException


TOOL_META = {
    "slug": "camel-snake-converter",
    "name": "驼峰下划线互转",
    "category": "text",
    "input_mode": "text",
    "result_type": "text",
}


def _camel_to_snake(value: str) -> str:
    normalized = value.replace("-", "_")
    first = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", normalized)
    second = re.sub("([a-z0-9])([A-Z])", r"\1_\2", first)
    return second.lower()


def _snake_to_camel(value: str, upper_first: bool) -> str:
    parts = [item for item in re.split(r"[_\-\s]+", value.strip()) if item]
    if not parts:
        return ""
    head = parts[0].capitalize() if upper_first else parts[0].lower()
    tail = "".join(item.capitalize() for item in parts[1:])
    return f"{head}{tail}"


def run(text: str, action: str = "camel_to_snake", **_: dict) -> str:
    value = text.strip()
    if not value:
        raise AppException(message="请输入要转换的文本", code=4001, status_code=400)

    if action == "camel_to_snake":
        return _camel_to_snake(value)
    if action == "snake_to_camel":
        return _snake_to_camel(value, upper_first=False)
    if action == "snake_to_pascal":
        return _snake_to_camel(value, upper_first=True)
    raise AppException(message="不支持的转换方式", code=4001, status_code=400)
