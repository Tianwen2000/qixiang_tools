from pathlib import Path

from app.utils.document_utils import extract_ppt_sections, write_text_pdf


TOOL_META = {
    "slug": "ppt-to-pdf",
    "name": "PPT 转 PDF",
    "category": "text",
    "input_mode": "file",
    "result_type": "file",
}


def run(input_path: str, output_dir: str, title: str = "", **_: dict) -> str:
    sections = extract_ppt_sections(input_path)
    pdf_title = title.strip() or "PPT 转 PDF"
    return write_text_pdf(sections, Path(output_dir) / "ppt-to-pdf.pdf", title=pdf_title)
