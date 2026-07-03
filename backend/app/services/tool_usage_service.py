"""文件说明：保存工具使用行为日志，并提供后台分页筛选查询。"""

from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError

from app.core.exceptions import AppException
from app.core.logger import get_logger
from app.db.init_db import ensure_schema
from app.db.models import ToolUsageLog, utcnow
from app.db.session import session_scope


logger = get_logger(__name__)
MAX_PAGE_SIZE = 100


def _clip(value: str, limit: int) -> str:
    return (value or "").strip()[:limit]


def _safe_int(value: int | None) -> int:
    try:
        return max(0, int(value or 0))
    except (TypeError, ValueError):
        return 0


def _parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    normalized = value.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(normalized).replace(tzinfo=None)
    except ValueError:
        return None


def submit(payload: dict, account: str = "", ip: str = "", user_agent: str = "") -> dict:
    """保存一条工具行为日志；不保存原始输入和原始输出。"""
    try:
        ensure_schema()
        row = ToolUsageLog(
            account=_clip(account, 11),
            device_id=_clip(payload.get("deviceId", ""), 128),
            ip=_clip(ip, 64),
            user_agent=_clip(user_agent or payload.get("userAgent", ""), 512),
            source_page=_clip(payload.get("sourcePage", ""), 512),
            tool_id=_clip(payload.get("toolId", ""), 128),
            tool_name=_clip(payload.get("toolName", ""), 128),
            category=_clip(payload.get("category", ""), 64),
            action=_clip(payload.get("action", ""), 32),
            success="success" if payload.get("success") is True else "fail" if payload.get("success") is False else "",
            duration_ms=_safe_int(payload.get("durationMs")),
            input_length=_safe_int(payload.get("inputLength")),
            output_length=_safe_int(payload.get("outputLength")),
            error_code=_clip(payload.get("errorCode", ""), 64),
            error_message=_clip(payload.get("errorMessage", ""), 512),
            created_at=utcnow(),
        )
        with session_scope() as session:
            session.add(row)
            session.flush()
            return {"id": row.id}
    except SQLAlchemyError as exc:
        logger.warning("工具使用日志写入失败：%s", exc)
        raise AppException(message="工具使用日志暂不可用", code=5035, status_code=503) from exc


def query(
    *,
    page: int = 1,
    page_size: int = 30,
    start_time: str = "",
    end_time: str = "",
    tool_name: str = "",
    category: str = "",
    action: str = "",
    success: str = "",
    account: str = "",
    ip: str = "",
) -> dict:
    """后台分页查询工具使用日志，按时间倒序返回。"""
    try:
        ensure_schema()
        page_value = max(1, int(page or 1))
        page_size_value = min(MAX_PAGE_SIZE, max(1, int(page_size or 30)))
    except (TypeError, ValueError):
        page_value = 1
        page_size_value = 30

    conditions = []
    start_at = _parse_datetime(start_time)
    end_at = _parse_datetime(end_time)
    if start_at:
        conditions.append(ToolUsageLog.created_at >= start_at)
    if end_at:
        conditions.append(ToolUsageLog.created_at <= end_at)
    if tool_name:
        conditions.append(ToolUsageLog.tool_name.like(f"%{tool_name.strip()}%"))
    if category:
        conditions.append(ToolUsageLog.category == category.strip())
    if action:
        conditions.append(ToolUsageLog.action == action.strip())
    if success:
        conditions.append(ToolUsageLog.success == success.strip())
    if account:
        conditions.append(ToolUsageLog.account.like(f"%{account.strip()}%"))
    if ip:
        conditions.append(ToolUsageLog.ip.like(f"%{ip.strip()}%"))

    try:
        with session_scope() as session:
            total_stmt = select(func.count()).select_from(ToolUsageLog)
            list_stmt = select(ToolUsageLog).order_by(ToolUsageLog.id.desc())
            if conditions:
                total_stmt = total_stmt.where(*conditions)
                list_stmt = list_stmt.where(*conditions)
            total = int(session.scalar(total_stmt) or 0)
            rows = session.scalars(list_stmt.offset((page_value - 1) * page_size_value).limit(page_size_value)).all()
            return {
                "items": [
                    {
                        "id": row.id,
                        "created_at": row.created_at.isoformat(),
                        "account": row.account,
                        "device_id": row.device_id,
                        "ip": row.ip,
                        "user_agent": row.user_agent,
                        "source_page": row.source_page,
                        "tool_id": row.tool_id,
                        "tool_name": row.tool_name,
                        "category": row.category,
                        "action": row.action,
                        "success": row.success,
                        "duration_ms": row.duration_ms,
                        "input_length": row.input_length,
                        "output_length": row.output_length,
                        "error_code": row.error_code,
                        "error_message": row.error_message,
                    }
                    for row in rows
                ],
                "page": page_value,
                "page_size": page_size_value,
                "total": total,
            }
    except SQLAlchemyError as exc:
        logger.warning("工具使用日志查询失败：%s", exc)
        raise AppException(message="工具使用日志暂不可用", code=5035, status_code=503) from exc
