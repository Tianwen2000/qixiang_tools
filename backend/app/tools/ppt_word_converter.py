"""文件说明：实现「PPT 和 Word 互转」工具的后端逻辑。"""

from app.tools.format_pair_converter import PPT_WORD_HANDLERS, dispatch_pair


def run(input_path: str, output_dir: str, direction: str = "ppt_to_word", **params: dict) -> str:
    return dispatch_pair(input_path, output_dir, direction, PPT_WORD_HANDLERS, **params)
