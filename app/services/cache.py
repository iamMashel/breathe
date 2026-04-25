import asyncio

from cachetools import TTLCache

from app.core.config import settings

_air_quality_cache: TTLCache = TTLCache(
    maxsize=1000,
    ttl=settings.CACHE_TTL_SECONDS,
)
_geocode_cache: TTLCache = TTLCache(
    maxsize=5000,
    ttl=settings.GEOCODE_CACHE_TTL_SECONDS,
)
_lock = asyncio.Lock()


def _round_coord(val: float, precision: int = 2) -> float:
    """Reduce cache misses from marginally different coordinates."""
    return round(val, precision)


async def get_cached_air_quality(lat: float, lon: float) -> dict | None:
    key = (_round_coord(lat), _round_coord(lon))
    return _air_quality_cache.get(key)


async def set_cached_air_quality(lat: float, lon: float, data: dict) -> None:
    key = (_round_coord(lat), _round_coord(lon))
    async with _lock:
        _air_quality_cache[key] = data


async def get_cached_geocode(city: str) -> list | None:
    return _geocode_cache.get(city.lower().strip())


async def set_cached_geocode(city: str, data: list) -> None:
    async with _lock:
        _geocode_cache[city.lower().strip()] = data
