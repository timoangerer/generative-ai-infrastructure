from uuid import uuid4
import pulsar
import pytest
from pulsar.schema import AvroSchema
from pulsar_schemas import RequestedTxt2ImgGenerationEvent
from config import get_config
from topics import Topics


@pytest.fixture()
def mock_request():
    return RequestedTxt2ImgGenerationEvent(
        id=str(uuid4()),
        generation_settings={
            "prompt": "prompt",
            "negative_prompt": "negative_prompt",
            "styles": ["style1", "style2"],
            "seed": 123,
            "sampler_name": "sampler_name",
            "batch_size": 1,
            "n_iters": 1,
            "steps": 1,
            "cfg_scale": 1.0,
            "width": 1,
            "height": 1,
            "override_settings": {
                "sd_model_checkpoint": "sd_model_checkpoint"
            }
        }
    )


@pytest.mark.basic
def test_basic_request(mock_request):
    config = get_config()
    pulsar_client = pulsar.Client(config.pulsar_broker_service_url)
    pulsar_client = pulsar.Client(config.pulsar_broker_service_url)

    requested_txt2img_generation_producer = pulsar_client.create_producer(
        topic=f"persistent://{config.pulsar_tenant}/{config.pulsar_namespace}/{Topics.REQUESTED_TXT2IMG_GENERATION.value}",
        schema=AvroSchema(RequestedTxt2ImgGenerationEvent))  # type: ignore

    requested_txt2img_generation_producer.send(mock_request)
    assert True
