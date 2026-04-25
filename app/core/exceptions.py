from fastapi import Request
from fastapi.responses import JSONResponse


class BreatheBaseException(Exception):
    status_code: int = 500
    error_code: str = "INTERNAL_ERROR"
    message: str = "An unexpected error occurred"

    def __init__(self, message: str | None = None):
        self.message = message or self.__class__.message
        super().__init__(self.message)


class OWMAPIError(BreatheBaseException):
    status_code = 502
    error_code = "OWM_API_ERROR"
    message = "Failed to fetch data from OpenWeatherMap"


class OWMRateLimitError(OWMAPIError):
    status_code = 429
    error_code = "OWM_RATE_LIMITED"
    message = "OpenWeatherMap rate limit exceeded — please retry shortly"


class GeocodeNotFoundError(BreatheBaseException):
    status_code = 404
    error_code = "LOCATION_NOT_FOUND"
    message = "Could not resolve the given location name"


class InvalidCoordinatesError(BreatheBaseException):
    status_code = 422
    error_code = "INVALID_COORDINATES"
    message = "Latitude must be -90 to 90, longitude -180 to 180"


def add_exception_handlers(app) -> None:
    @app.exception_handler(BreatheBaseException)
    async def breathe_exception_handler(
        request: Request, exc: BreatheBaseException
    ) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": exc.error_code,
                "message": exc.message,
                "path": str(request.url.path),
            },
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        return JSONResponse(
            status_code=500,
            content={
                "error": "INTERNAL_ERROR",
                "message": "An unexpected error occurred",
                "path": str(request.url.path),
            },
        )
