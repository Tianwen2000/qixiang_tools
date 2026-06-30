"""文件说明：实现「EPUB 转 PDF」工具的后端逻辑。"""

from pathlib import Path

from app.utils.document_utils import extract_epub_sections, write_text_pdf


TOOL_META = {
    "slug": "epub-to-pdf",
    "name": "EPUB 转 PDF",
    "category": "text",
    "input_mode": "file",
    "result_type": "file",
}


def run(input_path: str, output_dir: str, title: str = "", **_: dict) -> str:
    epub_title, sections = extract_epub_sections(input_path)
    pdf_title = title.strip() or epub_title or "EPUB 转 PDF"
    return write_text_pdf(sections, Path(output_dir) / "epub-to-pdf.pdf", title=pdf_title)
