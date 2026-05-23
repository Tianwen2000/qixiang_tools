from pathlib import Path

from app.utils.document_utils import build_docx_from_sections, read_plain_text


TOOL_META = {
    "slug": "txt-to-word",
    "name": "TXT 转 Word",
    "category": "text",
    "input_mode": "file",
    "result_type": "file",
}


def run(input_path: str, output_dir: str, title: str = "", **_: dict) -> str:
    text = read_plain_text(input_path)
    doc_title = title.strip() or "TXT 转 Word"
    return build_docx_from_sections([text], Path(output_dir) / "txt-to-word.docx", title=doc_title)
