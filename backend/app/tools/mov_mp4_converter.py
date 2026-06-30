"""文件说明：实现「MOV 和 MP4 互转」工具的后端逻辑。"""

from app.tools.media_converter import convert_media


TOOL_META = {
    "slug": "mov-mp4-converter",
    "name": "MOV / MP4 互转",
    "category": "format",
    "input_mode": "file",
    "result_type": "file",
}


def run(input_path: str, output_dir: str, direction: str = "mov_to_mp4", **_: dict) -> str:
    return convert_media(input_path, output_dir, TOOL_META["slug"], direction)
