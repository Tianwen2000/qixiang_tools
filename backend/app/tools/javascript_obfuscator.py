import base64

from rjsmin import jsmin

from app.core.exceptions import AppException


TOOL_META = {
    "slug": "javascript-obfuscator",
    "name": "Javascript 混淆加密",
    "category": "encode",
    "input_mode": "text",
    "result_type": "text",
}


def _base64_wrapper(script: str) -> str:
    payload = base64.b64encode(script.encode("utf-8")).decode("ascii")
    return f"(function(){{const s=atob('{payload}');(0,eval)(s);}})();"


def _charcode_wrapper(script: str) -> str:
    char_codes = ",".join(str(ord(char)) for char in script)
    return f"eval(String.fromCharCode({char_codes}));"


def run(text: str, mode: str = "base64_wrapper", minify_first: bool = True, **_: dict) -> str:
    if not text.strip():
        raise AppException(message="请输入 Javascript 代码", code=4001, status_code=400)

    script = jsmin(text) if minify_first else text

    if mode == "base64_wrapper":
        return _base64_wrapper(script)
    if mode == "charcode_wrapper":
        return _charcode_wrapper(script)

    raise AppException(message="混淆模式必须是 base64_wrapper 或 charcode_wrapper", code=4001, status_code=400)
