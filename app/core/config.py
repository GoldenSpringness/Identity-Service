import os
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    REDIS_URL: str = ""

    JWT_PRIVATE_KEY_PATH: str = ""
    JWT_PUBLIC_KEY_PATH: str = ""

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    ENVIRONMENT: str = "development"

    class Config:
        env_file = ".env"

@lru_cache
def get_settings():
    return Settings()

def load_private_key() -> str:
    return Path(settings.JWT_PRIVATE_KEY_PATH).read_text()


def load_public_key() -> str:
    return Path(settings.JWT_PUBLIC_KEY_PATH).read_text()

settings = get_settings()