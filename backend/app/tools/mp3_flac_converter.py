"""文件说明：实现「MP3 和 FLAC 互转」工具的后端逻辑。"""

from app.tools.media_converter import convert_media


TOOL_META = {
    "slug": "mp3-flac-converter",
    "name": "MP3 / FLAC 互转",
    "category": "format",
    "input_mode": "file",
    "result_type": "file",
}


def run(input_path: str, output_dir: str, direction: str = "mp3_to_flac", **_: dict) -> str:
    return convert_media(input_path, output_dir, TOOL_META["slug"], direction)
