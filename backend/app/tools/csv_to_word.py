"""文件说明：实现「CSV 转 Word」工具的后端逻辑。"""

from pathlib import Path

from app.utils.document_utils import build_docx_from_sections, extract_csv_rows, tables_to_sections


TOOL_META = {
    "slug": "csv-to-word",
    "name": "CSV 转 Word",
    "category": "text",
    "input_mode": "file",
    "result_type": "file",
}


def run(input_path: str, output_dir: str, title: str = "", **_: dict) -> str:
    sections = tables_to_sections([("CSV 数据", extract_csv_rows(input_path))])
    doc_title = title.strip() or "CSV 转 Word"
    return build_docx_from_sections(sections, Path(output_dir) / "csv-to-word.docx", title=doc_title)
