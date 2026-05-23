from pathlib import Path

from app.utils.document_utils import extract_pdf_sections, sections_to_text, write_plain_text


TOOL_META = {
    "slug": "pdf-to-txt",
    "name": "PDF 转 TXT",
    "category": "text",
    "input_mode": "file",
    "result_type": "file",
}


def run(input_path: str, output_dir: str, **_: dict) -> str:
    text = sections_to_text(extract_pdf_sections(input_path))
    return write_plain_text(text, Path(output_dir) / "pdf-to-txt.txt")
