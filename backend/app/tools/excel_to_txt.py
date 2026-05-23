from pathlib import Path

from app.utils.document_utils import extract_spreadsheet_sheets, tables_to_sections, write_plain_text


TOOL_META = {
    "slug": "excel-to-txt",
    "name": "Excel 转 TXT",
    "category": "text",
    "input_mode": "file",
    "result_type": "file",
}


def run(input_path: str, output_dir: str, **_: dict) -> str:
    sections = tables_to_sections(extract_spreadsheet_sheets(input_path))
    return write_plain_text("\n\n".join(sections), Path(output_dir) / "excel-to-txt.txt")
