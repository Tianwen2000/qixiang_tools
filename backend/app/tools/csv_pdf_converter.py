from app.tools.format_pair_converter import CSV_PDF_HANDLERS, dispatch_pair


def run(input_path: str, output_dir: str, direction: str = "csv_to_pdf", **params: dict) -> str:
    return dispatch_pair(input_path, output_dir, direction, CSV_PDF_HANDLERS, **params)
