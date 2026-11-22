from fastapi import APIRouter, Depends, Request
from app.router.dependencies import get_current_user

router = APIRouter(prefix="/analysis", tags=["Analysis"])

@router.get("/dashboard")
async def dashboard(request: Request, user=Depends(get_current_user)):
    repository = request.app.state.usage_repository
    return await repository.dashboard_stats()

@router.get("/usage")
async def usage(request: Request, user=Depends(get_current_user)):
    return await request.app.state.usage_repository.recent_usage()
