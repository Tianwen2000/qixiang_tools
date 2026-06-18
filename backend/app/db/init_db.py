"""建表入口。

不在应用启动时强制建表（避免数据库没配好就拖垮整站），
而是由 ``auth_service`` 在首次用到时懒触发，且失败会被兜成 503。
"""

from app.db.models import Base
from app.db.session import get_engine


def ensure_schema() -> None:
    Base.metadata.create_all(bind=get_engine())
