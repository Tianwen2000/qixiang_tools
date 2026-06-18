from fastapi import APIRouter, Request, Response

from app.core.config import get_settings
from app.core.response import success_response
from app.schemas.auth import AuthInput
from app.services import activity_service, auth_service


router = APIRouter()


def _read_session_cookie(request: Request) -> str | None:
    return request.cookies.get(get_settings().session_cookie_name)


def _client_ip(request: Request) -> str:
    # nginx 反代时优先看 X-Forwarded-For 的第一段。
    forwarded = request.headers.get("x-forwarded-for", "")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else ""


def _user_agent(request: Request) -> str:
    return request.headers.get("user-agent", "")


def _set_session_cookie(response: Response, token: str) -> None:
    settings = get_settings()
    response.set_cookie(
        key=settings.session_cookie_name,
        value=token,
        max_age=auth_service.cookie_max_age(),  # 30 天
        httponly=True,  # 前端 JS 读不到，降低 XSS 盗取风险
        samesite="lax",
        secure=settings.session_cookie_secure,
        path="/",
    )


def _clear_session_cookie(response: Response) -> None:
    response.delete_cookie(key=get_settings().session_cookie_name, path="/")


@router.post("/auth/register")
async def register(payload: AuthInput, request: Request, response: Response) -> dict:
    data = auth_service.register(payload.account, payload.password)
    _set_session_cookie(response, data["token"])
    activity_service.record("register", data["user"]["account"], _client_ip(request), _user_agent(request))
    return success_response({"user": data["user"]}, message="注册成功")


@router.post("/auth/login")
async def login(payload: AuthInput, request: Request, response: Response) -> dict:
    data = auth_service.login(payload.account, payload.password)
    _set_session_cookie(response, data["token"])
    activity_service.record("login", data["user"]["account"], _client_ip(request), _user_agent(request))
    return success_response({"user": data["user"]}, message="登录成功")


@router.get("/auth/me")
async def me(request: Request) -> dict:
    user = auth_service.resolve_session(_read_session_cookie(request))
    return success_response({"user": user})


@router.post("/auth/logout")
async def logout(request: Request, response: Response) -> dict:
    token = _read_session_cookie(request)
    account = auth_service.peek_account(token)  # 退出前取账号用于日志
    auth_service.destroy_session(token)  # 立即清除服务端会话
    _clear_session_cookie(response)
    if account:
        activity_service.record("logout", account, _client_ip(request), _user_agent(request))
    return success_response(message="已退出登录")
