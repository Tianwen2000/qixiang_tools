from app.core.exceptions import AppException


TOOL_META = {
    "slug": "hex-string-codec",
    "name": "16进制转字符串",
    "category": "encode",
    "input_mode": "text",
    "result_type": "text",
}


def run(text: str, action: str = "hex_to_text", **_: dict) -> str:
    if action == "text_to_hex":
        return text.encode("utf-8").hex()

    if action == "hex_to_text":
        normalized = "".join(text.split())
        try:
            return bytes.fromhex(normalized).decode("utf-8")
        except Exception as exc:
            raise AppException(message="Hex 文本无效", code=4001, status_code=400) from exc

    raise AppException(message="操作方式无效", code=4001, status_code=400)
