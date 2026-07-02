"""文件说明：定义用户、会话、反馈和账号活动日志等数据库模型。"""

"""ORM 模型。

``users`` 表存账号；``sessions`` 表存服务端会话（登录态），
退出登录时删除对应会话行即可让该登录态立即失效。不存历史对话，符合从简原则。
"""

from datetime import datetime, timezone

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


def utcnow() -> datetime:
    """统一用不带时区的 UTC，兼容 SQLite/MySQL 的 DATETIME 列。"""
    return datetime.now(tz=timezone.utc).replace(tzinfo=None)


def _pk():
    # MySQL 用 BIGINT；SQLite 必须落到 INTEGER 才能自增（rowid 别名）。
    return mapped_column(BigInteger().with_variant(Integer, "sqlite"), primary_key=True, autoincrement=True)


def _fk_int():
    return BigInteger().with_variant(Integer, "sqlite")


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = _pk()
    account: Mapped[str] = mapped_column(String(11), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=utcnow)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class Session(Base):
    __tablename__ = "sessions"

    id: Mapped[int] = _pk()
    # 随机会话令牌，写进 httpOnly Cookie；服务端按它查会话、删会话。
    token: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(_fk_int(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    account: Mapped[str] = mapped_column(String(11), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=utcnow)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)


class Feedback(Base):
    __tablename__ = "feedback"

    id: Mapped[int] = _pk()
    feedback_type: Mapped[str] = mapped_column(String(32), nullable=False, default="")
    content: Mapped[str] = mapped_column(Text, nullable=False)
    tool_slug: Mapped[str] = mapped_column(String(128), nullable=False, default="")
    tool_name: Mapped[str] = mapped_column(String(128), nullable=False, default="")
    tool_url: Mapped[str] = mapped_column(String(512), nullable=False, default="")
    contact_type: Mapped[str] = mapped_column(String(32), nullable=False, default="")
    contact_value: Mapped[str] = mapped_column(String(256), nullable=False, default="")
    submitted_page: Mapped[str] = mapped_column(String(512), nullable=False, default="")
    user_agent: Mapped[str] = mapped_column(String(512), nullable=False, default="")
    ip: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    device_id: Mapped[str] = mapped_column(String(128), nullable=False, default="")
    # 提交时如已登录，记录账号；匿名则为空。
    account: Mapped[str | None] = mapped_column(String(11), nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=utcnow, index=True)


class ActivityLog(Base):
    __tablename__ = "logs"

    id: Mapped[int] = _pk()
    event: Mapped[str] = mapped_column(String(16), nullable=False, index=True)  # register / login / logout
    account: Mapped[str] = mapped_column(String(11), nullable=False, default="", index=True)
    device_id: Mapped[str] = mapped_column(String(128), nullable=False, default="")
    ip: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    user_agent: Mapped[str] = mapped_column(String(512), nullable=False, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=utcnow, index=True)
