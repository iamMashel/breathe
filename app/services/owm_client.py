import httpx

from app.core.config import settings
from app.core.exceptions import OWMAPIError, OWMRateLimitError


class OWMClient:
    def __init__(self, client: httpx.AsyncClient) -> None:
        self._client = client
        self._base = settings.OWM_BASE_URL

    async def geocode(self, city: str, limit: int = 1) -> list[dict]:
        try:
            r = await self._client.get(
                f"{self._base}/geo/1.0/direct",
                params={"q": city, "limit": limit, "appid": settings.OWM_API_KEY},
            )
            self._raise_for_owm_status(r)
            return r.json()
        except httpx.TimeoutException as e:
            raise OWMAPIError(f"Geocoding request timed out: {e}") from e

    async def get_current_air_pollution(self, lat: float, lon: float) -> dict:
        try:
            r = await self._client.get(
                f"{self._base}/data/2.5/air_pollution",
                params={"lat": lat, "lon": lon, "appid": settings.OWM_API_KEY},
            )
            self._raise_for_owm_status(r)
            return r.json()
        except httpx.TimeoutException as e:
            raise OWMAPIError(f"Air pollution request timed out: {e}") from e

    async def get_air_pollution_forecast(self, lat: float, lon: float) -> dict:
        try:
            r = await self._client.get(
                f"{self._base}/data/2.5/air_pollution/forecast",
                params={"lat": lat, "lon": lon, "appid": settings.OWM_API_KEY},
            )
            self._raise_for_owm_status(r)
            return r.json()
        except httpx.TimeoutException as e:
            raise OWMAPIError(f"Forecast request timed out: {e}") from e

    async def get_current_weather(self, lat: float, lon: float) -> dict:
        try:
            r = await self._client.get(
                f"{self._base}/data/2.5/weather",
                params={"lat": lat, "lon": lon, "appid": settings.OWM_API_KEY, "units": "metric"},
            )
            self._raise_for_owm_status(r)
            return r.json()
        except httpx.TimeoutException as e:
            raise OWMAPIError(f"Weather request timed out: {e}") from e

    @staticmethod
    def _raise_for_owm_status(response: httpx.Response) -> None:
        if response.status_code == 429:
            raise OWMRateLimitError()
        if response.status_code == 401:
            raise OWMAPIError("Invalid OWM API key")
        if response.status_code >= 400:
            raise OWMAPIError(f"OWM returned HTTP {response.status_code}: {response.text[:200]}")
