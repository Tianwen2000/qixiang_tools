from app.utils.image_utils import extract_office_media


TOOL_META = {
    "slug": "excel-image-extractor",
    "name": "Excel 提取图片",
    "category": "image",
    "input_mode": "file",
    "result_type": "file",
}


def run(input_path: str, output_dir: str, **_: dict) -> str:
    return extract_office_media(input_path, output_dir, "xl/media/", "excel-images.zip")
