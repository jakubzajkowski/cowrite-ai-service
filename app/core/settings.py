"""Core settings for the application."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    gemini_api_key: str = "test_key"
    user_service_url: str = "http://localhost"
    user_cookie_name: str = "COWRITE_SESSION_ID"
    database_url: str = "postgresql+asyncpg://user:password@localhost:5432/app_db"
    jwt_secret_key: str = "your_jwt_secret_key_here"
    s3_endpoint_url: str = "http://localhost:4566"
    aws_access_key_id: str = "test"
    aws_secret_access_key: str = "test"
    aws_region: str = "us-east-1"
    aws_s3_bucket: str = "chat-files-bucket"
    chroma_host: str = "localhost"
    chroma_port: int = 8001

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
