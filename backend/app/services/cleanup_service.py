from datetime import datetime, timedelta, timezone

from app.core.config import get_settings
from app.utils.file_utils import remove_path


def ensure_temp_layout() -> None:
    settings = get_settings()
    (settings.temp_dir / "input").mkdir(parents=True, exist_ok=True)
    (settings.temp_dir / "output").mkdir(parents=True, exist_ok=True)


def cleanup_request_dirs(request_id: str) -> None:
    settings = get_settings()
    remove_path(settings.temp_dir / "input" / request_id)
    remove_path(settings.temp_dir / "output" / request_id)


def cleanup_expired_dirs() -> None:
    settings = get_settings()
    threshold = datetime.now(tz=timezone.utc) - timedelta(minutes=settings.file_ttl_minutes)
    for base_dir in (settings.temp_dir / "input", settings.temp_dir / "output"):
        if not base_dir.exists():
            continue
        for child in base_dir.iterdir():
            if not child.is_dir():
                continue
            modified_at = datetime.fromtimestamp(child.stat().st_mtime, tz=timezone.utc)
            if modified_at < threshold:
                remove_path(child)


def startup_cleanup() -> None:
    ensure_temp_layout()
    cleanup_expired_dirs()
