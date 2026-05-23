import base64

from app.core.exceptions import AppException


LABEL_MAP = {
    "key": "密钥",
    "iv": "IV",
    "cipher": "密文",
}


def _display_label(label: str) -> str:
    return LABEL_MAP.get(label, label)


def parse_bytes(value: str, encoding: str, label: str) -> bytes:
    display_label = _display_label(label)
    if encoding == "utf8":
        return value.encode("utf-8")
    if encoding == "hex":
        try:
            return bytes.fromhex("".join(value.split()))
        except ValueError as exc:
            raise AppException(message=f"{display_label} 的 Hex 文本无效", code=4001, status_code=400) from exc
    if encoding == "base64":
        try:
            return base64.b64decode(value.encode("utf-8"), validate=True)
        except Exception as exc:
            raise AppException(message=f"{display_label} 的 Base64 文本无效", code=4001, status_code=400) from exc
    raise AppException(message=f"不支持的{display_label}编码格式", code=4001, status_code=400)


def format_bytes(value: bytes, encoding: str, label: str) -> str:
    display_label = _display_label(label)
    if encoding == "hex":
        return value.hex()
    if encoding == "base64":
        return base64.b64encode(value).decode("utf-8")
    if encoding == "utf8":
        try:
            return value.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise AppException(message=f"{display_label} 不是有效的 UTF-8 文本", code=4001, status_code=400) from exc
    raise AppException(message=f"不支持的{display_label}编码格式", code=4001, status_code=400)
