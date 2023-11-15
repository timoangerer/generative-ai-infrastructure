from opentelemetry import trace, context
import asyncio
import atexit
import sys
import logging
import pulsar
from pulsar import ConsumerDeadLetterPolicy
from config import Config, get_config
from pulsar.schema import AvroSchema
from otel import setup_otel
from pulsar_schemas import CompletedTxt2ImgGenerationEvent, RequestedTxt2ImgGenerationEvent
from sd_generation import Txt2ImgGenerationOverrideSettings, Txt2ImgGenerationSettings, generate_txt2img
from topics import Topics
from utils import all_checks_successful, can_upload_to_s3, is_possible_to_generate_txt2img, is_pulsar_topic_available, upload_image_to_s3
from opentelemetry.trace.propagation.tracecontext import \
    TraceContextTextMapPropagator

setup_otel()

tracer = trace.get_tracer(__name__)

logging.basicConfig(level=logging.WARNING)

pulsar_logger = logging.getLogger('pulsar')

sidecar_logger = logging.getLogger('sidecar')
sidecar_logger.setLevel(logging.INFO)

config = get_config(env_file='dev.env')

pulsar_client = pulsar.Client(
    config.pulsar_broker_service_url, logger=pulsar_logger)

requested_txt2img_generation_consumer = pulsar_client.subscribe(
    topic=f"persistent://{config.pulsar_tenant}/{config.pulsar_namespace}/{Topics.REQUESTED_TXT2IMG_GENERATION.value}",
    subscription_name='requested_txt2img_generation-shared-subscription',
    schema=AvroSchema(RequestedTxt2ImgGenerationEvent),  # type: ignore
    receiver_queue_size=0,
    consumer_type=pulsar.ConsumerType.Shared,
    dead_letter_policy=ConsumerDeadLetterPolicy(
        max_redeliver_count=3,
        dead_letter_topic=Topics.DLQ_REQUESTED_TXT2IMG_GENERATION.value
    )
)

completed_txt2img_generation_producer = pulsar_client.create_producer(
    topic=f"persistent://{config.pulsar_tenant}/{config.pulsar_namespace}/{Topics.COMPLETED_TXT2IMG_GENERATION.value}",
    producer_name="completed_txt2img_generation_producer",
    schema=AvroSchema(CompletedTxt2ImgGenerationEvent))  # type: ignore


@tracer.start_as_current_span("process_requested_txt2img_generation_event")
def process_requested_txt2img_generation_event(config: Config, event: RequestedTxt2ImgGenerationEvent):
    sidecar_logger.info("Process event: %s, '%s'", event.id,
                        event.generation_settings.prompt)

    # type: ignore[start]
    txt2img_generation_settings = Txt2ImgGenerationSettings(
        prompt=event.generation_settings.prompt,  # type: ignore
        negative_prompt=event.generation_settings.negative_prompt,  # type: ignore
        styles=event.generation_settings.styles,  # type: ignore
        seed=event.generation_settings.seed,  # type: ignore
        sampler_name=event.generation_settings.sampler_name,  # type: ignore
        batch_size=event.generation_settings.batch_size,  # type: ignore
        n_iters=event.generation_settings.n_iters,  # type: ignore
        steps=event.generation_settings.steps,  # type: ignore
        cfg_scale=event.generation_settings.cfg_scale,  # type: ignore
        width=event.generation_settings.width,  # type: ignore
        height=event.generation_settings.height,  # type: ignore
        override_settings=Txt2ImgGenerationOverrideSettings(
            sd_model_checkpoint=event.generation_settings.override_settings.sd_model_checkpoint  # type: ignore
        )
    )
    # type: ignore[end]
    image = generate_txt2img(config.sd_server_url, txt2img_generation_settings)
    sidecar_logger.info("Generated image")

    # Store the generated image on S3
    with tracer.start_as_current_span("upload image"):
        upload_image_to_s3(image, config.s3_bucket_name, f"{event.id}.jpg")
        sidecar_logger.info("Uploaded image to S3")

    # Produce event for generated image
    completed_txt2img_generation_event = CompletedTxt2ImgGenerationEvent(
        id=event.id,
        s3_bucket=config.s3_bucket_name,
        s3_object_key=f"{event.id}.jpg"
    )
    completed_txt2img_generation_producer.send(
        completed_txt2img_generation_event)


@tracer.start_as_current_span("sidecar_main")
async def main():
    sidecar_logger.info(
        "Started Sidecar service ")

    checks = [
        lambda: can_upload_to_s3(config.s3_bucket_name),
        lambda: is_pulsar_topic_available(
            config.pulsar_service_url, Topics.REQUESTED_TXT2IMG_GENERATION.value),
        lambda: is_pulsar_topic_available(
            config.pulsar_service_url, Topics.COMPLETED_TXT2IMG_GENERATION.value),
        lambda: is_possible_to_generate_txt2img(config.sd_server_url),
    ]

    try:
        while await all_checks_successful(checks):
            while True:
                event = None
                try:
                    sidecar_logger.info("Waiting for message...")
                    event = requested_txt2img_generation_consumer.receive()
                    event_value: RequestedTxt2ImgGenerationEvent = event.value()

                    ctx = TraceContextTextMapPropagator().extract(carrier=event.properties())
                    context.attach(ctx)

                    process_requested_txt2img_generation_event(config=config,
                                                               event=event_value)

                    requested_txt2img_generation_consumer.acknowledge(event)
                    sidecar_logger.info(
                        "Acknowledged message '%s'", event_value.id)
                except Exception as e:
                    if event is not None:
                        event_value: RequestedTxt2ImgGenerationEvent = event.value()
                        sidecar_logger.error(
                            f"Error while processing message '{event_value.id}': {str(e)}")
                        requested_txt2img_generation_consumer.negative_acknowledge(
                            event)
                        requested_txt2img_generation_consumer.redeliver_unacknowledged_messages()
                        sidecar_logger.error(
                            f"Negative acknowledged message '{event_value.id}'")
                    break
    except Exception as e:
        sidecar_logger.error(f"Error in Sidecar: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    asyncio.run(main())

atexit.register(pulsar_client.close)
