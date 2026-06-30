"""文件说明：实现「TXT 转 PDF」工具的后端逻辑。"""

from pathlib import Path

from app.utils.document_utils import read_plain_text, write_text_pdf


TOOL_META = {
    "slug": "txt-to-pdf",
    "name": "TXT 转 PDF",
    "category": "text",
    "input_mode": "file",
    "result_type": "file",
}


def run(input_path: str, output_dir: str, title: str = "", **_: dict) -> str:
    text = read_plain_text(input_path)
    pdf_title = title.strip() or "TXT 转 PDF"
    return write_text_pdf([text], Path(output_dir) / "txt-to-pdf.pdf", title=pdf_title)
