"""文件说明：实现「TXT 转 HTML」工具的后端逻辑。"""

from pathlib import Path

from app.utils.document_utils import build_html_from_sections, read_plain_text


TOOL_META = {
    "slug": "txt-to-html",
    "name": "TXT 转 HTML",
    "category": "text",
    "input_mode": "file",
    "result_type": "file",
}


def run(input_path: str, output_dir: str, title: str = "", **_: dict) -> str:
    text = read_plain_text(input_path)
    html_title = title.strip() or "TXT 转 HTML"
    return build_html_from_sections([text], Path(output_dir) / "txt-to-html.html", title=html_title)
