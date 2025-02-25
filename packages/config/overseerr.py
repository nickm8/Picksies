from pydantic_settings import BaseSettings
from functools import lru_cache

class OverseerrSettings(BaseSettings):
    """Overseerr API configuration settings."""
    OVERSEERR_URL: str
    OVERSEERR_API_KEY: str

    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_overseerr_settings() -> OverseerrSettings:
    """Get cached Overseerr settings."""
    return OverseerrSettings()
