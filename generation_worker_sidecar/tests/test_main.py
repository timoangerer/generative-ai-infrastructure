import uuid
import pulsar
import pytest
from src.main import process_requested_txt2img_generation_event
from src.topics import Topics
from src.config import Config
from src.pulsar_schemas import RequestedTxt2ImgGenerationEvent, Txt2ImgGenerationOverrideSettings, Txt2ImgGenerationSettings
from tests.pulsar_admin_utils import create_tenant_namespace_topic, delete_tenant_namespace_topic


@pytest.fixture(scope="module")
def config():
    conf = Config()

    service_url = conf.pulsar_service_url
    cluster = conf.pulsar_cluster
    namespace = conf.pulsar_namespace + "-testing"
    tenant = conf.pulsar_tenant + "-testing"
    topic_name = Topics.REQUESTED_TXT2IMG_GENERATION.value + "-testing"

    conf.pulsar_namespace = namespace
    conf.pulsar_tenant = tenant

    delete_tenant_namespace_topic(
        service_url, tenant, namespace, topic_name)

    create_tenant_namespace_topic(
        service_url, cluster, tenant, namespace, topic_name)

    yield conf

    delete_tenant_namespace_topic(
        service_url, tenant, namespace, topic_name)

# Assert the function call succeeds
# Assert a request event exists on the queue
# Assert that two events are published
# Assert an image is stored on S3


def test_e2e_process_requested_txt2img_generation_event(config: Config):

    client = pulsar.Client(config.pulsar_broker_service_url)

    event: RequestedTxt2ImgGenerationEvent = RequestedTxt2ImgGenerationEvent(
        id=str(uuid.uuid4()),
        metadata={
            "grouping": "landscapes/test1",
        },
        generation_settings={
            'prompt': "A dog",
            'negative_prompt': "",
            'styles': [],
            'seed': -1,
            'sampler_name': "",
            'batch_size': 1,
            'n_iters': 1,
            'steps': 5,
            'cfg_scale': float(7),
            'width': 512,
            'height': 512,
            "override_settings": {
                "sd_model_checkpoint": "asdf"
            }
        })

    process_requested_txt2img_generation_event(pulsar_client=client,
                                               config=config,
                                               event=event)

    client.close()


# def test_cluster_is_avaiable(config: Config):
#     url = f"{config.service_url}/admin/v2/clusters"
#     response = requests.get(url, timeout=5)
#     clusters = response.json()
#     if clusters:
#         assert isinstance(clusters, list)
#         assert len(clusters) > 0
#         assert isinstance(clusters[0], str)


# def fetch_topics(service_url, tenant, namespace):
#     url = f"{service_url}/admin/v2/persistent/{tenant}/{namespace}/partitioned"
#     response = requests.get(url)
#     return response.json()


# def is_topic_at_end_of_array_items(topic_name, topics_array):
#     for item in topics_array:
#         if item.endswith(topic_name):
#             return True
#     return False


# def test_topic_exists(config: Config):
#     service_url = config.service_url
#     tenant = config.tenant
#     namespace = config.namespace
#     topic_name = Topics.REQUESTED_TXT2IMG_GENERATION.value

#     topics_array = fetch_topics(service_url, tenant, namespace)

#     # Check if topics_array is null or empty
#     assert topics_array is not None
#     assert isinstance(topics_array, list)

#     if topics_array:
#         assert is_topic_at_end_of_array_items(topic_name, topics_array)
