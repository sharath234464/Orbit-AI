from fastapi import APIRouter
from app.router.auth_router import router as auth_router
from app.router.chat_router import router as chat_router
from app.router.health_router import router as health_router
from app.router.analysis_router import router as analysis_router
from app.router.model_router import router as model_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(auth_router, prefix="/v1")
api_router.include_router(chat_router, prefix="/v1")
api_router.include_router(analysis_router, prefix="/v1")
api_router.include_router(model_router, prefix="/v1")
