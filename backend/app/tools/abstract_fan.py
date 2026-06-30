"""文件说明：实现「赛博抽象小风扇」工具的后端逻辑。"""

TOOL_META = {
    "slug": "abstract-fan",
    "name": "抽象小风扇",
    "category": "other",
    "input_mode": "local",
    "result_type": "text",
}


def run(text: str = "", **_: dict) -> str:
    _ = text
    return "该工具为前端本地抽象小风扇，请在页面中直接点击按钮体验。"
