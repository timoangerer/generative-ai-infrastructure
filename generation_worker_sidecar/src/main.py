import signal
import sys
import logging
import pulsar
from config import Config
from pulsar.schema import AvroSchema
from pulsar_schemas import CompletedTxt2ImgGenerationEvent, RequestedTxt2ImgGenerationEvent, StartedTxt2ImgGenerationEvent
from sd_generation import Txt2ImgGenerationOverrideSettings, Txt2ImgGenerationSettings, generate_txt2img

from topics import Topics
from utils import upload_image_to_s3

logging.basicConfig(level=logging.INFO)

config = Config()

pulsar_client = pulsar.Client(config.pulsar_broker_service_url)

requested_txt2img_generation_consumer = pulsar_client.subscribe(
    topic=f"persistent://{config.pulsar_tenant}/{config.pulsar_namespace}/{Topics.REQUESTED_TXT2IMG_GENERATION.value}",
    subscription_name='requested_txt2img_generation-shared-subscription',
    schema=AvroSchema(RequestedTxt2ImgGenerationEvent), receiver_queue_size=0,
    consumer_type=pulsar.ConsumerType.Shared)

started_txt2img_generation_producer = pulsar_client.create_producer(
    topic=f"persistent://{config.pulsar_tenant}/{config.pulsar_namespace}/{Topics.STARTED_TXT2IMG_GENERATION.value}",
    schema=AvroSchema(StartedTxt2ImgGenerationEvent))

completed_txt2img_generation_producer = pulsar_client.create_producer(
    topic=f"persistent://{config.pulsar_tenant}/{config.pulsar_namespace}/{Topics.COMPLETED_TXT2IMG_GENERATION.value}",
    schema=AvroSchema(CompletedTxt2ImgGenerationEvent))


def process_requested_txt2img_generation_event(pulsar_client: pulsar.Client, config: Config, event: RequestedTxt2ImgGenerationEvent):
    logging.info("Process event: %s, '%s'", event.id,
                 event.generation_settings.prompt)

    # Generate an image from the message
    started_txt2img_generation_producer.send(
        StartedTxt2ImgGenerationEvent(id=event.id))

    txt2img_generation_settings = Txt2ImgGenerationSettings(
        prompt=event.generation_settings.prompt,
        negative_prompt=event.generation_settings.negative_prompt,
        styles=event.generation_settings.styles,
        seed=event.generation_settings.seed,
        sampler_name=event.generation_settings.sampler_name,
        batch_size=event.generation_settings.batch_size,
        n_iters=event.generation_settings.n_iters,
        steps=event.generation_settings.steps,
        cfg_scale=event.generation_settings.cfg_scale,
        width=event.generation_settings.width,
        height=event.generation_settings.height,
        override_settings=Txt2ImgGenerationOverrideSettings(
            sd_model_checkpoint=event.generation_settings.override_settings.sd_model_checkpoint
        )
    )
    image = generate_txt2img(config.sd_server_url, txt2img_generation_settings)
    logging.info("Generated image")

    # Store the generated image on S3
    upload_image_to_s3(image, config.s3_bucket_name, f"{event.id}.jpg")
    logging.info("Uploaded image to S3")

    # Produce event for generated image
    completed_txt2img_generation_event = CompletedTxt2ImgGenerationEvent(
        id=event.id,
        s3_bucket=config.s3_bucket_name,
        s3_object_key=f"{event.id}.jpg"
    )
    completed_txt2img_generation_producer.send(
        completed_txt2img_generation_event)


def signal_handler(sig, frame):
    print('Shutting down gracefully...')

    requested_txt2img_generation_consumer.close()
    started_txt2img_generation_producer.close()
    completed_txt2img_generation_producer.close()

    pulsar_client.close()
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

if __name__ == '__main__':
    logging.info(
        "Started consumer for stream: %s. Waiting for messages...",
        Topics.REQUESTED_TXT2IMG_GENERATION.value)

    while True:
        try:
            event = requested_txt2img_generation_consumer.receive()
            event_value: RequestedTxt2ImgGenerationEvent = event.value()

            process_requested_txt2img_generation_event(pulsar_client=pulsar_client,
                                                       config=config,
                                                       event=event_value)

            requested_txt2img_generation_consumer.acknowledge(event)
            logging.info("Acknowledged message '%s'", event_value.id)
        except Exception as e:
            logging.error(
                f"Error while processing message '{event_value.id}': {str(e)}")
            requested_txt2img_generation_consumer.negative_acknowledge(event)
            logging.warn(f"Negative acknowledged message '{event_value.id}'")
