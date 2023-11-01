from config import Config
from topics import Topics
from pulsar_schemas import Txt2ImgGenerationSettings
from pulsar.schema import AvroSchema
import pulsar
import uuid
import sys
import os

# Get the current script's directory
script_dir = os.path.dirname(os.path.abspath(__file__))

# Get the parent directory (project root)
project_root = os.path.abspath(os.path.join(script_dir, os.pardir))

# Append the "src" folder to the module search path
src_dir = os.path.join(project_root, "src")
sys.path.append(src_dir)


def print_module_search_path():
    print("Module search path:")
    for path in sys.path:
        print(path)


if __name__ == '__main__':
    print_module_search_path()

    config = Config()

    broker_service_url = config.pulsar_broker_service_url
    req_topic = Topics.REQUESTED_TXT2IMG_GENERATION.value

    client = pulsar.Client(broker_service_url)

    req_producer = client.create_producer(topic=req_topic,
                                          schema=AvroSchema(Txt2ImgGenerationSettings))

    job = Txt2ImgGenerationSettings(
        id=str(uuid.uuid4()),
        prompt="A dog",
        negative_prompt="",
        styles=[],
        seed=-1,
        sampler_name="",
        batch_size=1,
        n_iters=1,
        steps=5,
        cfg_scale=float(7),
        width=512,
        height=512
    )

    req_producer.send(job)

    client.close()
