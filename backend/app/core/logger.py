"""文件说明：配置后端控制台日志和项目 log 目录下的分级滚动日志。"""

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
LOG_DIR = PROJECT_ROOT / "log"
LOG_FORMAT = "%(asctime)s %(levelname)s [%(name)s] %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
MAX_LOG_BYTES = 5 * 1024 * 1024
BACKUP_COUNT = 5


class ExactLevelFilter(logging.Filter):
    """只让指定级别的日志进入对应文件，方便按 DEBUG/INFO/WARN/ERROR 查问题。"""

    def __init__(self, level: int) -> None:
        super().__init__()
        self.level = level

    def filter(self, record: logging.LogRecord) -> bool:
        return record.levelno == self.level


def _build_file_handler(filename: str, level: int) -> RotatingFileHandler:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    handler = RotatingFileHandler(
        LOG_DIR / filename,
        maxBytes=MAX_LOG_BYTES,
        backupCount=BACKUP_COUNT,
        encoding="utf-8",
    )
    handler.setLevel(level)
    handler.addFilter(ExactLevelFilter(level))
    handler.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT))
    return handler


def configure_logging() -> None:
    root_logger = logging.getLogger()
    if getattr(root_logger, "_qixiang_logging_configured", False):
        return

    root_logger.setLevel(logging.DEBUG)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT))

    root_logger.handlers.clear()
    root_logger.addHandler(console_handler)
    root_logger.addHandler(_build_file_handler("backend-debug.log", logging.DEBUG))
    root_logger.addHandler(_build_file_handler("backend-info.log", logging.INFO))
    root_logger.addHandler(_build_file_handler("backend-warn.log", logging.WARNING))
    root_logger.addHandler(_build_file_handler("backend-error.log", logging.ERROR))
    root_logger._qixiang_logging_configured = True


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
