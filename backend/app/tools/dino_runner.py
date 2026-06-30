"""文件说明：实现「恐龙快跑」工具的后端逻辑。"""

TOOL_META = {
    "slug": "dino-runner",
    "name": "恐龙快跑",
    "category": "game",
    "input_mode": "local",
    "result_type": "text",
}


def run(text: str = "", **_: dict) -> str:
    _ = text
    return "该工具为前端本地小游戏，请在页面中直接开始游戏。"
