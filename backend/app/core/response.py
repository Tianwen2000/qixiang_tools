"""文件说明：提供统一成功响应结构，保证接口返回格式一致。"""

from typing import Any


def success_response(data: Any = None, message: str = "成功", code: int = 0) -> dict[str, Any]:
    return {"code": code, "message": message, "data": data}
