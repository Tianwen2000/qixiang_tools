"""文件说明：实现「2048 数字合成」工具的后端逻辑。"""

TOOL_META = {
    "slug": "game-2048",
    "name": "2048 数字合成",
    "category": "game",
    "input_mode": "local",
    "result_type": "text",
}


def run(text: str = "", **_: dict) -> str:
    _ = text
    return "该工具为前端本地小游戏，请在页面中直接开始游戏。"
