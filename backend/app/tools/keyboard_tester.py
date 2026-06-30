"""文件说明：实现「键盘测试」工具的后端逻辑。"""

TOOL_META = {
    "slug": "keyboard-tester",
    "name": "键盘测试",
    "category": "other",
    "input_mode": "local",
    "result_type": "text",
}


def run(text: str = "", **_: dict) -> str:
    _ = text
    return "该工具为前端本地键盘检测工具，请在页面中直接按键测试。"
