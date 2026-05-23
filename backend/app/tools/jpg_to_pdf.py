from pathlib import Path

from app.utils.document_utils import image_to_pdf


TOOL_META = {
    "slug": "jpg-to-pdf",
    "name": "JPG 转 PDF",
    "category": "text",
    "input_mode": "file",
    "result_type": "file",
}


def run(input_path: str, output_dir: str, **_: dict) -> str:
    return image_to_pdf(input_path, Path(output_dir) / "image-to-pdf.pdf")
