"""文件说明：提供上传保存、临时文件、下载文件名等文件处理公共函数。"""

import shutil
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

from app.core.config import get_settings
from app.core.exceptions import AppException
from app.utils.validators import validate_upload_for_tool


def create_request_id() -> str:
    return uuid4().hex


def get_request_dirs(request_id: str) -> tuple[Path, Path]:
    settings = get_settings()
    input_dir = settings.temp_dir / "input" / request_id
    output_dir = settings.temp_dir / "output" / request_id
    input_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)
    return input_dir, output_dir


async def save_upload_file(file: UploadFile, request_id: str, tool_slug: str) -> tuple[Path, Path]:
    settings = get_settings()
    validate_upload_for_tool(file=file, tool_slug=tool_slug)

    input_dir, output_dir = get_request_dirs(request_id)
    target_path = input_dir / (file.filename or "upload.bin")
    size = 0

    with target_path.open("wb") as stream:
        while True:
            chunk = await file.read(1024 * 1024)
            if not chunk:
                break
            size += len(chunk)
            if size > settings.max_upload_size_mb * 1024 * 1024:
                raise AppException(
                    message=f"文件过大，单个文件不能超过 {settings.max_upload_size_mb} MB，请压缩后重试。",
                    code=4003,
                    status_code=400,
                )
            stream.write(chunk)

    await file.close()
    return target_path, output_dir


def remove_path(path: Path | str | None) -> None:
    if path is None:
        return
    target = Path(path)
    if not target.exists():
        return
    if target.is_dir():
        shutil.rmtree(target, ignore_errors=True)
    else:
        target.unlink(missing_ok=True)
