"""文件说明：提供工具分类和工具元信息接口。"""

from fastapi import APIRouter, Query

from app.core.response import success_response
from app.schemas.meta import ToolMetaOut
from app.services.tool_loader import get_tool_detail, list_categories, list_tools


router = APIRouter()


@router.get("/categories")
async def get_categories() -> dict:
    items = [item.model_dump() for item in list_categories()]
    return success_response(items)


@router.get("/tools")
async def get_tools(
    category: str | None = Query(default=None),
    keyword: str | None = Query(default=None),
) -> dict:
    items = [ToolMetaOut.model_validate(item.model_dump()).model_dump() for item in list_tools(category=category, keyword=keyword)]
    return success_response(items)


@router.get("/tools/{slug}")
async def get_tool(slug: str) -> dict:
    item = ToolMetaOut.model_validate(get_tool_detail(slug).model_dump())
    return success_response(item.model_dump())
