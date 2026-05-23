from fastapi import APIRouter

from app.api.routes import health, meta, time, tools


api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(meta.router, tags=["meta"])
api_router.include_router(time.router, tags=["time"])
api_router.include_router(tools.router, tags=["tools"])
