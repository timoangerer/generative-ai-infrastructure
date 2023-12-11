import pathlib
from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    models_path: pathlib.Path
    sample_mode: bool = False

    class Config:
        env_prefix = ''


@lru_cache
def get_settings():
    return Settings()  # type: ignore
