"""反馈接口。

提交对所有人开放（无需登录）；若携带有效会话 Cookie，则顺带记录提交者账号。
管理端查看接口待“root 管理员 + 反馈系统页”确定后再补。
"""

from fastapi import APIRouter, Request

from app.core.config import get_settings
from app.core.response import success_response
from app.schemas.feedback import FeedbackInput
from app.services import auth_service, feedback_service


router = APIRouter()


@router.post("/feedback")
async def submit_feedback(payload: FeedbackInput, request: Request) -> dict:
    token = request.cookies.get(get_settings().session_cookie_name)
    account = auth_service.peek_account(token)  # 未登录则为 None
    data = feedback_service.submit(payload.model_dump(), account=account)
    return success_response(data, message="反馈已提交，感谢你的反馈")
