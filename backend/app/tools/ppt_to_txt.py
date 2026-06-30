"""文件说明：实现「PPT 转 TXT」工具的后端逻辑。"""

from pathlib import Path

from app.utils.document_utils import extract_ppt_sections, sections_to_text, write_plain_text


TOOL_META = {
    "slug": "ppt-to-txt",
    "name": "PPT 转 TXT",
    "category": "text",
    "input_mode": "file",
    "result_type": "file",
}


def run(input_path: str, output_dir: str, **_: dict) -> str:
    return write_plain_text(sections_to_text(extract_ppt_sections(input_path)), Path(output_dir) / "ppt-to-txt.txt")
