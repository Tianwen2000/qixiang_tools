"""文件说明：提供工具使用行为日志上报接口。"""

from ipaddress import ip_address

from fastapi import APIRouter, Request

from app.core.config import get_settings
from app.core.response import success_response
from app.schemas.tool_usage import ToolUsageLogInput
from app.services import auth_service, tool_usage_service


router = APIRouter()


def _client_ipv4(request: Request) -> str:
    """优先取公网 IPv4；本地开发或内网访问时回退到第一个可识别 IPv4。"""
    candidates: list[str] = []
    for header in ("cf-connecting-ip", "true-client-ip", "x-real-ip", "x-forwarded-for"):
        value = request.headers.get(header, "")
        if value:
            candidates.extend(item.strip() for item in value.split(",") if item.strip())
    if request.client and request.client.host:
        candidates.append(request.client.host)

    fallback_ipv4 = ""
    for candidate in candidates:
        try:
            parsed = ip_address(candidate)
        except ValueError:
            continue
        if parsed.version != 4:
            continue
        if not fallback_ipv4:
            fallback_ipv4 = str(parsed)
        if not parsed.is_private and not parsed.is_loopback:
            return str(parsed)
    return fallback_ipv4


@router.post("/tool-usage-logs")
async def submit_tool_usage_log(payload: ToolUsageLogInput, request: Request) -> dict:
    token = request.cookies.get(get_settings().session_cookie_name)
    account = auth_service.peek_account(token)
    data = tool_usage_service.submit(
        payload.model_dump(),
        account=account or "",
        ip=_client_ipv4(request),
        user_agent=request.headers.get("user-agent", ""),
    )
    return success_response(data, message="工具使用日志已记录")
