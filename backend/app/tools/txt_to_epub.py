from pathlib import Path

from app.utils.document_utils import build_epub_from_sections, read_plain_text


TOOL_META = {
    "slug": "txt-to-epub",
    "name": "TXT 转 EPUB",
    "category": "text",
    "input_mode": "file",
    "result_type": "file",
}


def run(input_path: str, output_dir: str, title: str = "", **_: dict) -> str:
    text = read_plain_text(input_path)
    epub_title = title.strip() or "TXT 转 EPUB"
    return build_epub_from_sections([text], Path(output_dir) / "txt-to-epub.epub", title=epub_title)
