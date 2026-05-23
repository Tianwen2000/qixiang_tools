TOOL_META = {
    "slug": "time-studio",
    "name": "时间工作台",
    "category": "time",
    "input_mode": "local",
    "result_type": "text",
}


def run(text: str = "", **_: dict) -> str:
    _ = text
    return "该工具为前端本地时间工作台，请在页面中直接进行时间计算和查看。"
