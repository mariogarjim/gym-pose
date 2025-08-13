from fastapi import APIRouter
from app.api.api_v2.api.router import video_router

api_router = APIRouter()

# Include different endpoint routers here
api_router.include_router(video_router)

__all__ = ["api_router"]
