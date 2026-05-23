TOOL_META = {
    "slug": "websocket-tester",
    "name": "Websocket 接口测试",
    "category": "dev",
    "input_mode": "form",
    "result_type": "text",
}


def run(text: str = "", **_: dict) -> str:
    _ = text
    return "请在前端页面中使用该工具，WebSocket 连接会在浏览器中直接建立。"
