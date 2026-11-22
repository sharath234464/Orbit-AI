from fastapi import APIRouter, Depends, Request
from app.router.dependencies import get_auth_service, get_current_user
from app.schemas.auth_schema import RegisterRequest, LoginRequest, AuthResponse, UserResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=AuthResponse, status_code=201)
async def register(payload: RegisterRequest, request: Request, service=Depends(get_auth_service)):
    return await service.register(payload.name, str(payload.email), payload.password)

@router.post("/login", response_model=AuthResponse)
async def login(payload: LoginRequest, service=Depends(get_auth_service)):
    return await service.login(str(payload.email), payload.password)

@router.get("/me", response_model=UserResponse)
async def me(user=Depends(get_current_user)):
    return user
