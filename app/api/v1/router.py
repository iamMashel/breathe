from fastapi import APIRouter

from app.api.v1.endpoints import air_quality, health

v1_router = APIRouter(prefix="/api/v1")

v1_router.include_router(
    air_quality.router,
    prefix="/air-quality",
    tags=["Air Quality"],
)
v1_router.include_router(
    health.router,
    tags=["System"],
)
