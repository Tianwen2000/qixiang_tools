import secrets
from datetime import date, timedelta

from app.core.exceptions import AppException


TOOL_META = {
    "slug": "random-id-card-generator",
    "name": "随机身份证生成器",
    "category": "dev",
    "input_mode": "text",
    "result_type": "text",
}


REGION_CODES = [
    "110101",
    "120101",
    "310101",
    "440103",
    "440106",
    "440305",
    "320102",
    "330106",
    "350203",
    "420102",
    "510104",
]

CHECKSUM_WEIGHTS = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
CHECKSUM_CHARS = "10X98765432"


def _random_birthdate() -> str:
    start = date(1970, 1, 1)
    end = date(2005, 12, 31)
    offset = secrets.randbelow((end - start).days + 1)
    return (start + timedelta(days=offset)).strftime("%Y%m%d")


def _sequence_code(gender: str) -> str:
    if gender == "male":
        base = secrets.randbelow(500) * 2 + 1
    elif gender == "female":
        base = secrets.randbelow(500) * 2
    elif gender == "random":
        base = secrets.randbelow(1000)
    else:
        raise AppException(message="性别参数必须是 random、male 或 female", code=4001, status_code=400)
    return f"{base:03d}"


def _checksum(first17: str) -> str:
    total = sum(int(char) * weight for char, weight in zip(first17, CHECKSUM_WEIGHTS))
    return CHECKSUM_CHARS[total % 11]


def run(text: str = "", count: int = 1, gender: str = "random", **_: dict) -> str:
    _ = text
    count = int(count)
    if count not in {1, 5, 10}:
        raise AppException(message="生成数量必须是 1、5 或 10", code=4001, status_code=400)

    values = []
    for _ in range(count):
        first17 = secrets.choice(REGION_CODES) + _random_birthdate() + _sequence_code(gender)
        values.append(first17 + _checksum(first17))
    return "\n".join(values)
