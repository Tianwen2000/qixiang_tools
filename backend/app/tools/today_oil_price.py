"""文件说明：实现「今日油价」工具的后端逻辑。"""

from app.tools.price_snapshot import run_domestic_oil


TOOL_META = {
    "slug": "today-oil-price",
    "name": "今日油价",
    "category": "other",
    "input_mode": "text",
    "result_type": "text",
}


def run(text: str = "", **kwargs: dict) -> str:
    return run_domestic_oil(text=text, **kwargs)
