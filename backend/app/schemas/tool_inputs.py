"""文件说明：定义 tool inputs 相关接口的数据结构。"""

from typing import Any

from pydantic import BaseModel, Field


class TextToolExecuteInput(BaseModel):
    text: str = Field(default="", min_length=0, max_length=200000)
    params: dict[str, Any] = Field(default_factory=dict)
