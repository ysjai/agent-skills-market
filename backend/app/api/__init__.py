from fastapi import APIRouter

from app.api.routers.auth import router as auth_router
from app.api.routers.blobs import router as blobs_router
from app.api.routers.skills import router as skills_router
from app.api.routers.trees import router as trees_router

api_router = APIRouter(prefix="/api")
api_router.include_router(auth_router)
api_router.include_router(skills_router)
api_router.include_router(blobs_router)
api_router.include_router(trees_router)

__all__ = ["api_router"]
