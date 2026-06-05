from app.tools.price_snapshot import run_exchange_rate


TOOL_META = {
    "slug": "today-exchange-rate",
    "name": "今日汇率",
    "category": "other",
    "input_mode": "text",
    "result_type": "text",
}


def run(text: str = "", **kwargs: dict) -> str:
    return run_exchange_rate(text=text, **kwargs)
