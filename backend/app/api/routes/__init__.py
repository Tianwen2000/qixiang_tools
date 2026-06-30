"""文件说明：后端路由包标记文件。"""

from fastapi import APIRouter

from app.api.routes import auth, backoffice, chat, feedback, health, meta, time, tools


api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(meta.router, tags=["meta"])
api_router.include_router(time.router, tags=["time"])
api_router.include_router(tools.router, tags=["tools"])
api_router.include_router(auth.router, tags=["auth"])
api_router.include_router(chat.router, tags=["chat"])
api_router.include_router(feedback.router, tags=["feedback"])
api_router.include_router(backoffice.router, tags=["backoffice"])
