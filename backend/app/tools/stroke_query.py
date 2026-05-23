from functools import lru_cache

from cnradical import Radical, RunOption
from strokes.strokes import strokes

from app.core.exceptions import AppException


TOOL_META = {
    "slug": "stroke-query",
    "name": "汉字笔画查询",
    "category": "text",
    "input_mode": "text",
    "result_type": "text",
}


@lru_cache
def _radical_helper() -> Radical:
    return Radical(RunOption.Radical)


@lru_cache
def _pinyin_helper() -> Radical:
    return Radical(RunOption.Pinyin)


def run(text: str, **_: dict) -> str:
    content = "".join(text.split())
    if not content:
        raise AppException(message="请输入要查询的汉字", code=4001, status_code=400)

    stroke_values = strokes(content)
    if isinstance(stroke_values, int):
        stroke_values = [stroke_values]

    rows: list[str] = []
    radical_helper = _radical_helper()
    pinyin_helper = _pinyin_helper()

    for char, count in zip(content, stroke_values):
        radical = radical_helper.trans_ch(char) or "-"
        pinyin = pinyin_helper.trans_ch(char) or "-"
        if count <= 0:
            rows.append(f"{char}：暂未收录笔画数据")
            continue
        rows.append(f"{char}：{count} 画，部首 {radical}，拼音 {pinyin}")
    return "\n".join(rows)
