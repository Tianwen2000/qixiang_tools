"""文件说明：提供日期、农历和时间卡片相关接口。"""

from fastapi import APIRouter

from app.core.response import success_response
from app.services.time_service import build_beijing_time_snapshot


router = APIRouter()


@router.get("/time/beijing")
async def get_beijing_time() -> dict:
    return success_response(build_beijing_time_snapshot().model_dump())
