"""文件说明：实现「PDF 转 HTML」工具的后端逻辑。"""

from pathlib import Path

from app.utils.document_utils import build_html_from_sections, extract_pdf_sections


TOOL_META = {
    "slug": "pdf-to-html",
    "name": "PDF 转 HTML",
    "category": "text",
    "input_mode": "file",
    "result_type": "file",
}


def run(input_path: str, output_dir: str, title: str = "", **_: dict) -> str:
    sections = extract_pdf_sections(input_path)
    html_title = title.strip() or "PDF 转 HTML"
    return build_html_from_sections(sections, Path(output_dir) / "pdf-to-html.html", title=html_title)
