"""文件说明：实现「进制转换」工具的后端逻辑。"""

import string

from app.core.exceptions import AppException


TOOL_META = {
    "slug": "base-converter",
    "name": "进制转换",
    "category": "utility",
    "input_mode": "text",
    "result_type": "text",
}


ALPHABET = string.digits + string.ascii_uppercase
SUPPORTED_BASES = {2, 8, 10, 16, 32, 36}


def _encode(number: int, base: int) -> str:
    if number == 0:
        return "0"

    negative = number < 0
    number = abs(number)
    chars: list[str] = []
    while number:
        number, remainder = divmod(number, base)
        chars.append(ALPHABET[remainder])
    result = "".join(reversed(chars))
    return f"-{result}" if negative else result


def _clean_prefix(value: str, base: int) -> str:
    cleaned = value.strip().upper()
    prefixes = {2: "0B", 8: "0O", 16: "0X"}
    prefix = prefixes.get(base)
    if prefix and cleaned.startswith(prefix):
        return cleaned[len(prefix) :]
    if prefix and cleaned.startswith(f"-{prefix}"):
        return f"-{cleaned[len(prefix) + 1 :]}"
    return cleaned


def run(text: str, from_base: int = 10, to_base: int = 16, **_: dict) -> str:
    from_base = int(from_base)
    to_base = int(to_base)
    if from_base not in SUPPORTED_BASES or to_base not in SUPPORTED_BASES:
        raise AppException(message="不支持的进制", code=4001, status_code=400)

    cleaned = _clean_prefix(text, from_base)
    try:
        number = int(cleaned, from_base)
    except ValueError as exc:
        raise AppException(message=f"{from_base} 进制数字无效", code=4001, status_code=400) from exc

    return _encode(number, to_base)
