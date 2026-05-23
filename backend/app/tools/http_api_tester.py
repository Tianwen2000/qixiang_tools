TOOL_META = {
    "slug": "http-api-tester",
    "name": "Http 接口测试",
    "category": "dev",
    "input_mode": "form",
    "result_type": "text",
}


def run(text: str = "", **_: dict) -> str:
    _ = text
    return "请在前端页面中使用该工具，HTTP 请求会在浏览器中直接发起。"
