from pathlib import Path

from app.utils.document_utils import extract_spreadsheet_sheets, tables_to_sections, write_text_pdf


TOOL_META = {
    "slug": "excel-to-pdf",
    "name": "Excel 转 PDF",
    "category": "text",
    "input_mode": "file",
    "result_type": "file",
}


def run(input_path: str, output_dir: str, title: str = "", **_: dict) -> str:
    sections = tables_to_sections(extract_spreadsheet_sheets(input_path))
    pdf_title = title.strip() or "Excel 转 PDF"
    return write_text_pdf(sections, Path(output_dir) / "excel-to-pdf.pdf", title=pdf_title)
