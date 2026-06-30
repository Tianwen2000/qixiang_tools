"""文件说明：实现「CSV 和 HTML 互转」工具的后端逻辑。"""

from app.tools.format_pair_converter import CSV_HTML_HANDLERS, dispatch_pair


def run(input_path: str, output_dir: str, direction: str = "csv_to_html", **params: dict) -> str:
    return dispatch_pair(input_path, output_dir, direction, CSV_HTML_HANDLERS, **params)
