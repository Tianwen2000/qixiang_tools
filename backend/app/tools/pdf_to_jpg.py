"""文件说明：实现「PDF 转 JPG」工具的后端逻辑。"""

from app.utils.document_utils import render_pdf_pages_to_jpg


TOOL_META = {
    "slug": "pdf-to-jpg",
    "name": "PDF 转 JPG",
    "category": "text",
    "input_mode": "file",
    "result_type": "file",
}


def run(input_path: str, output_dir: str, scale: float = 2, quality: int = 90, **_: dict) -> str:
    return render_pdf_pages_to_jpg(input_path, output_dir, scale=float(scale), quality=int(quality))
