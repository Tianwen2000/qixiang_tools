from pathlib import Path

from app.utils.document_utils import build_excel_from_rows, extract_csv_rows


TOOL_META = {
    "slug": "csv-to-excel",
    "name": "CSV 转 Excel",
    "category": "text",
    "input_mode": "file",
    "result_type": "file",
}


def run(input_path: str, output_dir: str, sheet_name: str = "", **_: dict) -> str:
    rows = extract_csv_rows(input_path)
    return build_excel_from_rows(rows, Path(output_dir) / "csv-to-excel.xlsx", sheet_name=sheet_name or "Sheet1")
