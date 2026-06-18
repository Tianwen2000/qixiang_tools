"""账号活动日志（注册/登录/退出）。

写入是"尽力而为"：任何数据库异常都吞掉，绝不影响登录主流程。
读取供管理员查看页使用。
"""

import threading

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from app.core.exceptions import AppException
from app.core.logger import get_logger
from app.db.init_db import ensure_schema
from app.db.models import ActivityLog, utcnow
from app.db.session import session_scope


logger = get_logger(__name__)

_schema_ready = False
_schema_lock = threading.Lock()


def _ensure_ready() -> None:
    global _schema_ready
    if _schema_ready:
        return
    with _schema_lock:
        if _schema_ready:
            return
        ensure_schema()  # 失败由调用方处理（record 吞掉，recent 兜成 503）
        _schema_ready = True


def record(event: str, account: str = "", ip: str = "", user_agent: str = "") -> None:
    """记录一条账号活动日志；失败仅告警，不抛错。"""
    try:
        _ensure_ready()
        with session_scope() as session:
            session.add(
                ActivityLog(
                    event=event[:16],
                    account=(account or "")[:11],
                    ip=(ip or "")[:64],
                    user_agent=(user_agent or "")[:512],
                    created_at=utcnow(),
                )
            )
    except SQLAlchemyError as exc:
        logger.warning("活动日志写入失败（已忽略）：%s", exc)


def recent(limit: int = 200) -> list[dict]:
    try:
        _ensure_ready()
        with session_scope() as session:
            rows = session.scalars(select(ActivityLog).order_by(ActivityLog.id.desc()).limit(limit)).all()
            return [
                {
                    "id": r.id,
                    "event": r.event,
                    "account": r.account,
                    "ip": r.ip,
                    "user_agent": r.user_agent,
                    "created_at": r.created_at.isoformat(),
                }
                for r in rows
            ]
    except SQLAlchemyError as exc:
        logger.warning("活动日志读取失败：%s", exc)
        raise AppException(message="日志服务暂不可用，请稍后再试", code=5035, status_code=503) from exc
