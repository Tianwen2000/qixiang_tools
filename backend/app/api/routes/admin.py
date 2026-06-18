"""管理员只读查看接口。

仅 root 管理员（账号在 ADMIN_ACCOUNTS 中）登录后可访问，用于查看反馈与账号活动日志。
未登录 → 401；已登录但非管理员 → 403。
"""

from fastapi import APIRouter, Request

from app.core.config import get_settings
from app.core.exceptions import AppException
from app.core.response import success_response
from app.services import activity_service, auth_service, feedback_service


router = APIRouter()


def _require_admin(request: Request) -> dict:
    token = request.cookies.get(get_settings().session_cookie_name)
    user = auth_service.resolve_session(token)  # 未登录/失效 → 401
    if not user.get("is_admin"):
        raise AppException(message="需要管理员权限", code=4030, status_code=403)
    return user


@router.get("/admin/feedback")
async def admin_feedback(request: Request) -> dict:
    _require_admin(request)
    return success_response({"items": feedback_service.recent(limit=500)})


@router.get("/admin/logs")
async def admin_logs(request: Request) -> dict:
    _require_admin(request)
    return success_response({"items": activity_service.recent(limit=500)})
