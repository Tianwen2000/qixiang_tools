"""文件说明：实现「文字竖排工具」工具的后端逻辑。"""

from app.core.exceptions import AppException


TOOL_META = {
    "slug": "vertical-text-tool",
    "name": "文字竖排工具",
    "category": "text",
    "input_mode": "text",
    "result_type": "text",
}


def run(text: str, blank_line_between_paragraphs: bool = True, **_: dict) -> str:
    if not text.strip():
        raise AppException(message="请输入要竖排的内容", code=4001, status_code=400)

    blocks: list[str] = []
    lines = text.splitlines()
    for index, raw_line in enumerate(lines):
        if raw_line:
            converted = "\n".join("　" if char == " " else char for char in raw_line)
            blocks.append(converted)
        if blank_line_between_paragraphs and index < len(lines) - 1:
            blocks.append("")
    return "\n".join(blocks)
