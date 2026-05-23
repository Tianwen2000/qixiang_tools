from functools import lru_cache

from hanzipy.dictionary import HanziDictionary

from app.core.exceptions import AppException


TOOL_META = {
    "slug": "word-group-builder",
    "name": "在线组词",
    "category": "text",
    "input_mode": "text",
    "result_type": "text",
}


LEVEL_MAP = {
    "high": ["high_frequency"],
    "common": ["high_frequency", "mid_frequency"],
    "all": ["high_frequency", "mid_frequency", "low_frequency"],
}


@lru_cache
def _get_dictionary() -> HanziDictionary:
    return HanziDictionary()


def _first_character(text: str) -> str:
    for char in text:
        if not char.isspace():
            return char
    return ""


def run(text: str, level: str = "common", limit: int = 10, **_: dict) -> str:
    if level not in LEVEL_MAP:
        raise AppException(message="组词范围不支持", code=4001, status_code=400)
    if limit not in {5, 10, 20}:
        raise AppException(message="结果数量只能是 5、10 或 20", code=4001, status_code=400)

    character = _first_character(text)
    if not character:
        raise AppException(message="请输入一个汉字", code=4001, status_code=400)

    examples = _get_dictionary().get_examples(character)
    results: list[str] = []
    seen: set[str] = set()
    for bucket in LEVEL_MAP[level]:
        for item in examples.get(bucket, []):
            word = item.get("simplified", "").strip()
            if not word or word in seen:
                continue
            seen.add(word)
            pinyin = item.get("pinyin", "").strip()
            definition = item.get("definition", "").strip()
            if definition:
                results.append(f"{word}  {pinyin}  {definition}")
            else:
                results.append(f"{word}  {pinyin}".rstrip())
            if len(results) >= limit:
                return "\n".join(results)

    if not results:
        return "未找到可用组词结果"
    return "\n".join(results)
