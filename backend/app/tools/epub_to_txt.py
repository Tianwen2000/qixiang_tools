"""文件说明：实现「EPUB 转 TXT」工具的后端逻辑。"""

from pathlib import Path

from app.utils.document_utils import extract_epub_sections, sections_to_text, write_plain_text


TOOL_META = {
    "slug": "epub-to-txt",
    "name": "EPUB 转 TXT",
    "category": "text",
    "input_mode": "file",
    "result_type": "file",
}


def run(input_path: str, output_dir: str, **_: dict) -> str:
    _, sections = extract_epub_sections(input_path)
    return write_plain_text(sections_to_text(sections), Path(output_dir) / "epub-to-txt.txt")
