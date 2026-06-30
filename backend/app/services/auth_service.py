"""文件说明：处理 AI 助手用户注册、登录、会话创建和校验。"""

"""登录/注册业务 + 服务端会话。

校验规则：
- 账号：11 位纯数字（可填手机号方便记忆，但不做短信验证）。
- 密码：8-16 位、同时包含字母和数字、区分大小写、不含其它字符。

登录态：服务端会话（``sessions`` 表）+ httpOnly Cookie。
- 登录/注册成功 → 新建一行会话（有效期 30 天）→ 令牌写进 Cookie。
- 退出登录 → 删除该会话行（服务端立即失效）+ 清 Cookie。
- 每次鉴权按 Cookie 里的令牌查会话并校验是否过期。

健壮性：所有数据库异常都兜成 ``AppException``（503），保证数据库不可用时
只有登录功能降级，整站其余工具不受影响。
"""

import re
import secrets
import threading
from datetime import timedelta
from typing import Callable, TypeVar

import bcrypt
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.core.config import get_settings
from app.core.exceptions import AppException
from app.core.logger import get_logger
from app.db.init_db import ensure_schema
from app.db.models import Session as SessionRow
from app.db.models import User, utcnow
from app.db.session import session_scope


logger = get_logger(__name__)

ACCOUNT_PATTERN = re.compile(r"^\d{11}$")
# 8-16 位，必须同时含字母和数字；其它合法字符（含符号）允许，仅排除换行。
PASSWORD_PATTERN = re.compile(r"^(?=.*[A-Za-z])(?=.*\d).{8,16}$")

_schema_ready = False
_schema_lock = threading.Lock()

T = TypeVar("T")


def cookie_max_age() -> int:
    return get_settings().session_expire_days * 86400


def _ensure_ready() -> None:
    """首次访问时懒建表；失败兜成 503，不拖垮其它接口。"""
    global _schema_ready
    if _schema_ready:
        return
    with _schema_lock:
        if _schema_ready:
            return
        try:
            ensure_schema()
        except SQLAlchemyError as exc:
            logger.warning("数据库初始化失败：%s", exc)
            raise AppException(message="登录服务暂不可用，请稍后再试", code=5031, status_code=503) from exc
        _schema_ready = True


def _validate_account(account: str) -> str:
    account = (account or "").strip()
    if not ACCOUNT_PATTERN.match(account):
        raise AppException(message="账号必须是 11 位纯数字", code=4001, status_code=400)
    return account


def _validate_password(password: str) -> str:
    if not PASSWORD_PATTERN.match(password or ""):
        raise AppException(
            message="密码需 8-16 位，且至少同时包含字母和数字（区分大小写）",
            code=4001,
            status_code=400,
        )
    return password


def _hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def _verify_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
    except (ValueError, TypeError):
        return False


def _new_session(session, user: User):
    """为某用户创建一行服务端会话，返回 (会话令牌, 过期时间)。"""
    token = secrets.token_urlsafe(32)
    expires_at = utcnow() + timedelta(days=get_settings().session_expire_days)
    session.add(
        SessionRow(token=token, user_id=user.id, account=user.account, created_at=utcnow(), expires_at=expires_at)
    )
    return token, expires_at


def _safe_db_call(fn: Callable[[], T]) -> T:
    try:
        return fn()
    except AppException:
        raise
    except IntegrityError as exc:
        logger.info("账号唯一约束冲突：%s", exc)
        raise AppException(message="该账号已注册，请直接登录", code=4090, status_code=409) from exc
    except SQLAlchemyError as exc:
        logger.warning("数据库操作失败：%s", exc)
        raise AppException(message="登录服务暂不可用，请稍后再试", code=5032, status_code=503) from exc


def register(account: str, password: str) -> dict:
    account = _validate_account(account)
    password = _validate_password(password)
    _ensure_ready()

    def _do() -> dict:
        with session_scope() as session:
            if session.scalar(select(User).where(User.account == account)) is not None:
                raise AppException(message="该账号已注册，请直接登录", code=4090, status_code=409)
            user = User(account=account, password_hash=_hash_password(password), created_at=utcnow(), last_login_at=utcnow())
            session.add(user)
            session.flush()
            token, expires_at = _new_session(session, user)
            return {
                "token": token,
                "user": {
                    "id": user.id,
                    "account": user.account,
                    "expires_at": expires_at.isoformat(),
                },
            }

    return _safe_db_call(_do)


def login(account: str, password: str) -> dict:
    account = _validate_account(account)
    if not password:
        raise AppException(message="请输入密码", code=4001, status_code=400)
    _ensure_ready()

    def _do() -> dict:
        with session_scope() as session:
            user = session.scalar(select(User).where(User.account == account))
            if user is None or not _verify_password(password, user.password_hash):
                raise AppException(message="账号或密码错误", code=4011, status_code=401)
            user.last_login_at = utcnow()
            token, expires_at = _new_session(session, user)
            return {
                "token": token,
                "user": {
                    "id": user.id,
                    "account": user.account,
                    "expires_at": expires_at.isoformat(),
                },
            }

    return _safe_db_call(_do)


def resolve_session(token: str | None) -> dict:
    """按 Cookie 令牌查会话；无效/过期 → 401。

    读取路径只读、不写库（避免"删除被异常回滚"）；过期时用 destroy_session
    尽力清掉该过期行，且清理失败不影响这里照常返回 401。
    """
    if not token:
        raise AppException(message="请先登录", code=4010, status_code=401)
    _ensure_ready()

    def _do() -> dict | None:
        with session_scope() as session:
            row = session.scalar(select(SessionRow).where(SessionRow.token == token))
            if row is None:
                return None
            if row.expires_at <= utcnow():
                return {"_expired": True}
            return {
                "id": row.user_id,
                "account": row.account,
                "expires_at": row.expires_at.isoformat(),
            }

    result = _safe_db_call(_do)
    if result is None:
        raise AppException(message="登录状态无效，请重新登录", code=4013, status_code=401)
    if result.get("_expired"):
        destroy_session(token)  # 尽力清掉过期行；失败也不影响下面的 401
        raise AppException(message="登录已过期，请重新登录", code=4012, status_code=401)
    return result


def peek_account(token: str | None) -> str | None:
    """尽力而为地取登录账号：有有效会话返回账号，否则返回 None（绝不抛错）。"""
    if not token:
        return None
    try:
        return resolve_session(token).get("account")
    except AppException:
        return None


def destroy_session(token: str | None) -> None:
    """退出登录：删除服务端会话行，使该登录态立即失效。

    尽力而为——即使数据库暂不可用也不抛错，调用方仍会清掉 Cookie。
    """
    if not token:
        return
    try:
        _ensure_ready()
        with session_scope() as session:
            row = session.scalar(select(SessionRow).where(SessionRow.token == token))
            if row is not None:
                session.delete(row)
    except (AppException, SQLAlchemyError) as exc:
        logger.warning("退出登录时清理服务端会话失败（已忽略，Cookie 仍会被清除）：%s", exc)
