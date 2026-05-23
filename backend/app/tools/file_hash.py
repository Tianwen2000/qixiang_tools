import hashlib
from pathlib import Path

from app.core.exceptions import AppException


TOOL_META = {
    "slug": "file-hash",
    "name": "文件 Hash 计算",
    "category": "utility",
    "input_mode": "file",
    "result_type": "text",
}


def run(input_path: str, output_dir: str, algorithm: str = "sha256", **_: dict) -> str:
    _ = output_dir
    supported = {"md5", "sha1", "sha256", "sha512"}
    if algorithm not in supported:
        raise AppException(message="不支持的哈希算法", code=4001, status_code=400)

    hasher = hashlib.new(algorithm)
    path = Path(input_path)
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()
