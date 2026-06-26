"""独立后台管理系统请求体。"""

from pydantic import BaseModel, Field


class BackofficeEntryInput(BaseModel):
    answer: str = Field(default="", max_length=128)


class BackofficeTicketInput(BaseModel):
    ticket: str = Field(default="", max_length=128)


class BackofficeLoginInput(BaseModel):
    account: str = Field(default="", max_length=128)
    password: str = Field(default="", max_length=128)
