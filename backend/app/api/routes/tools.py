"""文件说明：提供工具执行、文件上传执行和结果下载接口。"""

import json
from pathlib import Path

from fastapi import APIRouter, File, Form, Request, UploadFile
from fastapi.responses import FileResponse
from starlette.background import BackgroundTask

from app.core.exceptions import AppException
from app.core.response import success_response
from app.schemas.tool_inputs import TextToolExecuteInput
from app.services.cleanup_service import cleanup_request_dirs
from app.services.tool_loader import get_tool_detail
from app.services.tool_registry import get_tool_module
from app.utils.file_utils import create_request_id, get_request_dirs, save_upload_file
from app.utils.validators import validate_tool_supports_mode


router = APIRouter()


def _client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for", "")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else ""


def _build_file_response(result_path: Path, request_id: str) -> FileResponse:
    response = FileResponse(
        path=result_path,
        filename=result_path.name,
        background=BackgroundTask(cleanup_request_dirs, request_id),
    )
    response.headers["Access-Control-Expose-Headers"] = "Content-Disposition"
    return response


@router.post("/tools/{slug}/execute")
async def execute_tool(slug: str, payload: TextToolExecuteInput, request: Request) -> dict:
    tool_meta = get_tool_detail(slug)
    validate_tool_supports_mode(tool_meta.input_mode, allowed={"text", "mixed", "form"})
    module = get_tool_module(slug)
    request_id: str | None = None
    output_dir: Path | None = None

    if tool_meta.result_type == "file":
        request_id = create_request_id()
        _, output_dir = get_request_dirs(request_id)

    try:
        call_params = dict(payload.params)
        if output_dir is not None:
            call_params["output_dir"] = str(output_dir)
        if slug == "local-ip-lookup":
            call_params["client_ip"] = _client_ip(request)
        result = module.run(text=payload.text, **call_params)
    except AppException:
        if request_id:
            cleanup_request_dirs(request_id)
        raise
    except Exception as exc:  # pragma: no cover - safety net
        if request_id:
            cleanup_request_dirs(request_id)
        raise AppException(message=f"工具执行失败：{exc}", code=5001, status_code=500) from exc

    if tool_meta.result_type == "file":
        if request_id is None:
            raise AppException(message="请求初始化失败", code=5002, status_code=500)
        result_path = Path(result)
        if not result_path.exists():
            cleanup_request_dirs(request_id)
            raise AppException(message="结果文件不存在", code=5002, status_code=500)
        return _build_file_response(result_path, request_id)

    return success_response(
        {
            "result": result,
            "result_type": tool_meta.result_type,
            "tool": tool_meta.slug,
        }
    )


@router.post("/tools/{slug}/upload")
async def upload_tool_file(
    slug: str,
    file: UploadFile = File(...),
    params: str = Form(default="{}"),
):
    tool_meta = get_tool_detail(slug)
    validate_tool_supports_mode(tool_meta.input_mode, allowed={"file", "mixed"})

    try:
        parsed_params = json.loads(params) if params else {}
    except json.JSONDecodeError as exc:
        raise AppException(message=f"参数 JSON 格式无效：{exc.msg}", code=4001, status_code=400) from exc

    if not isinstance(parsed_params, dict):
        raise AppException(message="参数必须是 JSON 对象", code=4001, status_code=400)

    request_id = create_request_id()
    input_path, output_dir = await save_upload_file(file=file, request_id=request_id, tool_slug=slug)
    module = get_tool_module(slug)

    try:
        result = module.run(
            input_path=str(input_path),
            output_dir=str(output_dir),
            filename=file.filename or "",
            content_type=file.content_type or "",
            **parsed_params,
        )
    except AppException:
        cleanup_request_dirs(request_id)
        raise
    except Exception as exc:  # pragma: no cover - safety net
        cleanup_request_dirs(request_id)
        raise AppException(message=f"文件处理失败：{exc}", code=5002, status_code=500) from exc

    if tool_meta.result_type == "file":
        result_path = Path(result)
        if not result_path.exists():
            cleanup_request_dirs(request_id)
            raise AppException(message="结果文件不存在", code=5002, status_code=500)
        return _build_file_response(result_path, request_id)

    cleanup_request_dirs(request_id)
    return success_response(
        {
            "result": result,
            "result_type": tool_meta.result_type,
            "tool": tool_meta.slug,
        }
    )
