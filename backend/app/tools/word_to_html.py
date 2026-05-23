from pathlib import Path

from app.utils.document_utils import build_html_from_sections, extract_docx_sections


TOOL_META = {
    "slug": "word-to-html",
    "name": "Word 转 HTML",
    "category": "text",
    "input_mode": "file",
    "result_type": "file",
}


def run(input_path: str, output_dir: str, title: str = "", **_: dict) -> str:
    sections = extract_docx_sections(input_path)
    html_title = title.strip() or "Word 转 HTML"
    return build_html_from_sections(sections, Path(output_dir) / "word-to-html.html", title=html_title)
