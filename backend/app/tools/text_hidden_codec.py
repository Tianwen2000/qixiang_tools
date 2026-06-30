"""文件说明：实现「文字隐蔽加密/解密」工具的后端逻辑。"""

from app.core.exceptions import AppException


TOOL_META = {
    "slug": "text-hidden-codec",
    "name": "文字隐蔽加密/解密",
    "category": "encode",
    "input_mode": "text",
    "result_type": "text",
}


ZERO = "\u200b"
ONE = "\u200c"
START = "\u2060"
END = "\u2063"


def _text_to_hidden(value: str) -> str:
    bits = "".join(format(byte, "08b") for byte in value.encode("utf-8"))
    return START + "".join(ONE if bit == "1" else ZERO for bit in bits) + END


def _hidden_to_text(value: str) -> str:
    if START in value and END in value:
        start_index = value.index(START) + 1
        end_index = value.index(END, start_index)
        hidden = value[start_index:end_index]
    else:
        hidden = "".join(char for char in value if char in {ZERO, ONE})

    if not hidden:
        raise AppException(message="未找到隐藏内容", code=4001, status_code=400)

    bits = "".join("1" if char == ONE else "0" for char in hidden)
    if len(bits) % 8 != 0:
        raise AppException(message="隐藏内容已损坏", code=4001, status_code=400)

    try:
        decoded = bytes(int(bits[index : index + 8], 2) for index in range(0, len(bits), 8)).decode("utf-8")
    except Exception as exc:
        raise AppException(message="隐藏内容解码失败", code=4001, status_code=400) from exc
    return decoded


def run(text: str, action: str = "hide", cover_text: str = "", **_: dict) -> str:
    if action == "hide":
        if not text:
            raise AppException(message="请输入要隐藏的文本", code=4001, status_code=400)
        return f"{cover_text}{_text_to_hidden(text)}"

    if action == "reveal":
        return _hidden_to_text(text)

    raise AppException(message="操作方式无效", code=4001, status_code=400)
