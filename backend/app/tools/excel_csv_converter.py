from app.tools.format_pair_converter import EXCEL_CSV_HANDLERS, dispatch_pair


def run(input_path: str, output_dir: str, direction: str = "excel_to_csv", **params: dict) -> str:
    return dispatch_pair(input_path, output_dir, direction, EXCEL_CSV_HANDLERS, **params)
