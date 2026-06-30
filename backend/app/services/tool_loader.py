"""文件说明：加载工具分类和工具元信息，并按配置处理展示顺序。"""

import json
from pathlib import Path

from app.core.exceptions import AppException
from app.schemas.meta import CategoryMeta, ToolMeta


CONFIG_DIR = Path(__file__).resolve().parents[1] / "configs"
CATEGORIES_PATH = CONFIG_DIR / "categories.json"
TOOLS_PATH = CONFIG_DIR / "tools.json"

# 按大类配置工具展示顺序。
# 把已经在 tools.json 注册过的工具 slug 写到对应大类里，就会优先排在该大类前面。
# 没写进这里的工具仍然正常可用，并会按 tools.json 原顺序排在已固定工具后面。
CATEGORY_TOOL_ORDER = {
    "dev": (),
    "ops": (
        "text-format-cleaner",
        "invisible-control-chars",
        "character-count-slice",
        "free-translate",
        "local-ip-lookup",
    ),
    "format": (
        "png-jpg-ico-converter",
        "png-jpg-icns-converter",
        "animated-frames-converter",
        "svg-animation-converter",
        "mp3-flac-converter",
        "mp3-mp4-converter",
        "gif-mp4-converter",
        "mov-mp4-converter",
        "wav-mp3-converter",
        "ppt-html-converter",
        "word-pdf-converter",
        "image-format-converter",
    ),
    "text": (),
    "encode": (),
    "image": (),
    "chart": (),
    "time": (),
    "game": (),
    "other": (),
}

CATEGORY_TOOL_ORDER_INDEX = {
    category: {slug: index for index, slug in enumerate(slugs)}
    for category, slugs in CATEGORY_TOOL_ORDER.items()
}


def _sort_tools_by_category_order(items: list[ToolMeta], category: str) -> list[ToolMeta]:
    order_index = CATEGORY_TOOL_ORDER_INDEX.get(category, {})
    if not order_index:
        return items

    indexed_items = list(enumerate(items))
    sorted_items = sorted(
        indexed_items,
        key=lambda pair: (
            0,
            order_index[pair[1].slug],
            pair[0],
        )
        if pair[1].slug in order_index
        else (
            1,
            pair[0],
            pair[0],
        ),
    )
    return [item for _, item in sorted_items]


def _sort_all_tools_by_category_order(items: list[ToolMeta]) -> list[ToolMeta]:
    category_iters = {
        category: iter(_sort_tools_by_category_order([item for item in items if item.category == category], category))
        for category, order_index in CATEGORY_TOOL_ORDER_INDEX.items()
        if order_index
    }
    if not category_iters:
        return items
    return [next(category_iters[item.category]) if item.category in category_iters else item for item in items]


def _load_json(path: Path) -> list[dict]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise AppException(message=f"配置文件不存在：{path.name}", code=5003, status_code=500) from exc
    except json.JSONDecodeError as exc:
        raise AppException(message=f"配置 JSON 格式无效：{path.name}", code=5003, status_code=500) from exc


def load_categories() -> list[CategoryMeta]:
    return [CategoryMeta.model_validate(item) for item in _load_json(CATEGORIES_PATH)]


def load_tools() -> list[ToolMeta]:
    return [ToolMeta.model_validate(item) for item in _load_json(TOOLS_PATH)]


def list_categories() -> list[CategoryMeta]:
    return sorted((item for item in load_categories() if item.enabled), key=lambda item: item.sort_order, reverse=True)


def list_tools(category: str | None = None, keyword: str | None = None) -> list[ToolMeta]:
    items = [item for item in load_tools() if item.enabled and item.visible]
    if category:
        items = [item for item in items if item.category == category]
    if keyword:
        needle = keyword.strip().lower()
        items = [
            item
            for item in items
            if needle in item.name.lower()
            or needle in item.slug.lower()
            or needle in item.summary.lower()
            or needle in item.description.lower()
        ]
    if category:
        items = _sort_tools_by_category_order(items, category)
    elif category is None:
        items = _sort_all_tools_by_category_order(items)
    return items


def get_tool_detail(slug: str) -> ToolMeta:
    for item in load_tools():
        if item.slug == slug and item.enabled:
            return item
    raise AppException(message="未找到该工具", code=4004, status_code=404)
