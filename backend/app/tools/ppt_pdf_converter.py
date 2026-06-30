"""文件说明：实现「PPT 和 PDF 互转」工具的后端逻辑。"""

from app.tools.format_pair_converter import PPT_PDF_HANDLERS, dispatch_pair


def run(input_path: str, output_dir: str, direction: str = "ppt_to_pdf", **params: dict) -> str:
    return dispatch_pair(input_path, output_dir, direction, PPT_PDF_HANDLERS, **params)
