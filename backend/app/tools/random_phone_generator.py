import secrets

from app.core.exceptions import AppException


TOOL_META = {
    "slug": "random-phone-generator",
    "name": "随机手机号生成器",
    "category": "dev",
    "input_mode": "text",
    "result_type": "text",
}


PREFIXES = [
    "130",
    "131",
    "132",
    "133",
    "135",
    "136",
    "137",
    "138",
    "139",
    "150",
    "151",
    "152",
    "155",
    "156",
    "157",
    "158",
    "159",
    "166",
    "171",
    "172",
    "173",
    "175",
    "176",
    "177",
    "178",
    "180",
    "181",
    "182",
    "183",
    "184",
    "185",
    "186",
    "187",
    "188",
    "189",
    "191",
    "198",
    "199",
]


def run(text: str = "", count: int = 1, **_: dict) -> str:
    _ = text
    count = int(count)
    if count not in {1, 5, 10}:
        raise AppException(message="生成数量必须是 1、5 或 10", code=4001, status_code=400)
    values = []
    for _ in range(count):
        prefix = secrets.choice(PREFIXES)
        suffix = "".join(str(secrets.randbelow(10)) for _ in range(8))
        values.append(prefix + suffix)
    return "\n".join(values)
