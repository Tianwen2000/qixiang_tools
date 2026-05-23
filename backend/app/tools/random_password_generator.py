import random
import secrets
import string

from app.core.exceptions import AppException


TOOL_META = {
    "slug": "random-password-generator",
    "name": "随机密码生成器",
    "category": "utility",
    "input_mode": "text",
    "result_type": "text",
}


SYMBOLS = "!@#$%^&*()-_=+[]{}?"


def _strong_password(length: int) -> str:
    pools = [
        string.ascii_lowercase,
        string.ascii_uppercase,
        string.digits,
        SYMBOLS,
    ]
    chars = [secrets.choice(pool) for pool in pools]
    alphabet = "".join(pools)
    chars.extend(secrets.choice(alphabet) for _ in range(length - len(chars)))
    random.SystemRandom().shuffle(chars)
    return "".join(chars)


def _simple_password(length: int, profile: str) -> str:
    if profile == "letters_digits":
        alphabet = string.ascii_letters + string.digits
    elif profile == "digits":
        alphabet = string.digits
    else:
        raise AppException(message="密码模式无效", code=4001, status_code=400)
    return "".join(secrets.choice(alphabet) for _ in range(length))


def run(text: str = "", length: int = 12, profile: str = "strong", count: int = 1, **_: dict) -> str:
    _ = text
    if int(length) not in {8, 12, 16, 20, 32}:
        raise AppException(message="长度不在支持范围内", code=4001, status_code=400)
    if int(count) not in {1, 5, 10}:
        raise AppException(message="生成数量必须是 1、5 或 10", code=4001, status_code=400)

    result = []
    for _ in range(int(count)):
        if profile == "strong":
            result.append(_strong_password(int(length)))
        else:
            result.append(_simple_password(int(length), profile))
    return "\n".join(result)
