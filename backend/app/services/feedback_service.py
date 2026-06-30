"""文件说明：保存用户反馈，并供后台查询最近反馈记录。"""

"""反馈落库业务。

复用 auth 同款健壮性：懒建表、DB 异常兜成 AppException（503），不拖垮其它接口。
过长字段按列上限截断而非拒绝；只有内容为空才报 400。
"""

import threading

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from app.core.exceptions import AppException
from app.core.logger import get_logger
from app.db.init_db import ensure_schema
from app.db.models import Feedback, utcnow
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
        try:
            ensure_schema()
        except SQLAlchemyError as exc:
            logger.warning("数据库初始化失败：%s", exc)
            raise AppException(message="反馈服务暂不可用，请稍后再试", code=5033, status_code=503) from exc
        _schema_ready = True


def _clip(value: str, limit: int) -> str:
    return (value or "").strip()[:limit]


def submit(payload: dict, account: str | None = None) -> dict:
    content = (payload.get("content") or "").strip()
    if not content:
        raise AppException(message="请先填写反馈内容", code=4001, status_code=400)
    _ensure_ready()

    row = Feedback(
        feedback_type=_clip(payload.get("feedbackType", ""), 32),
        content=content[:20000],
        tool_slug=_clip(payload.get("toolSlug", ""), 128),
        tool_name=_clip(payload.get("toolName", ""), 128),
        tool_url=_clip(payload.get("toolUrl", ""), 512),
        contact_type=_clip(payload.get("contactType", ""), 32),
        contact_value=_clip(payload.get("contactValue", ""), 256),
        submitted_page=_clip(payload.get("submittedPage", ""), 512),
        user_agent=_clip(payload.get("userAgent", ""), 512),
        account=(account or None),
        created_at=utcnow(),
    )

    try:
        with session_scope() as session:
            session.add(row)
            session.flush()
            return {"id": row.id}
    except SQLAlchemyError as exc:
        logger.warning("反馈写入失败：%s", exc)
        raise AppException(message="反馈服务暂不可用，请稍后再试", code=5034, status_code=503) from exc


def recent(limit: int = 200) -> list[dict]:
    """按时间倒序取最近的反馈（管理端查看用）。"""
    _ensure_ready()
    try:
        with session_scope() as session:
            rows = session.scalars(select(Feedback).order_by(Feedback.id.desc()).limit(limit)).all()
            return [
                {
                    "id": r.id,
                    "feedback_type": r.feedback_type,
                    "content": r.content,
                    "tool_slug": r.tool_slug,
                    "tool_name": r.tool_name,
                    "tool_url": r.tool_url,
                    "contact_type": r.contact_type,
                    "contact_value": r.contact_value,
                    "submitted_page": r.submitted_page,
                    "user_agent": r.user_agent,
                    "account": r.account or "",
                    "created_at": r.created_at.isoformat(),
                }
                for r in rows
            ]
    except SQLAlchemyError as exc:
        logger.warning("反馈读取失败：%s", exc)
        raise AppException(message="反馈服务暂不可用，请稍后再试", code=5034, status_code=503) from exc
