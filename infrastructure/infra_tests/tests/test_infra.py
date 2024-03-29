import requests
import time
import pytest
import os

BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:8000")


@pytest.fixture
def image_generation_data():
    return {
        "generation_settings": {
            "prompt": "A dog",
            "negative_prompt": "",
            "seed": 42,
            "sampler_name": "euler",
            "batch_size": 1,
            "n_iters": 1,
            "steps": 5,
            "cfg_scale": 7.0,
            "width": 512,
            "height": 512,
            "model": "v1-5-pruned-emaonly"
        },
        "metadata": {
            "grouping": "test/grouping"
        }
    }


def test_health_endpoint():
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_image_generation(image_generation_data):
    post_response = requests.post(
        f"{BASE_URL}/images", json=image_generation_data)
    assert post_response.status_code == 202

    request_id = str(post_response.json()["id"])
    assert request_id, "No request ID returned"

    # Polling GET /images until the image with the correct ID is found
    image_info = None
    for attempt in range(1, 6):
        time.sleep(5)
        print(f"Polling attempt {attempt}")

        get_response = requests.get(f"{BASE_URL}/images/{request_id}")
        assert get_response.status_code == 200
        image = get_response.json()

        if image.get("image_url") is not None:
            image_info = image
            break

    assert image_info, "No image was generated with the given ID"

    if image_info:
        assert image_info['metadata'] == image_generation_data['metadata'], "Metadata does not match"
        assert image_info['generation_settings'] == image_generation_data['generation_settings'], "Generation settings do not match"
    else:
        raise AssertionError("Generated image data is None")
