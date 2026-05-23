from app.utils.document_utils import build_csv_outputs, extract_spreadsheet_sheets


TOOL_META = {
    "slug": "excel-to-csv",
    "name": "Excel 转 CSV",
    "category": "text",
    "input_mode": "file",
    "result_type": "file",
}


def run(input_path: str, output_dir: str, **_: dict) -> str:
    return build_csv_outputs(extract_spreadsheet_sheets(input_path), output_dir, basename="excel-to-csv")
