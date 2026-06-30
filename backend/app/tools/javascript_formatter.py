"""文件说明：实现「Javascript 格式化/压缩」工具的后端逻辑。"""

import jsbeautifier
from rjsmin import jsmin

from app.core.exceptions import AppException


TOOL_META = {
    "slug": "javascript-formatter",
    "name": "Javascript 格式化/压缩",
    "category": "dev",
    "input_mode": "text",
    "result_type": "text",
}


def _format_js(text: str) -> str:
    options = jsbeautifier.default_options()
    options.indent_size = 2
    options.preserve_newlines = True
    return jsbeautifier.beautify(text, options)


def run(text: str, action: str = "format", **_: dict) -> str:
    if action == "format":
        return _format_js(text)
    if action == "minify":
        try:
            return jsmin(text)
        except Exception as exc:
            raise AppException(message=f"Javascript 格式无效：{exc}", code=4001, status_code=400) from exc
    raise AppException(message="操作方式无效", code=4001, status_code=400)
