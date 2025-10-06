"""Core settings for the application."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    gemini_api_key: str
    user_service_url: str
    user_cookie_name: str
    database_url: str

    class Config:
        """Pydantic configuration."""

        # pylint: disable=too-few-public-methods
        env_file = ".env"


settings = Settings()
