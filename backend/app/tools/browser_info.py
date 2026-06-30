"""文件说明：实现「在线白板」工具的后端逻辑。"""

TOOL_META = {
    "slug": "browser-info",
    "name": "获取浏览器信息",
    "category": "dev",
    "input_mode": "form",
    "result_type": "text",
}


def run(text: str = "", **_: dict) -> str:
    _ = text
    return "请在前端页面中使用该工具，浏览器环境信息会在本地实时展示。"
