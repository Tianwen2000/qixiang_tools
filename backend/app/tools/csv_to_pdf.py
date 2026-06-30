"""文件说明：实现「CSV 转 PDF」工具的后端逻辑。"""

from pathlib import Path

from app.utils.document_utils import extract_csv_rows, tables_to_sections, write_text_pdf


TOOL_META = {
    "slug": "csv-to-pdf",
    "name": "CSV 转 PDF",
    "category": "text",
    "input_mode": "file",
    "result_type": "file",
}


def run(input_path: str, output_dir: str, title: str = "", **_: dict) -> str:
    sections = tables_to_sections([("CSV 数据", extract_csv_rows(input_path))])
    pdf_title = title.strip() or "CSV 转 PDF"
    return write_text_pdf(sections, Path(output_dir) / "csv-to-pdf.pdf", title=pdf_title)
