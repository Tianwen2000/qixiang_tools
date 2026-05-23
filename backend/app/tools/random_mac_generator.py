import secrets

from app.core.exceptions import AppException


TOOL_META = {
    "slug": "random-mac-generator",
    "name": "随机 MAC 地址生成器",
    "category": "utility",
    "input_mode": "text",
    "result_type": "text",
}


def _format_mac(parts: list[str], format_type: str) -> str:
    if format_type == "colon":
        return ":".join(parts)
    if format_type == "hyphen":
        return "-".join(parts)
    if format_type == "plain":
        return "".join(parts)
    raise AppException(message="MAC 地址格式无效", code=4001, status_code=400)


def run(text: str = "", format_type: str = "colon", count: int = 1, **_: dict) -> str:
    _ = text
    count = int(count)
    if count not in {1, 5, 10}:
        raise AppException(message="生成数量必须是 1、5 或 10", code=4001, status_code=400)

    items = []
    for _ in range(count):
        first_octet = (secrets.randbits(8) | 0x02) & 0xFE
        octets = [first_octet] + [secrets.randbits(8) for _ in range(5)]
        parts = [f"{item:02X}" for item in octets]
        items.append(_format_mac(parts, format_type))
    return "\n".join(items)
