from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class AirQualityReading(Base):
    __tablename__ = "air_quality_readings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    city: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    lat: Mapped[float] = mapped_column(Float, nullable=False)
    lon: Mapped[float] = mapped_column(Float, nullable=False)
    aqi: Mapped[int] = mapped_column(Integer, nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    dominant_pollutant: Mapped[str] = mapped_column(String(20), nullable=False)
    pm2_5: Mapped[float] = mapped_column(Float, nullable=True)
    pm10: Mapped[float] = mapped_column(Float, nullable=True)
    o3: Mapped[float] = mapped_column(Float, nullable=True)
    no2: Mapped[float] = mapped_column(Float, nullable=True)
    so2: Mapped[float] = mapped_column(Float, nullable=True)
    co: Mapped[float] = mapped_column(Float, nullable=True)
    fetched_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
