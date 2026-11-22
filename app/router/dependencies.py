from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.service.auth_service import AuthService

bearer = HTTPBearer(auto_error=False)

def get_auth_service(request: Request) -> AuthService:
    service = getattr(request.app.state, "auth_service", None)
    if service is None:
        raise HTTPException(status_code=503, detail="Authentication service is unavailable.")
    return service

async def get_current_user(request: Request, credentials: HTTPAuthorizationCredentials | None = Depends(bearer)):
    if credentials is None:
        raise HTTPException(status_code=401, detail="Sign in to continue.")
    service = get_auth_service(request)
    return await service.current_user(credentials.credentials)
