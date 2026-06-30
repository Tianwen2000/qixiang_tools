"""文件说明：实现「CSV 转 TXT」工具的后端逻辑。"""

from pathlib import Path

from app.utils.document_utils import extract_csv_rows, tables_to_sections, write_plain_text


TOOL_META = {
    "slug": "csv-to-txt",
    "name": "CSV 转 TXT",
    "category": "text",
    "input_mode": "file",
    "result_type": "file",
}


def run(input_path: str, output_dir: str, **_: dict) -> str:
    sections = tables_to_sections([("CSV 数据", extract_csv_rows(input_path))])
    return write_plain_text("\n\n".join(sections), Path(output_dir) / "csv-to-txt.txt")
