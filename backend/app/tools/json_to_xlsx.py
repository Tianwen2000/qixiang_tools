import json
from pathlib import Path

from openpyxl import Workbook

from app.core.exceptions import AppException


TOOL_META = {
    "slug": "json-to-xlsx",
    "name": "JSON 转 XLSX",
    "category": "dev",
    "input_mode": "text",
    "result_type": "file",
}


def _normalize_rows(value: object) -> list[dict]:
    if isinstance(value, dict):
        return [value]
    if isinstance(value, list):
        rows = []
        for item in value:
            if isinstance(item, dict):
                rows.append(item)
            else:
                rows.append({"value": item})
        return rows
    raise AppException(message="JSON 内容必须是对象或数组", code=4001, status_code=400)


def run(text: str, output_dir: str, sheet_name: str = "Sheet1", **_: dict) -> str:
    if not text.strip():
        raise AppException(message="请输入 JSON 内容", code=4001, status_code=400)

    try:
        value = json.loads(text)
    except json.JSONDecodeError as exc:
        raise AppException(message=f"JSON 格式无效：{exc.msg}", code=4001, status_code=400) from exc

    rows = _normalize_rows(value)
    headers = sorted({key for row in rows for key in row.keys()}) or ["value"]

    workbook = Workbook()
    worksheet = workbook.active
    safe_sheet_name = (sheet_name or "Sheet1").strip()[:31] or "Sheet1"
    worksheet.title = safe_sheet_name
    worksheet.append(headers)

    for row in rows:
        values = []
        for header in headers:
            cell_value = row.get(header, "")
            if isinstance(cell_value, (dict, list)):
                values.append(json.dumps(cell_value, ensure_ascii=False))
            else:
                values.append(cell_value)
        worksheet.append(values)

    target_path = Path(output_dir) / "json-to-xlsx.xlsx"
    workbook.save(target_path)
    return str(target_path)
