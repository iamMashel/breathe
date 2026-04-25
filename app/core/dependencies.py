import httpx
from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import AsyncSessionLocal
from app.services.owm_client import OWMClient


def get_http_client(request: Request) -> httpx.AsyncClient:
    return request.app.state.http_client


def get_owm_client(
    client: httpx.AsyncClient = Depends(get_http_client),
) -> OWMClient:
    return OWMClient(client)


async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
