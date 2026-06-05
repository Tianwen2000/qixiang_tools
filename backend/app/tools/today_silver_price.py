from app.tools.price_snapshot import run_silver


TOOL_META = {
    "slug": "today-silver-price",
    "name": "今日白银价格",
    "category": "other",
    "input_mode": "text",
    "result_type": "text",
}


def run(text: str = "", **kwargs: dict) -> str:
    return run_silver(text=text, **kwargs)
