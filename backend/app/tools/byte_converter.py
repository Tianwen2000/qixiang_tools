"""文件说明：实现「字节转换」工具的后端逻辑。"""

from decimal import Decimal, InvalidOperation

from app.core.exceptions import AppException


TOOL_META = {
    "slug": "byte-converter",
    "name": "字节转换",
    "category": "utility",
    "input_mode": "text",
    "result_type": "text",
}


UNIT_FACTORS = {
    "B": Decimal("1"),
    "KB": Decimal("1000"),
    "MB": Decimal("1000") ** 2,
    "GB": Decimal("1000") ** 3,
    "TB": Decimal("1000") ** 4,
    "KiB": Decimal("1024"),
    "MiB": Decimal("1024") ** 2,
    "GiB": Decimal("1024") ** 3,
    "TiB": Decimal("1024") ** 4,
}


def _format_decimal(value: Decimal) -> str:
    normalized = value.normalize()
    text = format(normalized, "f")
    return text.rstrip("0").rstrip(".") if "." in text else text


def run(text: str, from_unit: str = "B", to_unit: str = "MB", **_: dict) -> str:
    if from_unit not in UNIT_FACTORS or to_unit not in UNIT_FACTORS:
        raise AppException(message="不支持的单位", code=4001, status_code=400)
    try:
        amount = Decimal(text.strip())
    except InvalidOperation as exc:
        raise AppException(message="数字输入无效", code=4001, status_code=400) from exc

    bytes_value = amount * UNIT_FACTORS[from_unit]
    converted = bytes_value / UNIT_FACTORS[to_unit]
    return f"{_format_decimal(converted)} {to_unit}"
