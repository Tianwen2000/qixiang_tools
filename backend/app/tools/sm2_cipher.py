"""文件说明：实现「国密 SM2 加密/解密」工具的后端逻辑。"""

from gmssl import func, sm2

from app.core.exceptions import AppException
from app.utils.crypto_utils import format_bytes, parse_bytes


TOOL_META = {
    "slug": "sm2-cipher",
    "name": "国密 SM2 加密/解密",
    "category": "encode",
    "input_mode": "text",
    "result_type": "text",
}


def _build_sm2(private_key: str, public_key: str) -> sm2.CryptSM2:
    return sm2.CryptSM2(private_key=private_key, public_key=public_key, mode=1)


def _generate_keypair() -> str:
    temp = _build_sm2(private_key="1", public_key="")
    private_key = func.random_hex(temp.para_len)
    public_key = temp._kg(int(private_key, 16), temp.ecc_table["g"])
    return (
        "私钥:\n"
        f"{private_key}\n\n"
        "公钥:\n"
        f"{public_key}"
    )


def run(
    text: str,
    action: str = "encrypt",
    public_key: str = "",
    private_key: str = "",
    output_encoding: str = "base64",
    **_: dict,
) -> str:
    if action == "generate_keypair":
        return _generate_keypair()

    if action == "encrypt":
        if not public_key.strip():
            raise AppException(message="加密时必须提供 SM2 公钥", code=4001, status_code=400)
        cipher = _build_sm2(private_key="1", public_key=public_key.strip())
        encrypted = cipher.encrypt(text.encode("utf-8"))
        return format_bytes(encrypted, output_encoding, "cipher")

    if action == "decrypt":
        if not private_key.strip():
            raise AppException(message="解密时必须提供 SM2 私钥", code=4001, status_code=400)
        if not public_key.strip():
            raise AppException(message="解密时必须提供 SM2 公钥", code=4001, status_code=400)
        cipher_bytes = parse_bytes(text, output_encoding, "cipher")
        cipher = _build_sm2(private_key=private_key.strip(), public_key=public_key.strip())
        try:
            return cipher.decrypt(cipher_bytes).decode("utf-8")
        except Exception as exc:
            raise AppException(message=f"SM2 解密失败：{exc}", code=4001, status_code=400) from exc

    raise AppException(message="操作方式无效", code=4001, status_code=400)
