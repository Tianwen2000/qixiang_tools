"""文件说明：实现「图片 EXIF 读取」工具的后端逻辑。"""

import json
from pathlib import Path

from PIL import ExifTags

from app.utils.image_utils import load_image


TOOL_META = {
    "slug": "image-exif-reader",
    "name": "图片 EXIF 读取",
    "category": "image",
    "input_mode": "file",
    "result_type": "text",
}


def run(input_path: str, filename: str = "", **_: dict) -> str:
    image = load_image(input_path)
    exif_data = image.getexif()
    payload = {
        "filename": filename or Path(input_path).name,
        "format": image.format,
        "size": {"width": image.width, "height": image.height},
        "mode": image.mode,
        "exif": {},
    }
    for key, value in exif_data.items():
        tag = ExifTags.TAGS.get(key, str(key))
        payload["exif"][tag] = value
    return json.dumps(payload, ensure_ascii=False, indent=2, default=str)
