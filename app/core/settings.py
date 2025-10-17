"""Core settings for the application."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    gemini_api_key: str = "test_key"
    user_service_url: str = "http://localhost"
    user_cookie_name: str = "COWRITE_SESSION_ID"
    database_url: str

    class Config:
        """Pydantic configuration."""

        # pylint: disable=too-few-public-methods
        env_file = ".env"


settings = Settings()
