"""文件说明：实现「CSV 转 HTML」工具的后端逻辑。"""

from pathlib import Path

from app.utils.document_utils import build_html_from_tables, extract_csv_rows


TOOL_META = {
    "slug": "csv-to-html",
    "name": "CSV 转 HTML",
    "category": "text",
    "input_mode": "file",
    "result_type": "file",
}


def run(input_path: str, output_dir: str, title: str = "", **_: dict) -> str:
    rows = extract_csv_rows(input_path)
    return build_html_from_tables([("CSV 数据", rows)], Path(output_dir) / "csv-to-html.html", title=title.strip() or "CSV 转 HTML")
