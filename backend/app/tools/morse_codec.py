from app.core.exceptions import AppException


TOOL_META = {
    "slug": "morse-codec",
    "name": "摩斯密码加密/解密",
    "category": "encode",
    "input_mode": "text",
    "result_type": "text",
}


MORSE_MAP = {
    "A": ".-",
    "B": "-...",
    "C": "-.-.",
    "D": "-..",
    "E": ".",
    "F": "..-.",
    "G": "--.",
    "H": "....",
    "I": "..",
    "J": ".---",
    "K": "-.-",
    "L": ".-..",
    "M": "--",
    "N": "-.",
    "O": "---",
    "P": ".--.",
    "Q": "--.-",
    "R": ".-.",
    "S": "...",
    "T": "-",
    "U": "..-",
    "V": "...-",
    "W": ".--",
    "X": "-..-",
    "Y": "-.--",
    "Z": "--..",
    "0": "-----",
    "1": ".----",
    "2": "..---",
    "3": "...--",
    "4": "....-",
    "5": ".....",
    "6": "-....",
    "7": "--...",
    "8": "---..",
    "9": "----.",
    ".": ".-.-.-",
    ",": "--..--",
    "?": "..--..",
    "!": "-.-.--",
    "-": "-....-",
    "/": "-..-.",
    "@": ".--.-.",
    "(": "-.--.",
    ")": "-.--.-",
}

REVERSE_MORSE_MAP = {value: key for key, value in MORSE_MAP.items()}


def _encode(text: str) -> str:
    tokens: list[str] = []
    for char in text.upper():
        if char.isspace():
            tokens.append("/")
            continue
        if char not in MORSE_MAP:
            raise AppException(message=f"摩斯密码不支持该字符：{char}", code=4001, status_code=400)
        tokens.append(MORSE_MAP[char])
    return " ".join(tokens)


def _decode(text: str) -> str:
    result: list[str] = []
    for token in text.strip().split():
        if token == "/":
            result.append(" ")
            continue
        if token not in REVERSE_MORSE_MAP:
            raise AppException(message=f"无效的摩斯密码片段：{token}", code=4001, status_code=400)
        result.append(REVERSE_MORSE_MAP[token])
    return "".join(result)


def run(text: str, action: str = "encode", **_: dict) -> str:
    if action == "encode":
        return _encode(text)
    if action == "decode":
        return _decode(text)
    raise AppException(message="操作方式无效", code=4001, status_code=400)
