"""文件说明：实现「Shake 加密」工具的后端逻辑。"""

import hashlib

from app.core.exceptions import AppException


TOOL_META = {
    "slug": "shake-hash",
    "name": "Shake 加密",
    "category": "encode",
    "input_mode": "text",
    "result_type": "text",
}


def run(text: str, algorithm: str = "shake_128", digest_bytes: int = 16, **_: dict) -> str:
    try:
        digest_bytes = int(digest_bytes)
    except (TypeError, ValueError) as exc:
        raise AppException(message="摘要字节数必须是整数", code=4001, status_code=400) from exc

    if digest_bytes <= 0 or digest_bytes > 128:
        raise AppException(message="摘要字节数必须在 1 到 128 之间", code=4001, status_code=400)

    if algorithm == "shake_128":
        hasher = hashlib.shake_128(text.encode("utf-8"))
    elif algorithm == "shake_256":
        hasher = hashlib.shake_256(text.encode("utf-8"))
    else:
        raise AppException(message="算法必须是 shake_128 或 shake_256", code=4001, status_code=400)

    return hasher.hexdigest(digest_bytes)
