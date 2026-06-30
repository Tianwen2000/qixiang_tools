"""文件说明：实现「罗马数字转换」工具的后端逻辑。"""

from app.core.exceptions import AppException


TOOL_META = {
    "slug": "roman-numeral-converter",
    "name": "罗马数字转换",
    "category": "utility",
    "input_mode": "text",
    "result_type": "text",
}


ROMAN_MAP = [
    ("M", 1000),
    ("CM", 900),
    ("D", 500),
    ("CD", 400),
    ("C", 100),
    ("XC", 90),
    ("L", 50),
    ("XL", 40),
    ("X", 10),
    ("IX", 9),
    ("V", 5),
    ("IV", 4),
    ("I", 1),
]


def _to_roman(number: int) -> str:
    if number <= 0 or number >= 4000:
        raise AppException(message="数字必须在 1 到 3999 之间", code=4001, status_code=400)
    result: list[str] = []
    remaining = number
    for symbol, value in ROMAN_MAP:
        while remaining >= value:
            result.append(symbol)
            remaining -= value
    return "".join(result)


def _from_roman(value: str) -> int:
    text = value.strip().upper()
    if not text:
        raise AppException(message="请输入罗马数字", code=4001, status_code=400)
    index = 0
    total = 0
    for symbol, amount in ROMAN_MAP:
        while text[index : index + len(symbol)] == symbol:
            total += amount
            index += len(symbol)
            if index >= len(text):
                break
    if _to_roman(total) != text:
        raise AppException(message="罗马数字无效", code=4001, status_code=400)
    return total


def run(text: str, action: str = "to_roman", **_: dict) -> str:
    if action == "to_roman":
        try:
            number = int(text.strip())
        except ValueError as exc:
            raise AppException(message="输入内容必须是整数", code=4001, status_code=400) from exc
        return _to_roman(number)
    if action == "from_roman":
        return str(_from_roman(text))
    raise AppException(message="操作方式无效", code=4001, status_code=400)
