"""文件说明：提供健康检查接口。"""

from fastapi import APIRouter

from app.core.response import success_response


router = APIRouter()


@router.get("/health")
async def health() -> dict:
    return success_response({"status": "ok"})
