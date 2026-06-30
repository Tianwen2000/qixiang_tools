"""文件说明：实现「PDF 转 Word」工具的后端逻辑。"""

from pathlib import Path

from app.utils.document_utils import build_docx_from_sections, extract_pdf_sections


TOOL_META = {
    "slug": "pdf-to-word",
    "name": "PDF 转 Word",
    "category": "text",
    "input_mode": "file",
    "result_type": "file",
}


def run(input_path: str, output_dir: str, **_: dict) -> str:
    sections = extract_pdf_sections(input_path)
    return build_docx_from_sections(sections, Path(output_dir) / "pdf-to-word.docx", title="PDF 转 Word")
