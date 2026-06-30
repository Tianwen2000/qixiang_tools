"""文件说明：实现「CSS 格式化/压缩」工具的后端逻辑。"""

import cssbeautifier
from rcssmin import cssmin

from app.core.exceptions import AppException


TOOL_META = {
    "slug": "css-formatter",
    "name": "CSS 格式化/压缩",
    "category": "dev",
    "input_mode": "text",
    "result_type": "text",
}


def _format_css(text: str) -> str:
    options = cssbeautifier.default_options()
    options.indent_size = 2
    return cssbeautifier.beautify(text, options)


def run(text: str, action: str = "format", **_: dict) -> str:
    if action == "format":
        return _format_css(text)
    if action == "minify":
        try:
            return cssmin(text)
        except Exception as exc:
            raise AppException(message=f"CSS 格式无效：{exc}", code=4001, status_code=400) from exc
    raise AppException(message="操作方式无效", code=4001, status_code=400)
