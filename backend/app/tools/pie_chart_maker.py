"""文件说明：实现 pie chart maker 工具的后端逻辑。"""

TOOL_META = {
    "slug": "pie-chart-maker",
    "name": "饼图制作",
    "category": "chart",
    "input_mode": "local",
    "result_type": "text",
}


def run(text: str = "", **_: dict) -> str:
    _ = text
    return "该工具为前端本地绘图工具，请在页面中直接编辑数据并生成图表。"
