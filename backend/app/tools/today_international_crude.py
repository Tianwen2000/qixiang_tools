from app.tools.price_snapshot import run_international_crude


TOOL_META = {
    "slug": "today-international-crude",
    "name": "今日国际原油价格",
    "category": "other",
    "input_mode": "text",
    "result_type": "text",
}


def run(text: str = "", **kwargs: dict) -> str:
    return run_international_crude(text=text, **kwargs)
