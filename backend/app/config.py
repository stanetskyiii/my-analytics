import os
from pydantic import BaseSettings

class Settings(BaseSettings):
    # URL для подключения к PostgreSQL, например: "postgresql://user:pass@host:port/dbname"
    DATABASE_URL: str = os.environ.get("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/analytics_db")
    # Дополнительно можно прописать другие переменные

    class Config:
        env_file = ".env"  # если хотим загружать из .env

settings = Settings()
