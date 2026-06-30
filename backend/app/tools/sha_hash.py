"""文件说明：实现「SHA 加密」工具的后端逻辑。"""

import hashlib

from app.core.exceptions import AppException


TOOL_META = {
    "slug": "sha-hash",
    "name": "SHA 加密",
    "category": "encode",
    "input_mode": "text",
    "result_type": "text",
}


ALGORITHMS = {"sha1", "sha224", "sha256", "sha384", "sha512"}


def run(text: str, algorithm: str = "sha256", digest_case: str = "lower", **_: dict) -> str:
    normalized_algorithm = algorithm.lower()
    if normalized_algorithm not in ALGORITHMS:
        raise AppException(message="不支持的 SHA 算法", code=4001, status_code=400)

    if digest_case not in {"lower", "upper"}:
        raise AppException(message="输出大小写必须是 lower 或 upper", code=4001, status_code=400)

    result = hashlib.new(normalized_algorithm, text.encode("utf-8")).hexdigest()
    return result.upper() if digest_case == "upper" else result
