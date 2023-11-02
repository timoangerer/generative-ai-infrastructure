import pulsar
from pulsar.schema import AvroSchema

from config import get_config
from models import Txt2ImgGenerationRequest
from pulsar_schemas import \
    RequestedTxt2ImgGenerationEvent as PulsarRequestedTxt2ImgGenerationEvent
from pulsar_schemas import \
    Txt2ImgGenerationOverrideSettings as \
    PulsarTxt2ImgGenerationOverrideSettings
from pulsar_schemas import \
    Txt2ImgGenerationSettings as PulsarTxt2ImgGenerationSettings
from topics import Topics

config = get_config()

client = pulsar.Client(config.pulsar_broker_service_url)


def send_generation_request(generation_request: Txt2ImgGenerationRequest):
    producer = client.create_producer(
        topic=f"persistent://{config.pulsar_tenant}/{config.pulsar_namespace}/{Topics.REQUESTED_TXT2IMG_GENERATION.value}",
        schema=AvroSchema(PulsarRequestedTxt2ImgGenerationEvent))  # type: ignore

    override_settings = PulsarTxt2ImgGenerationOverrideSettings(
        sd_model_checkpoint=generation_request.generation_settings.override_settings.sd_model_checkpoint
    )

    generation_settings = PulsarTxt2ImgGenerationSettings(
        prompt=generation_request.generation_settings.prompt,
        negative_prompt=generation_request.generation_settings.negative_prompt,
        styles=generation_request.generation_settings.styles,
        seed=generation_request.generation_settings.seed,
        sampler_name=generation_request.generation_settings.sampler_name,
        batch_size=generation_request.generation_settings.batch_size,
        n_iters=generation_request.generation_settings.n_iters,
        steps=generation_request.generation_settings.steps,
        cfg_scale=generation_request.generation_settings.cfg_scale,
        width=generation_request.generation_settings.width,
        height=generation_request.generation_settings.height,
        override_settings=override_settings
    )

    pulsar_generation_request = PulsarRequestedTxt2ImgGenerationEvent(
        id=str(generation_request.id),
        metadata=generation_request.metadata,
        generation_settings=generation_settings
    )

    producer.send(pulsar_generation_request)


def close_pulsar_resources():
    client.close()
