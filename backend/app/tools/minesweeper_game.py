TOOL_META = {
    "slug": "minesweeper-game",
    "name": "扫雷",
    "category": "game",
    "input_mode": "local",
    "result_type": "text",
}


def run(text: str = "", **_: dict) -> str:
    _ = text
    return "该工具为前端本地小游戏，请在页面中直接开始游戏。"
