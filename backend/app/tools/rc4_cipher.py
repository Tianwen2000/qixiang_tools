from Crypto.Cipher import ARC4

from app.core.exceptions import AppException
from app.utils.crypto_utils import format_bytes, parse_bytes


TOOL_META = {
    "slug": "rc4-cipher",
    "name": "RC4 加密/解密",
    "category": "encode",
    "input_mode": "text",
    "result_type": "text",
}


def run(
    text: str,
    action: str = "encrypt",
    key_text: str = "",
    key_encoding: str = "utf8",
    output_encoding: str = "base64",
    **_: dict,
) -> str:
    key = parse_bytes(key_text, key_encoding, "key")
    if not key:
        raise AppException(message="RC4 密钥不能为空", code=4001, status_code=400)

    if action == "encrypt":
        cipher = ARC4.new(key)
        encrypted = cipher.encrypt(text.encode("utf-8"))
        return format_bytes(encrypted, output_encoding, "cipher")

    if action == "decrypt":
        cipher_bytes = parse_bytes(text, output_encoding, "cipher")
        cipher = ARC4.new(key)
        try:
            return cipher.decrypt(cipher_bytes).decode("utf-8")
        except Exception as exc:
            raise AppException(message=f"RC4 解密失败：{exc}", code=4001, status_code=400) from exc

    raise AppException(message="操作方式无效", code=4001, status_code=400)
