"""测试期强制把数据库指向临时 SQLite 文件。

这样鉴权相关用例无需本地/线上 MySQL 即可跑通；环境变量优先级高于 .env，
因此即使本地配了 MySQL 的 .env，测试也始终走隔离的临时库，互不污染。
"""

import os
import tempfile
from pathlib import Path

_TEST_DB = Path(tempfile.gettempdir()) / "qixiang_auth_test.db"
if _TEST_DB.exists():
    _TEST_DB.unlink()

os.environ["DATABASE_URL"] = f"sqlite:///{_TEST_DB.as_posix()}"
os.environ["SESSION_EXPIRE_DAYS"] = "30"
os.environ["ADMIN_ACCOUNTS"] = "13900000000"
