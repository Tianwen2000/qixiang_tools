"""文件说明：实现「今日股票指数」工具的后端逻辑。"""

from app.tools.price_snapshot import run_stock_index


TOOL_META = {
    "slug": "today-stock-index",
    "name": "今日股票指数",
    "category": "other",
    "input_mode": "text",
    "result_type": "text",
}


def run(text: str = "", **kwargs: dict) -> str:
    return run_stock_index(text=text, **kwargs)
