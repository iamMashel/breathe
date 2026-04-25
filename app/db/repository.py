from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import AirQualityReading


async def save_reading(session: AsyncSession, data: dict) -> AirQualityReading:
    reading = AirQualityReading(**data)
    session.add(reading)
    await session.flush()
    return reading


async def get_history(
    session: AsyncSession, city: str, limit: int = 48
) -> list[AirQualityReading]:
    result = await session.execute(
        select(AirQualityReading)
        .where(AirQualityReading.city == city.lower())
        .order_by(AirQualityReading.fetched_at.desc())
        .limit(limit)
    )
    return list(result.scalars().all())
