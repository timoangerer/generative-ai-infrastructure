import logging
import pulsar
from src.config import get_config
from pulsar.schema import AvroSchema
from src.pulsar_schemas import RequestedTxt2ImgGenerationEvent
from src.topics import Topics
import atexit

logging.basicConfig(level=logging.WARNING)

pulsar_logger = logging.getLogger('pulsar')

logger = logging.getLogger('test-client')

config = get_config()

pulsar_client = pulsar.Client(
    config.pulsar_broker_service_url, logger=pulsar_logger)


requested_txt2img_generation_consumer = pulsar_client.subscribe(
    topic=f"persistent://{config.pulsar_tenant}/{config.pulsar_namespace}/{Topics.REQUESTED_TXT2IMG_GENERATION.value}",
    subscription_name='requested_txt2img_generation-shared-subscription',
    schema=AvroSchema(RequestedTxt2ImgGenerationEvent),  # type: ignore
    receiver_queue_size=0,
    consumer_type=pulsar.ConsumerType.Shared)

atexit.register(pulsar_client.close)


def main():
    config = get_config(env_file="test.env")

    msg = requested_txt2img_generation_consumer.receive()
    print(msg.value())


if __name__ == '__main__':
    main()
