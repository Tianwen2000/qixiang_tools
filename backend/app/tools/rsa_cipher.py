"""文件说明：实现「RSA 加密/解密」工具的后端逻辑。"""

from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA

from app.core.exceptions import AppException
from app.utils.crypto_utils import format_bytes, parse_bytes


TOOL_META = {
    "slug": "rsa-cipher",
    "name": "RSA 加密/解密",
    "category": "encode",
    "input_mode": "text",
    "result_type": "text",
}


def _import_key(key_text: str) -> RSA.RsaKey:
    try:
        return RSA.import_key(key_text)
    except (ValueError, IndexError, TypeError) as exc:
        raise AppException(message="RSA 密钥文本无效", code=4001, status_code=400) from exc


def run(
    text: str,
    action: str = "encrypt",
    key_text: str = "",
    output_encoding: str = "base64",
    **_: dict,
) -> str:
    if not key_text.strip():
        raise AppException(message="请输入 RSA 密钥", code=4001, status_code=400)

    rsa_key = _import_key(key_text)

    if action == "encrypt":
        public_key = rsa_key.publickey() if rsa_key.has_private() else rsa_key
        cipher = PKCS1_OAEP.new(public_key)
        try:
            encrypted = cipher.encrypt(text.encode("utf-8"))
        except ValueError as exc:
            raise AppException(message=f"RSA 加密失败：{exc}", code=4001, status_code=400) from exc
        return format_bytes(encrypted, output_encoding, "cipher")

    if action == "decrypt":
        if not rsa_key.has_private():
            raise AppException(message="解密时必须提供 RSA 私钥", code=4001, status_code=400)
        cipher_bytes = parse_bytes(text, output_encoding, "cipher")
        cipher = PKCS1_OAEP.new(rsa_key)
        try:
            return cipher.decrypt(cipher_bytes).decode("utf-8")
        except Exception as exc:
            raise AppException(message=f"RSA 解密失败：{exc}", code=4001, status_code=400) from exc

    raise AppException(message="操作方式无效", code=4001, status_code=400)
