"""文件说明：定义工具使用日志上报和后台查询的数据结构。"""

from pydantic import BaseModel, Field


class ToolUsageLogInput(BaseModel):
    toolId: str = Field(default="", max_length=128)
    toolName: str = Field(default="", max_length=128)
    category: str = Field(default="", max_length=64)
    action: str = Field(default="", max_length=32)
    success: bool | None = Field(default=None)
    durationMs: int | None = Field(default=None, ge=0)
    inputLength: int | None = Field(default=None, ge=0)
    outputLength: int | None = Field(default=None, ge=0)
    errorCode: str = Field(default="", max_length=64)
    errorMessage: str = Field(default="", max_length=512)
    sourcePage: str = Field(default="", max_length=512)
    deviceId: str = Field(default="", max_length=128)
