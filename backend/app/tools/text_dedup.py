from app.utils.text_utils import deduplicate_lines


TOOL_META = {
    "slug": "text-dedup",
    "name": "文本去重",
    "category": "text",
    "input_mode": "text",
    "result_type": "text",
}


def run(text: str, keep_empty: bool = False, **_: dict) -> str:
    return deduplicate_lines(text=text, keep_empty=keep_empty)
