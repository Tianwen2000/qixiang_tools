from Crypto.Hash import keccak

from app.core.exceptions import AppException


TOOL_META = {
    "slug": "keccak-hash",
    "name": "Keccak 加密",
    "category": "encode",
    "input_mode": "text",
    "result_type": "text",
}


def run(text: str, digest_bits: int = 256, digest_case: str = "lower", **_: dict) -> str:
    try:
        digest_bits = int(digest_bits)
    except (TypeError, ValueError) as exc:
        raise AppException(message="摘要位数必须是 224、256、384 或 512", code=4001, status_code=400) from exc

    if digest_bits not in {224, 256, 384, 512}:
        raise AppException(message="摘要位数必须是 224、256、384 或 512", code=4001, status_code=400)
    if digest_case not in {"lower", "upper"}:
        raise AppException(message="输出大小写必须是 lower 或 upper", code=4001, status_code=400)

    hasher = keccak.new(digest_bits=digest_bits)
    hasher.update(text.encode("utf-8"))
    result = hasher.hexdigest()
    return result.upper() if digest_case == "upper" else result
