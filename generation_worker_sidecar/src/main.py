from stable_diffusion.diffusers import generate_txt2img_diffusers
from opentelemetry import trace, context
import atexit
import logging
import pulsar
from pulsar import ConsumerDeadLetterPolicy
from config import Config, get_config
from pulsar.schema import AvroSchema
from otel import setup_otel
from pulsar_schemas import CompletedTxt2ImgGenerationEvent, RequestedTxt2ImgGenerationEvent
from sd_generation import Txt2ImgGenerationOverrideSettings, Txt2ImgGenerationSettings
from topics import Topics
from utils import upload_image_to_s3
from opentelemetry.trace.propagation.tracecontext import \
    TraceContextTextMapPropagator

setup_otel()

tracer = trace.get_tracer(__name__)

pulsar_logger = logging.getLogger('pulsar')

sidecar_logger = logging.getLogger('sidecar')
sidecar_logger.setLevel(logging.INFO)

config = get_config()

pulsar_client = pulsar.Client(
    config.pulsar_broker_service_url, logger=pulsar_logger)

requested_txt2img_generation_consumer = pulsar_client.subscribe(
    topic=f"persistent://{config.pulsar_tenant}/{config.pulsar_namespace}/{Topics.REQUESTED_TXT2IMG_GENERATION.value}",
    subscription_name='requested_txt2img_generation-shared-subscription',
    schema=AvroSchema(RequestedTxt2ImgGenerationEvent),  # type: ignore
    receiver_queue_size=0,
    consumer_type=pulsar.ConsumerType.Shared,
    negative_ack_redelivery_delay_ms=60000,
    dead_letter_policy=ConsumerDeadLetterPolicy(
        max_redeliver_count=3,
        dead_letter_topic=Topics.DLQ_REQUESTED_TXT2IMG_GENERATION.value
    )
)

completed_txt2img_generation_producer = pulsar_client.create_producer(
    topic=f"persistent://{config.pulsar_tenant}/{config.pulsar_namespace}/{Topics.COMPLETED_TXT2IMG_GENERATION.value}",
    producer_name="completed_txt2img_generation_producer",
    schema=AvroSchema(CompletedTxt2ImgGenerationEvent))  # type: ignore


@tracer.start_as_current_span("sidecar.requested_txt2img_generation_event process")
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

    def iter_duration_callback(start, end, i):
        with tracer.start_as_current_span(f"generation_progress_step_{i}", start_time = start) as span:
            span.set_attribute("step", i)

    # type: ignore[end]
    image = generate_txt2img_diffusers(txt2img_generation_settings, iter_duration_callback)
    sidecar_logger.info("Generated image")

    # Store the generated image
    with tracer.start_as_current_span("Save image"):
        upload_image_to_s3(image, config.s3_bucket_name, f"{event.id}.jpg")
        sidecar_logger.info("Saved image")

    # Produce event for generated image
    completed_txt2img_generation_event = CompletedTxt2ImgGenerationEvent(
        id=event.id,
        s3_bucket=config.s3_bucket_name,
        s3_object_key=f"{event.id}.jpg"
    )
    completed_txt2img_generation_producer.send(
        completed_txt2img_generation_event)


@tracer.start_as_current_span("sidecar.requested_txt2img_generation_event receive")
def main():
    sidecar_logger.info(
        "Started Sidecar service")

    while True:
        sidecar_logger.info("Waiting for message...")

        event = requested_txt2img_generation_consumer.receive()
        event_value: RequestedTxt2ImgGenerationEvent = event.value()

        ctx = TraceContextTextMapPropagator().extract(carrier=event.properties())
        context.attach(ctx)

        try:
            process_requested_txt2img_generation_event(config=config, event=event_value)  
            requested_txt2img_generation_consumer.acknowledge(event)
            sidecar_logger.info(
                f"Acknowledged message '{event_value.id}'")
        except Exception as e:
            sidecar_logger.error(
                f"Error while processing message '{event_value.id}': {str(e)}")
            requested_txt2img_generation_consumer.negative_acknowledge(
                event)
            sidecar_logger.error(
                f"Negative acknowledged message '{event_value.id}'")

        

if __name__ == '__main__':
    main()

atexit.register(pulsar_client.close)
