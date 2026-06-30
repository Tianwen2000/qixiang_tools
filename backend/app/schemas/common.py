"""文件说明：定义 common 相关接口的数据结构。"""

from typing import Any

from pydantic import BaseModel


class ApiResponse(BaseModel):
    code: int = 0
    message: str = "成功"
    data: Any | None = None
