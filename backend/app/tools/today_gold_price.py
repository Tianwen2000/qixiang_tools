from app.tools.price_snapshot import run_gold


TOOL_META = {
    "slug": "today-gold-price",
    "name": "今日金价",
    "category": "other",
    "input_mode": "text",
    "result_type": "text",
}


def run(text: str = "", **kwargs: dict) -> str:
    return run_gold(text=text, **kwargs)
