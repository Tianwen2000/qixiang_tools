from pathlib import Path

from app.utils.document_utils import build_epub_from_sections, extract_csv_rows, tables_to_sections


TOOL_META = {
    "slug": "csv-to-epub",
    "name": "CSV 转 EPUB",
    "category": "text",
    "input_mode": "file",
    "result_type": "file",
}


def run(input_path: str, output_dir: str, title: str = "", **_: dict) -> str:
    sections = tables_to_sections([("CSV 数据", extract_csv_rows(input_path))])
    epub_title = title.strip() or "CSV 转 EPUB"
    return build_epub_from_sections(sections, Path(output_dir) / "csv-to-epub.epub", title=epub_title)
