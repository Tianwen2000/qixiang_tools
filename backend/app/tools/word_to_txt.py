"""文件说明：实现「Word 转 TXT」工具的后端逻辑。"""

from pathlib import Path

from app.utils.document_utils import extract_docx_sections, sections_to_text, write_plain_text


TOOL_META = {
    "slug": "word-to-txt",
    "name": "Word 转 TXT",
    "category": "text",
    "input_mode": "file",
    "result_type": "file",
}


def run(input_path: str, output_dir: str, **_: dict) -> str:
    text = sections_to_text(extract_docx_sections(input_path))
    return write_plain_text(text, Path(output_dir) / "word-to-txt.txt")
