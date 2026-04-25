from datetime import datetime

from pydantic import BaseModel, Field


class PollutantComponents(BaseModel):
    co: float = Field(description="Carbon monoxide (µg/m³)")
    no: float = Field(description="Nitrogen monoxide (µg/m³)")
    no2: float = Field(description="Nitrogen dioxide (µg/m³)")
    o3: float = Field(description="Ozone (µg/m³)")
    so2: float = Field(description="Sulphur dioxide (µg/m³)")
    pm2_5: float = Field(description="Fine particles <2.5µm (µg/m³)")
    pm10: float = Field(description="Coarse particles <10µm (µg/m³)")
    nh3: float = Field(description="Ammonia (µg/m³)")


class AQIBreakdown(BaseModel):
    overall: int = Field(description="EPA AQI (0-500)")
    category: str
    color: str = Field(description="Hex color for UI rendering")
    dominant_pollutant: str
    per_pollutant: dict[str, int] = Field(description="AQI sub-index per pollutant")
    who_guidelines_exceeded: list[str] = Field(
        description="Pollutants above WHO 2021 24-hour guidelines"
    )


class LocationInfo(BaseModel):
    city: str
    country: str
    lat: float
    lon: float


class CurrentAirQualityResponse(BaseModel):
    location: LocationInfo
    aqi: AQIBreakdown
    components: PollutantComponents
    advisories: dict[str, str] = Field(
        description="Health advisories keyed by population group"
    )
    outdoor_safety: dict = Field(
        description="Composite outdoor safety score and label"
    )
    weather: dict | None = Field(default=None, description="Current weather conditions")
    measured_at: datetime


class ForecastEntry(BaseModel):
    aqi: int
    category: str
    color: str
    dominant_pollutant: str
    components: PollutantComponents
    timestamp: datetime


class ForecastResponse(BaseModel):
    location: LocationInfo
    forecast: list[ForecastEntry]


class HistoryEntry(BaseModel):
    aqi: int
    category: str
    dominant_pollutant: str
    pm2_5: float | None
    pm10: float | None
    fetched_at: datetime


class HistoryResponse(BaseModel):
    location: str
    readings: list[HistoryEntry]


class CompareEntry(BaseModel):
    location: LocationInfo
    aqi: int
    category: str
    color: str
    dominant_pollutant: str
    outdoor_safety: dict


class CompareResponse(BaseModel):
    cities: list[CompareEntry]
    safest: str
    most_polluted: str


class SafeHoursResponse(BaseModel):
    location: LocationInfo
    date: str
    safe_windows: list[dict] = Field(
        description="Time windows with AQI < 100, sorted by air quality"
    )
    worst_hours: list[dict] = Field(description="Hours to avoid (AQI >= 150)")
