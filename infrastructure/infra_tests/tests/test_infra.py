import requests
import time
import pytest

BASE_URL = "http://127.0.0.1:8000"

@pytest.fixture
def image_generation_data():
    return {
        "generation_settings": {
            "prompt": "A dog",
            "negative_prompt": "",
            "styles": [],
            "seed": 42,
            "sampler_name": "asdf",
            "batch_size": 1,
            "n_iters": 1,
            "steps": 5,
            "cfg_scale": 7.0,
            "width": 512,
            "height": 512,
            "override_settings": {
                "sd_model_checkpoint": "cc6cb27"
            }
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
    post_response = requests.post(f"{BASE_URL}/images", json=image_generation_data)
    assert post_response.status_code == 200

    request_id = post_response.text.strip('"')
    assert request_id, "No request ID returned"

    # Polling GET /images until the image with the correct ID is found
    image_info = None
    for attempt in range(1, 3):
        time.sleep(8)
        print(f"Polling attempt {attempt}")
        
        get_response = requests.get(f"{BASE_URL}/images")
        assert get_response.status_code == 200
        images = get_response.json()

        image_info = next((img for img in images if img.get('id') == request_id and img.get("image_url") is not None), None)
        if image_info:
            break

    assert image_info, "No image was generated with the given ID"

    if image_info:
        assert image_info['metadata'] == image_generation_data['metadata'], "Metadata does not match"
        assert image_info['generation_settings'] == image_generation_data['generation_settings'], "Generation settings do not match"
    else:
        raise AssertionError("Generated image data is None")
