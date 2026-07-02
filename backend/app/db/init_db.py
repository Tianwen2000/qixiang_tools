"""文件说明：初始化数据库表结构，并做必要的兼容补字段处理。"""

"""建表入口。

不在应用启动时强制建表（避免数据库没配好就拖垮整站），
而是由 ``auth_service`` 在首次用到时懒触发，且失败会被兜成 503。
"""

from app.db.models import Base
from app.db.session import get_engine
from sqlalchemy import inspect, text


COMPAT_COLUMNS = {
    "feedback": {
        "ip": "VARCHAR(64) NOT NULL DEFAULT ''",
        "device_id": "VARCHAR(128) NOT NULL DEFAULT ''",
    },
    "logs": {
        "device_id": "VARCHAR(128) NOT NULL DEFAULT ''",
    },
}


def _ensure_compat_columns() -> None:
    engine = get_engine()
    inspector = inspect(engine)
    table_names = set(inspector.get_table_names())
    with engine.begin() as connection:
        for table_name, columns in COMPAT_COLUMNS.items():
            if table_name not in table_names:
                continue
            existing = {column["name"] for column in inspector.get_columns(table_name)}
            for column_name, column_sql in columns.items():
                if column_name not in existing:
                    connection.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_sql}"))


def ensure_schema() -> None:
    Base.metadata.create_all(bind=get_engine())
    _ensure_compat_columns()
