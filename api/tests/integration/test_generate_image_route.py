import pytest
from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app, raise_server_exceptions=False)


test_data = [
    # All fields are present and valid
    ({
        "metadata": {"key1": "value1"},
        "generation_settings": {
            "prompt": "test prompt 1",
            "negative_prompt": "monochrome, black and white",
            "sampler_name": "Euler a",
            "n_iters": 1,
            "steps": 20,
            "cfg_scale": 7.0,
            "width": 512,
            "height": 512,
            "model": "DreamShaper_6"
        }
    }, 202),
    # Only required paramters present
    ({
        "metadata": {"key1": "value1"},
        "generation_settings": {
            "prompt": "test prompt 1",
            "model": "DreamShaper_6",
            "sampler_name": "Euler a"
        }
    }, 202),
    # Prompt is missing
    ({
        "metadata": {"key1": "value1"},
        "generation_settings": {
            "negative_prompt": "monochrome, black and white",
            "seed": 1,
            "sampler_name": "Euler a",
            "n_iters": 1,
            "steps": 20,
            "cfg_scale": 7.0,
            "width": 512,
            "height": 512,
            "model": "DreamShaper_6"
        }
    }, 422),
    # model is missing
    ({
        "metadata": {"key1": "value1"},
        "generation_settings": {
            "prompt": "test prompt 1",
            "negative_prompt": "monochrome, black and white",
            "seed": 1,
            "sampler_name": "Euler a",
            "n_iters": 1,
            "steps": 20,
            "cfg_scale": 7.0,
            "width": 512,
            "height": 512
        }
    }, 422),
    # sd_model_checkpoint is empty string
    ({
        "metadata": {"key1": "value1"},
        "generation_settings": {
            "prompt": "test prompt 1",
            "negative_prompt": "monochrome, black and white",
            "seed": 1,
            "sampler_name": "Euler a",
            "n_iters": 1,
            "steps": 20,
            "cfg_scale": 7.0,
            "width": 512,
            "height": 512,
            "model": {"sd_model_checkpoint": ""}
        }
    }, 422),
    # metadata is missing
    ({
        "generation_settings": {
            "prompt": "test prompt 1",
            "negative_prompt": "monochrome, black and white",
            "seed": 1,
            "sampler_name": "Euler a",
            "n_iters": 1,
            "steps": 20,
            "cfg_scale": 7.0,
            "width": 512,
            "height": 512,
            "model": "DreamShaper_6"
        }
    }, 422),
    # metadata is a string instead of a dict
    ({
        "metadata": "plain string",
        "generation_settings": {
            "prompt": "test prompt 1",
            "negative_prompt": "monochrome, black and white",
            "seed": 1,
            "sampler_name": "Euler a",
            "n_iters": 1,
            "steps": 20,
            "cfg_scale": 7.0,
            "width": 512,
            "height": 512,
            "model": "DreamShaper_6"
        }
    }, 422)
]


@pytest.mark.parametrize("payload, expected_status", test_data)
def test_generate_image_requests(mocker, payload, expected_status):
    mocker.patch("src.main.send_generation_request")

    response = client.post("/images/", json=payload)

    assert response.status_code == expected_status
