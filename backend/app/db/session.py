"""数据库会话管理。

设计要点（关键：绝不影响现有无数据库工具）：
- 引擎懒加载：import 本模块不会连库，第一次真正用到时才建引擎。
- 建引擎/连库失败都向上抛 ``SQLAlchemyError``，由 ``auth_service`` 兜成
  友好的 ``AppException``，因此即使数据库没配好/连不上，整站其余工具照常工作。
- 引擎按连接串自动适配 SQLite（测试）与 MySQL（线上）。
"""

import threading
from contextlib import contextmanager
from typing import Iterator

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine, make_url
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import get_settings


_engine: Engine | None = None
_session_factory: sessionmaker[Session] | None = None
_lock = threading.Lock()


def _build_engine() -> Engine:
    settings = get_settings()
    url = make_url(settings.database_url)

    kwargs: dict = {"pool_pre_ping": True, "future": True}
    if url.get_backend_name() == "sqlite":
        kwargs["connect_args"] = {"check_same_thread": False}
        if url.database in (None, "", ":memory:"):
            # 内存库必须共享同一连接，否则每个连接各看到一个空库。
            kwargs["poolclass"] = StaticPool
    else:
        # MySQL 等长连接，回收空闲连接避免 "server has gone away"。
        kwargs["pool_recycle"] = 3600

    return create_engine(url, **kwargs)


def get_engine() -> Engine:
    global _engine, _session_factory
    if _engine is None:
        with _lock:
            if _engine is None:
                engine = _build_engine()
                _session_factory = sessionmaker(
                    bind=engine,
                    autoflush=False,
                    expire_on_commit=False,
                    class_=Session,
                )
                _engine = engine
    return _engine


def get_session_factory() -> sessionmaker[Session]:
    get_engine()
    assert _session_factory is not None  # get_engine 保证已初始化
    return _session_factory


@contextmanager
def session_scope() -> Iterator[Session]:
    session = get_session_factory()()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
