import os

from dotenv import load_dotenv


class Config:
    def __init__(self):
        load_dotenv()  # Load environment variables from .env
        self.pulsar_service_url = os.getenv('pulsar_service_url')
        self.pulsar_broker_service_url = os.getenv('pulsar_broker_service_url')
        self.pulsar_cluster = os.getenv('pulsar_cluster')
        self.pulsar_tenant = os.getenv('pulsar_tenant')
        self.pulsar_namespace = os.getenv('pulsar_namespace')
        self.trino_host = os.getenv('trino_host')
        self.trino_port = os.getenv('trino_port')
