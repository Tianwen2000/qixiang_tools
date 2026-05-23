from Crypto.Random import get_random_bytes
from gmssl import sm4

from app.core.exceptions import AppException
from app.utils.crypto_utils import format_bytes, parse_bytes


TOOL_META = {
    "slug": "sm4-cipher",
    "name": "国密 SM4 加密/解密",
    "category": "encode",
    "input_mode": "text",
    "result_type": "text",
}


def _parse_cipher_payload(text: str, encoding: str) -> tuple[bytes, bytes]:
    parts = [item.strip() for item in text.strip().split(":") if item.strip()]
    if len(parts) != 2:
        raise AppException(message="密文格式必须是 iv:data", code=4001, status_code=400)
    iv = parse_bytes(parts[0], encoding, "iv")
    cipher_bytes = parse_bytes(parts[1], encoding, "cipher")
    return iv, cipher_bytes


def run(
    text: str,
    action: str = "encrypt",
    key_text: str = "",
    key_encoding: str = "utf8",
    output_encoding: str = "base64",
    **_: dict,
) -> str:
    key = parse_bytes(key_text, key_encoding, "key")
    if len(key) != 16:
        raise AppException(message="SM4 密钥长度必须正好是 16 字节", code=4001, status_code=400)

    cipher = sm4.CryptSM4()

    if action == "encrypt":
        iv = get_random_bytes(16)
        cipher.set_key(key, sm4.SM4_ENCRYPT)
        encrypted = cipher.crypt_cbc(iv, text.encode("utf-8"))
        return f"{format_bytes(iv, output_encoding, 'iv')}:{format_bytes(encrypted, output_encoding, 'cipher')}"

    if action == "decrypt":
        iv, cipher_bytes = _parse_cipher_payload(text, output_encoding)
        if len(iv) != 16:
            raise AppException(message="SM4 的 IV 长度必须是 16 字节", code=4001, status_code=400)
        try:
            cipher.set_key(key, sm4.SM4_DECRYPT)
            return cipher.crypt_cbc(iv, cipher_bytes).decode("utf-8")
        except Exception as exc:
            raise AppException(message=f"SM4 解密失败：{exc}", code=4001, status_code=400) from exc

    raise AppException(message="操作方式无效", code=4001, status_code=400)
