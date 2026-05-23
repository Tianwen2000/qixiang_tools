from app.core.exceptions import AppException


TOOL_META = {
    "slug": "copybook-generator",
    "name": "描字帖",
    "category": "text",
    "input_mode": "text",
    "result_type": "text",
}


def run(text: str, repeat_count: int = 6, **_: dict) -> str:
    if not text.strip():
        raise AppException(message="请输入要生成描字帖的文字", code=4001, status_code=400)
    if repeat_count not in {3, 5, 6, 8, 10}:
        raise AppException(message="重复次数只能是 3、5、6、8 或 10", code=4001, status_code=400)

    lines: list[str] = []
    for raw_line in text.splitlines():
        characters = [char for char in raw_line if not char.isspace()]
        if not characters:
            lines.append("")
            continue
        for char in characters:
            lines.append("　".join([char] * repeat_count))
        lines.append("")

    while lines and lines[-1] == "":
        lines.pop()
    return "\n".join(lines)
