"""AI 对话接口（占位）。

真实模型尚未接入：``/chat/models`` 先返回占位模型供前端选择器渲染，
``/chat`` 校验登录态（服务端会话 Cookie）后回一条占位回复。后续接入多模型时只改本文件。
"""

from fastapi import APIRouter, Request
from pydantic import BaseModel, Field

from app.core.config import get_settings
from app.core.exceptions import AppException
from app.core.response import success_response
from app.services import auth_service


router = APIRouter()

# 占位模型清单（假数据）：接入真实模型后在此替换/扩展即可。
# badge 是列表右侧展示的倍率徽标，纯占位。
MODELS = [
    {"id": "tianwen-1", "name": "天问一号", "description": "占位模型，待接入", "badge": "1.0x"},
    {"id": "tianwen-2", "name": "天问二号", "description": "占位模型，待接入", "badge": "1.6x"},
    {"id": "tianwen-3", "name": "天问三号", "description": "占位模型，待接入", "badge": "0.5x"},
    {"id": "tianwen-4", "name": "天问四号", "description": "占位模型，待接入", "badge": "0.3x"},
]
ALLOWED_HISTORY_ROLES = {"user", "assistant"}
MAX_HISTORY_MESSAGES = 20


class ChatMessage(BaseModel):
    role: str = Field(default="user", max_length=16)
    content: str = Field(default="", max_length=8000)


class ChatInput(BaseModel):
    message: str = Field(default="", max_length=8000)
    model: str = Field(default="", max_length=64)
    history: list[ChatMessage] = Field(default_factory=list)


def validate_history(history: list[ChatMessage]) -> list[ChatMessage]:
    if len(history) > MAX_HISTORY_MESSAGES:
        raise AppException(message=f"历史消息最多支持 {MAX_HISTORY_MESSAGES} 条", code=4001, status_code=400)
    for item in history:
        role = (item.role or "").strip().lower()
        if role not in ALLOWED_HISTORY_ROLES:
            raise AppException(message="历史消息角色仅支持 user 和 assistant", code=4001, status_code=400)
    return history


@router.get("/chat/models")
async def chat_models() -> dict:
    return success_response({"models": MODELS, "default": MODELS[0]["id"]})


@router.post("/chat")
async def chat(payload: ChatInput, request: Request) -> dict:
    token = request.cookies.get(get_settings().session_cookie_name)
    user = auth_service.resolve_session(token)
    text = (payload.message or "").strip()
    if not text:
        raise AppException(message="请输入内容", code=4001, status_code=400)
    validate_history(payload.history)

    model_id = payload.model or MODELS[0]["id"]
    reply = (
        f"（示例回复）你好 {user['account']}，我已收到：{text}\n\n"
        "真实模型尚未接入，接好之后这里会返回模型的实际回复。"
    )
    return success_response({"reply": reply, "model": model_id})
