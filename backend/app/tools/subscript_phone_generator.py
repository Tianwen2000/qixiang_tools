"""文件说明：实现「下标电话生成器」工具的后端逻辑。"""

from app.core.exceptions import AppException


TOOL_META = {
    "slug": "subscript-phone-generator",
    "name": "下标电话生成器",
    "category": "text",
    "input_mode": "text",
    "result_type": "text",
}


SUBSCRIPT_MAP = str.maketrans(
    {
        "0": "₀",
        "1": "₁",
        "2": "₂",
        "3": "₃",
        "4": "₄",
        "5": "₅",
        "6": "₆",
        "7": "₇",
        "8": "₈",
        "9": "₉",
        "+": "₊",
        "-": "₋",
        "(": "₍",
        ")": "₎",
        " ": " ",
    }
)


def run(text: str, **_: dict) -> str:
    if not text.strip():
        raise AppException(message="请输入手机号或数字内容", code=4001, status_code=400)
    return text.translate(SUBSCRIPT_MAP)
