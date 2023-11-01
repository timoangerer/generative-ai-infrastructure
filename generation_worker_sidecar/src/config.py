from dotenv import load_dotenv
import os


class Config:
    def __init__(self):
        load_dotenv()  # Load environment variables from .env
        self.pulsar_service_url = os.getenv('pulsar_service_url')
        self.pulsar_broker_service_url = os.getenv('pulsar_broker_service_url')
        self.pulsar_cluster = os.getenv('pulsar_cluster')
        self.pulsar_tenant = os.getenv('pulsar_tenant')
        self.pulsar_namespace = os.getenv('pulsar_namespace')
        self.sd_server_url = os.getenv('sd_server_url')
        self.s3_bucket_name = os.getenv('s3_bucket_name')
