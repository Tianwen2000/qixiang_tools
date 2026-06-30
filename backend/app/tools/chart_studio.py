"""文件说明：实现「K 线图制作」工具的后端逻辑。"""

TOOL_META = {
    "slug": "chart-studio",
    "name": "图表工作台",
    "category": "chart",
    "input_mode": "local",
    "result_type": "text",
}


def run(text: str = "", **_: dict) -> str:
    _ = text
    return "该工具为前端本地图表工作台，请在页面中直接编辑数据并生成图表。"
