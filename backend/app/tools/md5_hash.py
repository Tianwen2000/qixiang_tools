import hashlib

from app.core.exceptions import AppException


TOOL_META = {
    "slug": "md5-hash",
    "name": "MD5 加密",
    "category": "encode",
    "input_mode": "text",
    "result_type": "text",
}


def run(text: str, digest_length: int = 32, digest_case: str = "lower", **_: dict) -> str:
    try:
        digest_length = int(digest_length)
    except (TypeError, ValueError) as exc:
        raise AppException(message="摘要长度必须是 16 或 32", code=4001, status_code=400) from exc

    if digest_length not in {16, 32}:
        raise AppException(message="摘要长度必须是 16 或 32", code=4001, status_code=400)
    if digest_case not in {"lower", "upper"}:
        raise AppException(message="输出大小写必须是 lower 或 upper", code=4001, status_code=400)

    digest = hashlib.md5(text.encode("utf-8")).hexdigest()
    if digest_length == 16:
        digest = digest[8:24]
    return digest.upper() if digest_case == "upper" else digest
