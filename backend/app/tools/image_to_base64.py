import base64
import mimetypes
from pathlib import Path


TOOL_META = {
    "slug": "image-to-base64",
    "name": "图片转 Base64",
    "category": "image",
    "input_mode": "file",
    "result_type": "text",
}


def run(input_path: str, output_dir: str, filename: str = "", content_type: str = "", **_: dict) -> str:
    _ = output_dir
    path = Path(input_path)
    mime = content_type or mimetypes.guess_type(filename or path.name)[0] or "application/octet-stream"
    encoded = base64.b64encode(path.read_bytes()).decode("utf-8")
    return f"data:{mime};base64,{encoded}"
