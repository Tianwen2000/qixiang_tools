from typing import Any

from pydantic import BaseModel, Field


class TextToolExecuteInput(BaseModel):
    text: str = Field(default="", min_length=0, max_length=200000)
    params: dict[str, Any] = Field(default_factory=dict)
