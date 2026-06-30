"""文件说明：实现「正则表达式测试」工具的后端逻辑。"""

import json
import re

from app.core.exceptions import AppException


TOOL_META = {
    "slug": "regex-tester",
    "name": "正则表达式测试",
    "category": "dev",
    "input_mode": "text",
    "result_type": "text",
}


FLAG_MAP = {
    "i": re.IGNORECASE,
    "m": re.MULTILINE,
    "s": re.DOTALL,
}


def _build_flags(raw_flags: str) -> int:
    flags = 0
    for item in raw_flags.lower():
        if not item:
            continue
        if item not in FLAG_MAP:
            raise AppException(message=f"不支持的正则标记：{item}", code=4001, status_code=400)
        flags |= FLAG_MAP[item]
    return flags


def run(text: str, pattern: str = "", flags: str = "", **_: dict) -> str:
    if not pattern:
        raise AppException(message="请输入正则表达式", code=4001, status_code=400)
    try:
        compiled = re.compile(pattern, _build_flags(flags))
    except re.error as exc:
        raise AppException(message=f"正则表达式无效：{exc}", code=4001, status_code=400) from exc

    matches = []
    for matched in compiled.finditer(text):
        matches.append(
            {
                "match": matched.group(0),
                "start": matched.start(),
                "end": matched.end(),
                "groups": list(matched.groups()),
            }
        )

    result = {
        "pattern": pattern,
        "flags": flags,
        "matched": bool(matches),
        "match_count": len(matches),
        "matches": matches,
    }
    return json.dumps(result, ensure_ascii=False, indent=2)
