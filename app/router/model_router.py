from fastapi import APIRouter, Depends, Request
from app.router.dependencies import get_current_user

router = APIRouter(prefix="/models", tags=["Models"])

@router.get("")
async def list_models(request: Request, user=Depends(get_current_user)):
    rows = await request.app.state.mongodb["model_registry"].find({}, {"_id": 0}).to_list(length=50)
    return {"models": rows}
