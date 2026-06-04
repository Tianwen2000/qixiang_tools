TOOL_META = {
    "slug": "image-inspector",
    "name": "图片详情查看",
    "category": "image",
    "input_mode": "local",
    "result_type": "text",
}


def run(text: str = "", **_: dict) -> str:
    _ = text
    return "该工具在浏览器本地读取图片详情，请在页面中上传图片查看，不依赖后端执行。"
