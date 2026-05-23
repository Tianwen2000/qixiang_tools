from pathlib import Path

from app.utils.document_utils import heic_to_pdf as convert_heic_to_pdf


TOOL_META = {
    "slug": "heic-to-pdf",
    "name": "HEIC 转 PDF",
    "category": "text",
    "input_mode": "file",
    "result_type": "file",
}


def run(input_path: str, output_dir: str, **_: dict) -> str:
    return convert_heic_to_pdf(input_path, Path(output_dir) / "heic-to-pdf.pdf")
