"""文件说明：实现「Word 转 EPUB」工具的后端逻辑。"""

from pathlib import Path

from app.utils.document_utils import build_epub_from_sections, extract_docx_sections


TOOL_META = {
    "slug": "word-to-epub",
    "name": "Word 转 EPUB",
    "category": "text",
    "input_mode": "file",
    "result_type": "file",
}


def run(input_path: str, output_dir: str, title: str = "", **_: dict) -> str:
    sections = extract_docx_sections(input_path)
    epub_title = title.strip() or "Word 转 EPUB"
    return build_epub_from_sections(sections, Path(output_dir) / "word-to-epub.epub", title=epub_title)
