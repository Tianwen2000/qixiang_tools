from pathlib import Path

from app.utils.document_utils import build_html_from_tables, extract_spreadsheet_sheets


TOOL_META = {
    "slug": "excel-to-html",
    "name": "Excel 转 HTML",
    "category": "text",
    "input_mode": "file",
    "result_type": "file",
}


def run(input_path: str, output_dir: str, title: str = "", **_: dict) -> str:
    tables = extract_spreadsheet_sheets(input_path)
    return build_html_from_tables(tables, Path(output_dir) / "excel-to-html.html", title=title.strip() or "Excel 转 HTML")
