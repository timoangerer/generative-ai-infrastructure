import time
from fastapi.testclient import TestClient
from src.main import app
from uuid import UUID

client = TestClient(app)


def test_generate_image_route():
    response = client.post(
        "/images/",
        json={
            "generation_settings": {
                "prompt": "A dog",
                "negative_prompt": "",
                "styles": [],
                "seed": -1,
                "sampler_name": "",
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
    )

    assert response.status_code == 200
    assert UUID(response.json())  # Asserting that a valid UUID is returned


def test_get_all_images_route():
    response = client.get(
        "/images/", params={"limit": 4, "offset": 0}
    )

    assert response.status_code == 200


def test_get_image_by_id_route():
    id = "9c39dd92-6606-4a96-b629-52b36fbc660a"
    response = client.get(
        f"/images/{id}"
    )

    assert response.status_code == 200


def test_generation_and_fetching():
    generation_req = {
        "generation_settings": {
            "prompt": "A dog",
            "negative_prompt": "",
            "styles": [],
            "seed": -1,
            "sampler_name": "",
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

    generation_res = client.post(
        "/images/",
        json=generation_req
    )

    assert generation_res.status_code == 200
    time.sleep(5)

    id = generation_res.json()
    response = client.get(
        f"/images/{id}"
    )
    assert response.status_code == 200

    data = response.json()

    assert data["image_url"] is not None

    assert data["metadata"] == generation_req["metadata"]
    assert data["generation_settings"] == generation_req["generation_settings"]
