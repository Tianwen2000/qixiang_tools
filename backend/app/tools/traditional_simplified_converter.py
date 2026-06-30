"""文件说明：实现「简繁体转换」工具的后端逻辑。"""

from functools import lru_cache

from opencc import OpenCC

from app.core.exceptions import AppException


TOOL_META = {
    "slug": "traditional-simplified-converter",
    "name": "简繁体转换",
    "category": "text",
    "input_mode": "text",
    "result_type": "text",
}


ACTION_MAP = {
    "simplified_to_traditional": "s2t",
    "traditional_to_simplified": "t2s",
}


@lru_cache
def _get_converter(config: str) -> OpenCC:
    return OpenCC(config)


def run(text: str, action: str = "simplified_to_traditional", **_: dict) -> str:
    if action not in ACTION_MAP:
        raise AppException(message="不支持的转换方式", code=4001, status_code=400)
    return _get_converter(ACTION_MAP[action]).convert(text)
