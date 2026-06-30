"""文件说明：实现「Word 转 PDF」工具的后端逻辑。"""

from pathlib import Path

from app.utils.document_utils import extract_docx_sections, write_text_pdf


TOOL_META = {
    "slug": "docx-to-pdf",
    "name": "Word 转 PDF",
    "category": "text",
    "input_mode": "file",
    "result_type": "file",
}


def run(input_path: str, output_dir: str, **_: dict) -> str:
    sections = extract_docx_sections(input_path)
    return write_text_pdf(sections, Path(output_dir) / "word-to-pdf.pdf", title="Word 转 PDF")
