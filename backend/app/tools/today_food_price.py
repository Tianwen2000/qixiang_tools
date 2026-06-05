from app.tools.price_snapshot import run_food_price


TOOL_META = {
    "slug": "today-food-price",
    "name": "今日猪肉/鸡蛋/蔬菜价格",
    "category": "other",
    "input_mode": "text",
    "result_type": "text",
}


def run(text: str = "", **kwargs: dict) -> str:
    return run_food_price(text=text, **kwargs)
