import uuid
import requests
from PIL import Image
import io
from src.utils import convert_record_to_json
from src.pulsar_schemas import Txt2ImgGenerationSettings
from src.sd_generation import generate_txt2img
from src.config import Config


def test_server_is_available():
    config = Config()
    response = requests.get(f'{config.sd_server_url}/sdapi/v1/memory')
    assert response.status_code == 200


def test_generate_images():
    config = Config()

    payload = {
        "prompt": "puppy dog",
        "steps": 5
    }

    image = generate_txt2img(payload, config.sd_server_url)

    # Assert that the returned image is a valid PIL image
    assert isinstance(image, Image.Image)

    # Assert that the image can be opened and read as bytes
    with io.BytesIO() as output:
        image.save(output, format="PNG")
        assert output.getvalue()


def test_generate_images_with_class():
    config = Config()

    payload = Txt2ImgGenerationSettings(
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

    json_payload = convert_record_to_json(
        Txt2ImgGenerationSettings, payload)

    image = generate_txt2img(json_payload, config.sd_server_url)

    # Assert that the returned image is a valid PIL image
    assert isinstance(image, Image.Image)

    # Assert that the image can be opened and read as bytes
    with io.BytesIO() as output:
        image.save(output, format="PNG")
        assert output.getvalue()
