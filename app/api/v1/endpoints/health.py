from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.core.config import settings

router = APIRouter()


@router.get("/healthz")
async def healthz() -> JSONResponse:
    return JSONResponse(
        content={
            "status": "ok",
            "app": settings.APP_NAME,
            "env": settings.APP_ENV,
            "version": "1.0.0",
        }
    )
