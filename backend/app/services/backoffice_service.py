"""独立后台管理系统鉴权服务。

这套后台不复用 AI 登录用户，不查 users/sessions 表，也不返回给前端任何后台地址常量。
账号、密码、入口问答都只从服务端环境变量读取。
"""

import secrets
import threading
from datetime import datetime, timedelta, timezone

from app.core.config import get_settings
from app.core.exceptions import AppException


_entry_tickets: dict[str, datetime] = {}
_sessions: dict[str, dict[str, object]] = {}
_lock = threading.Lock()
ROLE_ADMIN = "admin"
ROLE_VIEWER = "viewer"


def _now() -> datetime:
    return datetime.now(tz=timezone.utc)


def _clean_expired() -> None:
    now = _now()
    with _lock:
        for ticket, expires_at in list(_entry_tickets.items()):
            if expires_at <= now:
                _entry_tickets.pop(ticket, None)
        for token, data in list(_sessions.items()):
            expires_at = data.get("expires_at")
            if isinstance(expires_at, datetime) and expires_at <= now:
                _sessions.pop(token, None)


def _require_configured() -> None:
    settings = get_settings()
    if not _load_accounts() or not settings.backoffice_entry_answer:
        raise AppException(message="后台管理系统尚未配置", code=5033, status_code=503)


def _load_accounts() -> dict[str, dict[str, str]]:
    """读取后台账号配置；优先使用多账号配置，保留旧单账号兜底。"""
    settings = get_settings()
    accounts: dict[str, dict[str, str]] = {}
    for raw_item in (settings.backoffice_accounts or "").split(","):
        parts = [part.strip() for part in raw_item.split(":")]
        if len(parts) != 3 or not parts[0] or not parts[1]:
            continue
        role = parts[2] if parts[2] in {ROLE_ADMIN, ROLE_VIEWER} else ROLE_VIEWER
        accounts[parts[0]] = {"password": parts[1], "role": role}

    if accounts:
        return accounts

    if settings.backoffice_account and settings.backoffice_password:
        accounts[settings.backoffice_account.strip()] = {
            "password": settings.backoffice_password,
            "role": ROLE_ADMIN,
        }
    return accounts


def _constant_time_equal(actual: str, expected: str) -> bool:
    """按 UTF-8 字节做恒定时间比较，兼容中文入口答案。"""
    return secrets.compare_digest((actual or "").encode("utf-8"), (expected or "").encode("utf-8"))


def cookie_max_age() -> int:
    return get_settings().backoffice_session_hours * 3600


def challenge_question() -> str:
    return get_settings().backoffice_entry_question


def create_entry_ticket(answer: str) -> str:
    """校验入口答案，成功后发一个短时一次性 ticket。"""
    _require_configured()
    expected = get_settings().backoffice_entry_answer.strip()
    actual = (answer or "").strip()
    if not _constant_time_equal(actual, expected):
        raise AppException(message="入口验证失败", code=4015, status_code=401)

    _clean_expired()
    ticket = secrets.token_urlsafe(24)
    with _lock:
        _entry_tickets[ticket] = _now() + timedelta(minutes=2)
    return ticket


def consume_entry_ticket(ticket: str) -> None:
    """后台页面打开后消费 ticket；消费后刷新不会重复使用。"""
    _clean_expired()
    value = (ticket or "").strip()
    if not value:
        raise AppException(message="后台入口已失效", code=4016, status_code=401)
    with _lock:
        expires_at = _entry_tickets.pop(value, None)
    if expires_at is None or expires_at <= _now():
        raise AppException(message="后台入口已失效", code=4016, status_code=401)


def login(account: str, password: str) -> dict:
    """后台账号登录。账号密码由服务端配置，不支持注册。"""
    _require_configured()
    account_value = (account or "").strip()
    account_config = _load_accounts().get(account_value)
    if not account_config or not _constant_time_equal(password or "", account_config["password"]):
        raise AppException(message="后台账号或密码错误", code=4017, status_code=401)

    _clean_expired()
    token = secrets.token_urlsafe(32)
    expires_at = _now() + timedelta(hours=get_settings().backoffice_session_hours)
    with _lock:
        _sessions[token] = {"account": account_value, "role": account_config["role"], "expires_at": expires_at}
    return {
        "token": token,
        "user": {"account": account_value, "role": account_config["role"], "expires_at": expires_at.isoformat()},
    }


def resolve_session(token: str | None) -> dict:
    if not token:
        raise AppException(message="请先登录后台", code=4018, status_code=401)
    _clean_expired()
    with _lock:
        data = _sessions.get(token)
    if not data:
        raise AppException(message="后台登录状态无效，请重新登录", code=4019, status_code=401)
    return {"account": data["account"], "role": data.get("role", ROLE_VIEWER), "expires_at": data["expires_at"].isoformat()}


def require_admin(user: dict) -> None:
    """观察员只能看反馈，管理员才能看全部后台内容。"""
    if user.get("role") != ROLE_ADMIN:
        raise AppException(message="当前后台账号无权查看该内容", code=4031, status_code=403)


def destroy_session(token: str | None) -> None:
    if not token:
        return
    with _lock:
        _sessions.pop(token, None)


def reset_for_tests() -> None:
    """测试专用：清空内存 ticket/session，避免用例互相影响。"""
    with _lock:
        _entry_tickets.clear()
        _sessions.clear()
