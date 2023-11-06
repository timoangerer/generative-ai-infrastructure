from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    pulsar_service_url: str = Field(...)
    pulsar_broker_service_url: str = Field(...)
    pulsar_cluster: str = Field(...)
    pulsar_tenant: str = Field(...)
    pulsar_namespace: str = Field(...)
    sd_server_url: str = Field(...)
    s3_bucket_name: str = Field(...)

    aws_access_key_id: str = Field(...)
    aws_secret_access_key: str = Field(...)

    model_config = SettingsConfigDict(env_file=".env")


@lru_cache
def get_config():
    return Config()  # type: ignore
