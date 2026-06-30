"""文件说明：实现「WAV 和 MP3 互转」工具的后端逻辑。"""

from app.tools.media_converter import convert_media


TOOL_META = {
    "slug": "wav-mp3-converter",
    "name": "WAV / MP3 互转",
    "category": "format",
    "input_mode": "file",
    "result_type": "file",
}


def run(input_path: str, output_dir: str, direction: str = "wav_to_mp3", **_: dict) -> str:
    return convert_media(input_path, output_dir, TOOL_META["slug"], direction)
