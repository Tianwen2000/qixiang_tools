import json
from pathlib import Path

from app.core.exceptions import AppException
from app.schemas.meta import CategoryMeta, ToolMeta


CONFIG_DIR = Path(__file__).resolve().parents[1] / "configs"
CATEGORIES_PATH = CONFIG_DIR / "categories.json"
TOOLS_PATH = CONFIG_DIR / "tools.json"

FORMAT_TOOL_ORDER = {
    "png-jpg-ico-converter": 1,
    "png-jpg-icns-converter": 2,
    "animated-frames-converter": 3,
    "svg-animation-converter": 4,
    "mp3-flac-converter": 5,
    "mp3-mp4-converter": 6,
    "gif-mp4-converter": 7,
    "mov-mp4-converter": 8,
    "wav-mp3-converter": 9,
    "ppt-html-converter": 10,
    "word-pdf-converter": 11,
    "image-format-converter": 12,
}


def _format_tool_sort_key(item: ToolMeta) -> tuple[int, int, str]:
    order = FORMAT_TOOL_ORDER.get(item.slug)
    if order is not None:
        return (0, order, item.slug)
    return (1, 0, item.slug)


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
    if category == "format":
        items = sorted(items, key=_format_tool_sort_key)
    elif category is None:
        format_items = [item for item in items if item.category == "format"]
        ordered_format_items = sorted(format_items, key=_format_tool_sort_key)
        format_iter = iter(ordered_format_items)
        items = [next(format_iter) if item.category == "format" else item for item in items]
    return items


def get_tool_detail(slug: str) -> ToolMeta:
    for item in load_tools():
        if item.slug == slug and item.enabled:
            return item
    raise AppException(message="未找到该工具", code=4004, status_code=404)
