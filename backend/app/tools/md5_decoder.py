import hashlib
import json

from app.core.exceptions import AppException


TOOL_META = {
    "slug": "md5-decoder",
    "name": "MD5 解密",
    "category": "encode",
    "input_mode": "text",
    "result_type": "text",
}


COMMON_CANDIDATES = [
    "123456",
    "123456789",
    "12345678",
    "123123",
    "000000",
    "111111",
    "654321",
    "qwerty",
    "qwerty123",
    "password",
    "admin",
    "admin123",
    "root",
    "root123",
    "test",
    "test123",
    "guest",
    "welcome",
    "abc123",
    "hello",
    "hello123",
    "letmein",
    "iloveyou",
    "888888",
    "666666",
    "1q2w3e4r",
    "sunshine",
    "dragon",
    "monkey",
    "football",
]


def _normalize_bool(value: bool | str) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "on"}
    return bool(value)


def _md5_variants(candidate: str) -> tuple[str, str]:
    digest = hashlib.md5(candidate.encode("utf-8")).hexdigest()
    return digest, digest[8:24]


def _build_hash(text: str, digest_length: int = 32, digest_case: str = "lower") -> str:
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


def _match_hashes(text: str, custom_candidates: str = "", include_common: bool = True) -> str:
    hashes = [item.strip().lower() for item in text.splitlines() if item.strip()]
    if not hashes:
        raise AppException(message="请输入要尝试匹配的 MD5 文本", code=4001, status_code=400)

    candidates: list[str] = []
    if include_common:
        candidates.extend(COMMON_CANDIDATES)
    if custom_candidates.strip():
        candidates.extend(item.strip() for item in custom_candidates.splitlines() if item.strip())

    if not candidates:
        raise AppException(message="至少需要一组候选词", code=4001, status_code=400)

    found: dict[str, str] = {}
    normalized_targets = set(hashes)
    for candidate in dict.fromkeys(candidates):
        full_md5, short_md5 = _md5_variants(candidate)
        if full_md5 in normalized_targets and full_md5 not in found:
            found[full_md5] = candidate
        if short_md5 in normalized_targets and short_md5 not in found:
            found[short_md5] = candidate

    payload = {
        "matched_count": len(found),
        "total_hashes": len(hashes),
        "matched": [{"hash": target, "plain": found[target]} for target in hashes if target in found],
        "unmatched": [target for target in hashes if target not in found],
        "note": "当前为候选词匹配模式，不保证能还原所有 MD5。",
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)


def run(
    text: str,
    action: str = "decode",
    custom_candidates: str = "",
    include_common: bool = True,
    digest_length: int = 32,
    digest_case: str = "lower",
    **_: dict,
) -> str:
    if action == "hash":
        return _build_hash(text=text, digest_length=digest_length, digest_case=digest_case)
    if action == "decode":
        return _match_hashes(
            text=text,
            custom_candidates=custom_candidates,
            include_common=_normalize_bool(include_common),
        )
    raise AppException(message="操作方式无效", code=4001, status_code=400)
