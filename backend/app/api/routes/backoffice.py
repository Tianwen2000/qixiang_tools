"""文件说明：提供独立后台入口验证、登录、反馈和账号活动日志接口。"""

"""独立后台管理系统接口。

这组接口使用后台专用 Cookie，不复用 AI 登录态，也不依赖旧的 AI 管理员配置。
"""

from fastapi import APIRouter, Request, Response

from app.core.config import get_settings
from app.core.response import success_response
from app.schemas.backoffice import BackofficeEntryInput, BackofficeLoginInput, BackofficeTicketInput
from app.services import activity_service, backoffice_service, feedback_service


router = APIRouter()
BACKOFFICE_ROUTE_PREFIX = "/qx-backoffice"


def _read_cookie(request: Request) -> str | None:
    return request.cookies.get(get_settings().backoffice_cookie_name)


def _set_cookie(response: Response, token: str) -> None:
    settings = get_settings()
    response.set_cookie(
        key=settings.backoffice_cookie_name,
        value=token,
        max_age=backoffice_service.cookie_max_age(),
        httponly=True,
        samesite="lax",
        secure=settings.session_cookie_secure,
        path="/",
    )


def _clear_cookie(response: Response) -> None:
    response.delete_cookie(key=get_settings().backoffice_cookie_name, path="/")


def _require_backoffice(request: Request) -> dict:
    return backoffice_service.resolve_session(_read_cookie(request))


@router.get("/backoffice/challenge")
async def backoffice_challenge() -> dict:
    return success_response({"question": backoffice_service.challenge_question()})


@router.post("/backoffice/entry")
async def backoffice_entry(payload: BackofficeEntryInput) -> dict:
    ticket = backoffice_service.create_entry_ticket(payload.answer)
    return success_response({"path": f"{BACKOFFICE_ROUTE_PREFIX}/{ticket}"})


@router.post("/backoffice/entry/consume")
async def backoffice_entry_consume(payload: BackofficeTicketInput) -> dict:
    backoffice_service.consume_entry_ticket(payload.ticket)
    return success_response(message="入口验证通过")


@router.post("/backoffice/login")
async def backoffice_login(payload: BackofficeLoginInput, response: Response) -> dict:
    data = backoffice_service.login(payload.account, payload.password)
    _set_cookie(response, data["token"])
    return success_response({"user": data["user"]}, message="后台登录成功")


@router.get("/backoffice/me")
async def backoffice_me(request: Request) -> dict:
    return success_response({"user": _require_backoffice(request)})


@router.post("/backoffice/logout")
async def backoffice_logout(request: Request, response: Response) -> dict:
    backoffice_service.destroy_session(_read_cookie(request))
    _clear_cookie(response)
    return success_response(message="已退出后台")


@router.get("/backoffice/feedback")
async def backoffice_feedback(request: Request) -> dict:
    _require_backoffice(request)
    return success_response({"items": feedback_service.recent(limit=500)})


@router.get("/backoffice/logs")
async def backoffice_logs(request: Request) -> dict:
    user = _require_backoffice(request)
    backoffice_service.require_admin(user)
    return success_response({"items": activity_service.recent(limit=500)})
