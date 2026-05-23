from pathlib import Path

from app.utils.document_utils import build_html_from_sections, extract_ppt_sections


TOOL_META = {
    "slug": "ppt-to-html",
    "name": "PPT 转 HTML",
    "category": "text",
    "input_mode": "file",
    "result_type": "file",
}


def run(input_path: str, output_dir: str, title: str = "", **_: dict) -> str:
    sections = extract_ppt_sections(input_path)
    return build_html_from_sections(sections, Path(output_dir) / "ppt-to-html.html", title=title.strip() or "PPT 转 HTML")
