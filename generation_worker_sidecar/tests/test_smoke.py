
from uuid import uuid4
import boto3
from botocore.exceptions import ClientError
from pulsar.schema import AvroSchema
import pytest
import pulsar
from config import Config, get_config
from tests.pulsar_admin_utils import create_tenant_namespace_topics, delete_tenant_namespace_topics, get_stats
from topics import Topics
from pulsar_schemas import CompletedTxt2ImgGenerationEvent, RequestedTxt2ImgGenerationEvent


# @pytest.fixture()
# def config():
#     conf = Config()  # type: ignore

#     service_url = conf.pulsar_service_url
#     cluster = conf.pulsar_cluster
#     tenant = conf.pulsar_tenant
#     namespace = conf.pulsar_namespace

#     conf.pulsar_namespace = namespace

#     topics = [topic.value for topic in Topics]

#     delete_tenant_namespace_topics(
#         service_url, tenant, namespace, topics)

#     create_tenant_namespace_topics(
#         service_url, cluster, tenant, namespace, topics)

#     yield conf

#     delete_tenant_namespace_topics(
#         service_url, tenant, namespace, topics)


def file_exists_in_s3(bucket_name, file_key):
    s3 = boto3.client('s3')

    try:
        s3.head_object(Bucket=bucket_name, Key=file_key)
        return True
    except ClientError as e:
        # The file does not exist or other error
        return False


@pytest.fixture()
def mock_request():
    return RequestedTxt2ImgGenerationEvent(
        id=str(uuid4()),
        generation_settings={
            "prompt": "prompt",
            "negative_prompt": "negative_prompt",
            "styles": ["style1", "style2"],
            "seed": 123,
            "sampler_name": "euler",
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


@pytest.fixture()
def mock_request_invalid():
    return RequestedTxt2ImgGenerationEvent(
        id=str(uuid4()),
        generation_settings={
            "prompt": "prompt",
            "negative_prompt": "negative_prompt",
            "styles": ["style1", "style2"],
            "seed": 123,
            "sampler_name": "invalid_sampler_name_will_cause_error",
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


def read_message_from_topic(pulsar_broker_service_url, pulsar_tenant, pulsar_namespace, topic_name, cls):
    pulsar_client = pulsar.Client(pulsar_broker_service_url)

    consumer = pulsar_client.subscribe(
        topic=f"persistent://{pulsar_tenant}/{pulsar_namespace}/{topic_name}",
        subscription_name='requested_txt2img_generation-shared-subscription',
        schema=AvroSchema(cls),  # type: ignore
        receiver_queue_size=0,
        initial_position=pulsar.InitialPosition.Earliest
    )

    msg = consumer.receive()

    pulsar_client.close()

    return msg.value()


def send_message_to_topic(pulsar_broker_service_url, pulsar_tenant, pulsar_namespace, topic_name, cls, message):
    pulsar_client = pulsar.Client(pulsar_broker_service_url)

    producer = pulsar_client.create_producer(
        topic=f"persistent://{pulsar_tenant}/{pulsar_namespace}/{topic_name}",
        schema=AvroSchema(cls))  # type: ignore

    producer.send(message)

    pulsar_client.close()


@pytest.mark.basic
def test_e2e_smoke(mock_request):
    config = get_config(env_file="test.env")

    send_message_to_topic(config.pulsar_broker_service_url, config.pulsar_tenant, config.pulsar_namespace,
                          Topics.REQUESTED_TXT2IMG_GENERATION.value, RequestedTxt2ImgGenerationEvent, mock_request)

    request_event: RequestedTxt2ImgGenerationEvent = read_message_from_topic(
        config.pulsar_broker_service_url,
        config.pulsar_tenant, config.pulsar_namespace,
        Topics.REQUESTED_TXT2IMG_GENERATION.value,
        RequestedTxt2ImgGenerationEvent)
    assert request_event.id == mock_request.id

    stats = get_stats(config.pulsar_service_url, config.pulsar_tenant, config.pulsar_namespace,
                      Topics.REQUESTED_TXT2IMG_GENERATION.value)
    msg_count = stats["msgInCounter"]
    assert msg_count == 1

    completed_event: CompletedTxt2ImgGenerationEvent = read_message_from_topic(
        config.pulsar_broker_service_url,
        config.pulsar_tenant, config.pulsar_namespace,
        Topics.COMPLETED_TXT2IMG_GENERATION.value,
        CompletedTxt2ImgGenerationEvent)
    assert completed_event.s3_bucket == config.s3_bucket_name
    assert completed_event.s3_object_key == f"{mock_request.id}.jpg"

    assert file_exists_in_s3(config.s3_bucket_name, f"{mock_request.id}.jpg")


@pytest.mark.basic
def test_e2e_smoke_dead_letter_queue(mock_request_invalid):
    config = get_config(env_file="test.env")

    send_message_to_topic(config.pulsar_broker_service_url, config.pulsar_tenant, config.pulsar_namespace,
                          Topics.REQUESTED_TXT2IMG_GENERATION.value, RequestedTxt2ImgGenerationEvent, mock_request_invalid)

    request_event: RequestedTxt2ImgGenerationEvent = read_message_from_topic(
        config.pulsar_broker_service_url,
        config.pulsar_tenant, config.pulsar_namespace,
        Topics.DLQ_REQUESTED_TXT2IMG_GENERATION.value,
        RequestedTxt2ImgGenerationEvent)
    assert request_event.id == mock_request_invalid.id
