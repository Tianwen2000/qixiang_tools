"""文件说明：实现「Nano ID 生成器」工具的后端逻辑。"""

import secrets
import string

from app.core.exceptions import AppException


TOOL_META = {
    "slug": "nanoid-generator",
    "name": "Nano ID 生成器",
    "category": "utility",
    "input_mode": "text",
    "result_type": "text",
}


ALPHABETS = {
    "default": string.ascii_letters + string.digits + "_-",
    "lowercase": string.ascii_lowercase + string.digits,
    "digits": string.digits,
    "hex": string.hexdigits.lower()[:16],
}


def _generate_id(length: int, alphabet: str) -> str:
    return "".join(secrets.choice(alphabet) for _ in range(length))


def run(text: str = "", length: int = 21, alphabet: str = "default", count: int = 1, **_: dict) -> str:
    _ = text
    if alphabet not in ALPHABETS:
        raise AppException(message="字符集预设无效", code=4001, status_code=400)
    if int(length) not in {8, 12, 16, 21, 32}:
        raise AppException(message="长度不在支持范围内", code=4001, status_code=400)
    if int(count) not in {1, 5, 10}:
        raise AppException(message="生成数量必须是 1、5 或 10", code=4001, status_code=400)
    charset = ALPHABETS[alphabet]
    return "\n".join(_generate_id(int(length), charset) for _ in range(int(count)))
