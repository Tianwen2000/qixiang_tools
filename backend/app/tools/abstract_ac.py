TOOL_META = {
    "slug": "abstract-ac",
    "name": "抽象小空调",
    "category": "other",
    "input_mode": "local",
    "result_type": "text",
}


def run(text: str = "", **_: dict) -> str:
    _ = text
    return "该工具为前端本地抽象小空调，请在页面中直接点击按钮体验。"
