from fastapi import APIRouter, Depends, HTTPException, Request
from app.router.dependencies import get_current_user
from app.schemas.chat_schema import ChatRequest, ChatResponse

router = APIRouter()

@router.post("/chat/completions", response_model=ChatResponse)
async def chat_completions(payload: ChatRequest, request: Request, user=Depends(get_current_user)):
    service = request.app.state.gateway_service
    try:
        return await service.chat(payload, user)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail="Chat generation failed. Check backend logs, model availability, and API credentials.") from exc
