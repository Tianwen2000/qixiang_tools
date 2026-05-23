import json
from pathlib import Path

from app.core.exceptions import AppException
from app.schemas.meta import CategoryMeta, ToolMeta


CONFIG_DIR = Path(__file__).resolve().parents[1] / "configs"
CATEGORIES_PATH = CONFIG_DIR / "categories.json"
TOOLS_PATH = CONFIG_DIR / "tools.json"


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
    items = [item for item in load_tools() if item.enabled]
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
    return items


def get_tool_detail(slug: str) -> ToolMeta:
    for item in load_tools():
        if item.slug == slug and item.enabled:
            return item
    raise AppException(message="未找到该工具", code=4004, status_code=404)
