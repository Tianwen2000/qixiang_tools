"""文件说明：实现「随机 IP 地址生成器」工具的后端逻辑。"""

import ipaddress
import secrets

from app.core.exceptions import AppException


TOOL_META = {
    "slug": "random-ip-generator",
    "name": "随机 IP 地址生成器",
    "category": "utility",
    "input_mode": "text",
    "result_type": "text",
}


def run(text: str = "", version: str = "ipv4", count: int = 1, **_: dict) -> str:
    _ = text
    count = int(count)
    if count not in {1, 5, 10}:
        raise AppException(message="生成数量必须是 1、5 或 10", code=4001, status_code=400)
    if version not in {"ipv4", "ipv6"}:
        raise AppException(message="IP 版本必须是 ipv4 或 ipv6", code=4001, status_code=400)

    result = []
    for _ in range(count):
        if version == "ipv4":
            result.append(str(ipaddress.IPv4Address(secrets.randbits(32))))
        else:
            result.append(str(ipaddress.IPv6Address(secrets.randbits(128))))
    return "\n".join(result)
