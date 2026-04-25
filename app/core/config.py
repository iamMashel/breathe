from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    APP_NAME: str = "Breathe"
    APP_ENV: str = "development"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"

    OWM_API_KEY: str
    OWM_BASE_URL: str = "https://api.openweathermap.org"

    CACHE_TTL_SECONDS: int = 600
    GEOCODE_CACHE_TTL_SECONDS: int = 86400

    DATABASE_URL: str = "sqlite+aiosqlite:///./breathe.db"

    @field_validator("APP_ENV")
    @classmethod
    def validate_env(cls, v: str) -> str:
        allowed = {"development", "staging", "production"}
        if v not in allowed:
            raise ValueError(f"APP_ENV must be one of {allowed}")
        return v


settings = Settings()
