from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    pulsar_service_url: str = Field(...)
    pulsar_broker_service_url: str = Field(...)
    pulsar_cluster: str = Field(...)
    pulsar_tenant: str = Field(...)
    pulsar_namespace: str = Field(...)
    trino_host: str = Field(...)
    trino_port: int = Field(...)
    trino_user: str = Field(...)
    trino_catalog: str = Field(...)
    trino_schema: str = Field(...)

    otel_service_name: str = Field(...)
    otel_exporter_otlp_endpoint: str = Field(...)

    model_config = SettingsConfigDict(env_file=".env")


@lru_cache
def get_config():
    return Config()  # type: ignore
