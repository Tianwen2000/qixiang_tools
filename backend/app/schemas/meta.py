from typing import Any

from pydantic import BaseModel, Field


class ParamOption(BaseModel):
    label: str
    value: Any


class ToolParamMeta(BaseModel):
    key: str
    label: str
    type: str
    default: Any | None = None
    placeholder: str | None = None
    showWhen: dict[str, Any] | None = None
    options: list[ParamOption] = Field(default_factory=list)


class CategoryMeta(BaseModel):
    slug: str
    name: str
    description: str
    enabled: bool = True
    sort_order: int = 0


class ToolMeta(BaseModel):
    slug: str
    module: str
    name: str
    category: str
    summary: str
    description: str
    input_mode: str
    result_type: str
    component: str
    enabled: bool = True
    visible: bool = True
    params: list[ToolParamMeta] = Field(default_factory=list)


class ToolMetaOut(BaseModel):
    slug: str
    name: str
    category: str
    summary: str
    description: str
    input_mode: str
    result_type: str
    component: str
    enabled: bool = True
    visible: bool = True
    params: list[ToolParamMeta] = Field(default_factory=list)
