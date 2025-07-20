from fastapi import APIRouter
from app.api.api_v1.endpoints import health
from app.api.api_v1.endpoints import video

api_router = APIRouter()

# Include different endpoint routers here
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(video.router, prefix="/video", tags=["video"])
