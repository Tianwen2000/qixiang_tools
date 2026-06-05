from app.tools.price_snapshot import run_building_materials


TOOL_META = {
    "slug": "today-building-materials",
    "name": "今日钢材/水泥/建材价格",
    "category": "other",
    "input_mode": "text",
    "result_type": "text",
}


def run(text: str = "", **kwargs: dict) -> str:
    return run_building_materials(text=text, **kwargs)
