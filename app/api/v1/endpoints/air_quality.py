from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, get_owm_client
from app.core.exceptions import GeocodeNotFoundError
from app.db import repository
from app.schemas.air_quality import (
    CompareResponse,
    CurrentAirQualityResponse,
    ForecastEntry,
    ForecastResponse,
    HistoryResponse,
    LocationInfo,
    SafeHoursResponse,
)
from app.services import cache
from app.services.advisory import get_advisories, get_outdoor_safety_score
from app.services.aqi_calculator import compute_aqi
from app.services.owm_client import OWMClient

router = APIRouter()


async def _resolve_location(city: str, owm: OWMClient) -> tuple[float, float, str, str]:
    """Returns (lat, lon, resolved_name, country)."""
    cached = await cache.get_cached_geocode(city)
    if cached:
        geo = cached[0]
    else:
        results = await owm.geocode(city)
        if not results:
            raise GeocodeNotFoundError(f"Location not found: {city!r}")
        await cache.set_cached_geocode(city, results)
        geo = results[0]

    return geo["lat"], geo["lon"], geo["name"], geo.get("country", "")


@router.get("/{city}", response_model=CurrentAirQualityResponse)
async def get_current_air_quality(
    city: str,
    owm: OWMClient = Depends(get_owm_client),
    db: AsyncSession = Depends(get_db),
):
    lat, lon, name, country = await _resolve_location(city, owm)

    # Try cache before hitting OWM
    cached_aq = await cache.get_cached_air_quality(lat, lon)
    if cached_aq:
        raw_aq = cached_aq
    else:
        raw_aq = await owm.get_current_air_pollution(lat, lon)
        await cache.set_cached_air_quality(lat, lon, raw_aq)

    entry = raw_aq["list"][0]
    components = entry["components"]
    aqi_result = compute_aqi(components)

    # Fetch weather in parallel isn't worth the complexity for a single call;
    # it's a fast sequential fetch that adds meaningful data to the response.
    weather_data = None
    try:
        raw_weather = await owm.get_current_weather(lat, lon)
        weather_data = {
            "temperature_c": raw_weather["main"]["temp"],
            "feels_like_c": raw_weather["main"]["feels_like"],
            "humidity_pct": raw_weather["main"]["humidity"],
            "condition": raw_weather["weather"][0]["description"],
            "wind_speed_ms": raw_weather["wind"]["speed"],
        }
        outdoor_safety = get_outdoor_safety_score(
            aqi_result.aqi,
            raw_weather["main"]["temp"],
            raw_weather["main"]["humidity"],
        )
    except Exception:
        outdoor_safety = get_outdoor_safety_score(aqi_result.aqi, 20.0, 50.0)

    # Persist to DB for history tracking
    await repository.save_reading(
        db,
        {
            "city": name.lower(),
            "lat": lat,
            "lon": lon,
            "aqi": aqi_result.aqi,
            "category": aqi_result.category,
            "dominant_pollutant": aqi_result.dominant_pollutant,
            "pm2_5": components.get("pm2_5"),
            "pm10": components.get("pm10"),
            "o3": components.get("o3"),
            "no2": components.get("no2"),
            "so2": components.get("so2"),
            "co": components.get("co"),
        },
    )

    return CurrentAirQualityResponse(
        location=LocationInfo(city=name, country=country, lat=lat, lon=lon),
        aqi={
            "overall": aqi_result.aqi,
            "category": aqi_result.category,
            "color": aqi_result.color,
            "dominant_pollutant": aqi_result.dominant_pollutant,
            "per_pollutant": aqi_result.pollutant_indices,
            "who_guidelines_exceeded": aqi_result.who_guidelines_exceeded,
        },
        components=components,
        advisories=get_advisories(aqi_result.aqi),
        outdoor_safety=outdoor_safety,
        weather=weather_data,
        measured_at=datetime.fromtimestamp(entry["dt"], tz=timezone.utc),
    )


@router.get("/{city}/forecast", response_model=ForecastResponse)
async def get_forecast(
    city: str,
    owm: OWMClient = Depends(get_owm_client),
):
    lat, lon, name, country = await _resolve_location(city, owm)
    raw = await owm.get_air_pollution_forecast(lat, lon)

    entries = []
    for item in raw["list"]:
        components = item["components"]
        result = compute_aqi(components)
        entries.append(
            ForecastEntry(
                aqi=result.aqi,
                category=result.category,
                color=result.color,
                dominant_pollutant=result.dominant_pollutant,
                components=components,
                timestamp=datetime.fromtimestamp(item["dt"], tz=timezone.utc),
            )
        )

    return ForecastResponse(
        location=LocationInfo(city=name, country=country, lat=lat, lon=lon),
        forecast=entries,
    )


@router.get("/{city}/history", response_model=HistoryResponse)
async def get_history(
    city: str,
    limit: int = Query(default=48, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    owm: OWMClient = Depends(get_owm_client),
):
    # Resolve the canonical city name so history lookups are consistent
    _, _, name, _ = await _resolve_location(city, owm)
    readings = await repository.get_history(db, name, limit=limit)

    return HistoryResponse(
        location=name,
        readings=[
            {
                "aqi": r.aqi,
                "category": r.category,
                "dominant_pollutant": r.dominant_pollutant,
                "pm2_5": r.pm2_5,
                "pm10": r.pm10,
                "fetched_at": r.fetched_at,
            }
            for r in readings
        ],
    )


@router.get("/compare/cities", response_model=CompareResponse)
async def compare_cities(
    cities: str = Query(description="Comma-separated city names, e.g. Nairobi,Lagos,Cairo"),
    owm: OWMClient = Depends(get_owm_client),
):
    city_list = [c.strip() for c in cities.split(",") if c.strip()][:5]

    results = []
    for city in city_list:
        lat, lon, name, country = await _resolve_location(city, owm)

        cached = await cache.get_cached_air_quality(lat, lon)
        if cached:
            raw = cached
        else:
            raw = await owm.get_current_air_pollution(lat, lon)
            await cache.set_cached_air_quality(lat, lon, raw)

        components = raw["list"][0]["components"]
        aqi_result = compute_aqi(components)
        outdoor_safety = get_outdoor_safety_score(aqi_result.aqi, 20.0, 50.0)

        results.append(
            {
                "location": LocationInfo(city=name, country=country, lat=lat, lon=lon),
                "aqi": aqi_result.aqi,
                "category": aqi_result.category,
                "color": aqi_result.color,
                "dominant_pollutant": aqi_result.dominant_pollutant,
                "outdoor_safety": outdoor_safety,
            }
        )

    safest = min(results, key=lambda x: x["aqi"])["location"].city
    most_polluted = max(results, key=lambda x: x["aqi"])["location"].city

    return CompareResponse(cities=results, safest=safest, most_polluted=most_polluted)


@router.get("/{city}/safe-hours", response_model=SafeHoursResponse)
async def get_safe_hours(
    city: str,
    owm: OWMClient = Depends(get_owm_client),
):
    lat, lon, name, country = await _resolve_location(city, owm)
    raw = await owm.get_air_pollution_forecast(lat, lon)

    from datetime import date

    today = date.today().isoformat()

    safe_windows = []
    worst_hours = []

    for item in raw["list"]:
        dt = datetime.fromtimestamp(item["dt"], tz=timezone.utc)
        if dt.date().isoformat() != today:
            continue

        components = item["components"]
        result = compute_aqi(components)
        entry = {
            "time": dt.strftime("%H:%M UTC"),
            "aqi": result.aqi,
            "category": result.category,
            "color": result.color,
        }

        if result.aqi < 100:
            safe_windows.append(entry)
        elif result.aqi >= 150:
            worst_hours.append(entry)

    safe_windows.sort(key=lambda x: x["aqi"])

    return SafeHoursResponse(
        location=LocationInfo(city=name, country=country, lat=lat, lon=lon),
        date=today,
        safe_windows=safe_windows,
        worst_hours=worst_hours,
    )
