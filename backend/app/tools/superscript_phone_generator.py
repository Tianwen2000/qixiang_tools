"""文件说明：实现「上标电话生成器」工具的后端逻辑。"""

from app.core.exceptions import AppException


TOOL_META = {
    "slug": "superscript-phone-generator",
    "name": "上标电话生成器",
    "category": "text",
    "input_mode": "text",
    "result_type": "text",
}


SUPERSCRIPT_MAP = str.maketrans(
    {
        "0": "⁰",
        "1": "¹",
        "2": "²",
        "3": "³",
        "4": "⁴",
        "5": "⁵",
        "6": "⁶",
        "7": "⁷",
        "8": "⁸",
        "9": "⁹",
        "+": "⁺",
        "-": "⁻",
        "(": "⁽",
        ")": "⁾",
        " ": " ",
    }
)


def run(text: str, **_: dict) -> str:
    if not text.strip():
        raise AppException(message="请输入手机号或数字内容", code=4001, status_code=400)
    return text.translate(SUPERSCRIPT_MAP)
