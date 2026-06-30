"""文件说明：实现「PDF 转 EPUB」工具的后端逻辑。"""

from pathlib import Path

from app.utils.document_utils import build_epub_from_sections, extract_pdf_sections


TOOL_META = {
    "slug": "pdf-to-epub",
    "name": "PDF 转 EPUB",
    "category": "text",
    "input_mode": "file",
    "result_type": "file",
}


def run(input_path: str, output_dir: str, title: str = "", **_: dict) -> str:
    sections = extract_pdf_sections(input_path)
    book_title = title.strip() or "PDF 转 EPUB"
    return build_epub_from_sections(sections, Path(output_dir) / "pdf-to-epub.epub", title=book_title)
