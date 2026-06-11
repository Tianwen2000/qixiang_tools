from app.tools.format_pair_converter import PDF_EPUB_HANDLERS, dispatch_pair


def run(input_path: str, output_dir: str, direction: str = "pdf_to_epub", **params: dict) -> str:
    return dispatch_pair(input_path, output_dir, direction, PDF_EPUB_HANDLERS, **params)
