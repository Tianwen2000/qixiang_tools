import re

from app.core.exceptions import AppException


TOOL_META = {
    "slug": "regex-replacer",
    "name": "正则替换字符串",
    "category": "text",
    "input_mode": "text",
    "result_type": "text",
}


FLAG_MAP = {
    "i": re.IGNORECASE,
    "m": re.MULTILINE,
    "s": re.DOTALL,
}


def _parse_flags(value: str) -> int:
    flags = 0
    for item in value.replace(" ", "").lower():
        if not item:
            continue
        if item not in FLAG_MAP:
            raise AppException(message=f"不支持的正则标记：{item}", code=4001, status_code=400)
        flags |= FLAG_MAP[item]
    return flags


def run(
    text: str,
    pattern: str = "",
    replacement: str = "",
    flags: str = "",
    count: int = 0,
    **_: dict,
) -> str:
    if not pattern:
        raise AppException(message="请先输入正则表达式", code=4001, status_code=400)
    if count < 0:
        raise AppException(message="替换次数不能小于 0", code=4001, status_code=400)

    try:
        compiled = re.compile(pattern, _parse_flags(flags))
    except re.error as exc:
        raise AppException(message=f"正则表达式无效：{exc.msg}", code=4001, status_code=400) from exc

    return compiled.sub(replacement, text, count=count)
