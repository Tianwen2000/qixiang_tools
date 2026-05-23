from pathlib import Path

from app.utils.document_utils import build_docx_from_sections, extract_epub_sections


TOOL_META = {
    "slug": "epub-to-word",
    "name": "EPUB 转 Word",
    "category": "text",
    "input_mode": "file",
    "result_type": "file",
}


def run(input_path: str, output_dir: str, title: str = "", **_: dict) -> str:
    epub_title, sections = extract_epub_sections(input_path)
    doc_title = title.strip() or epub_title or "EPUB 转 Word"
    return build_docx_from_sections(sections, Path(output_dir) / "epub-to-word.docx", title=doc_title)
