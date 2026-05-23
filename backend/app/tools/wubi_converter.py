from pywubi import conbin_wubi, single_wubi, wubi

from app.core.exceptions import AppException


TOOL_META = {
    "slug": "wubi-converter",
    "name": "汉字转五笔码",
    "category": "text",
    "input_mode": "text",
    "result_type": "text",
}


def _convert_single(text: str) -> str:
    rows: list[str] = []
    for char in text:
        if char.isspace():
            continue
        code = single_wubi(char)
        rows.append(f"{char}：{code}")
    return "\n".join(rows)


def run(text: str, mode: str = "single", **_: dict) -> str:
    content = "".join(text.split())
    if not content:
        raise AppException(message="请输入要转换的汉字内容", code=4001, status_code=400)

    try:
        if mode == "single":
            return _convert_single(content)
        if mode == "phrase":
            return conbin_wubi(content)
        if mode == "both":
            single_lines = _convert_single(content)
            phrase_code = conbin_wubi(content)
            return f"逐字编码：\n{single_lines}\n\n词组编码：\n{phrase_code}"
    except Exception as exc:
        raise AppException(message=f"五笔转换失败：{exc}", code=4001, status_code=400) from exc

    raise AppException(message="不支持的五笔输出方式", code=4001, status_code=400)
