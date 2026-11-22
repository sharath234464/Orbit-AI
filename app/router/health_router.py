from fastapi import APIRouter, Request
router = APIRouter()

@router.get("/health", tags=["Health"])
async def health(request: Request):
    providers = getattr(request.app.state, "providers", {})
    return {"status": "ok", "database": "connected", "configured_providers": sorted(providers), "provider_count": len(providers)}
