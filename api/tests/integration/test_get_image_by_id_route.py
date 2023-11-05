from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from models import Txt2ImgImgDTO
from src.main import app
from tests.mocks import mock_txt2img_img_dto

client = TestClient(app, raise_server_exceptions=False)


@pytest.fixture
def mock_get_image_by_id(mocker):
    # Mock the get_image_by_id function using pytest-mocker
    mock_func = mocker.patch("src.main.get_image_by_id")
    return mock_func


def test_get_image_success(mock_get_image_by_id):
    mock_image = mock_txt2img_img_dto()
    mock_get_image_by_id.return_value = mock_image

    response = client.get(f"/images/{mock_image.id}/")
    assert response.status_code == 200
    assert response.json()["id"] == str(mock_image.id)


def test_image_not_found(mock_get_image_by_id):
    test_id = uuid4()
    mock_get_image_by_id.return_value = None

    response = client.get(f"/images/{test_id}/")
    assert response.status_code == 404
    assert response.json() == {"detail": "Image not found"}


def test_invalid_uuid_format():
    response = client.get("/images/not-a-uuid/")
    assert response.status_code == 422


def test_unexpected_error(mock_get_image_by_id):
    test_id = uuid4()
    mock_get_image_by_id.side_effect = Exception("Unexpected error")

    response = client.get(f"/images/{test_id}/")
    assert response.status_code == 500


def test_response_model_validation(mock_get_image_by_id):
    test_id = uuid4()
    mock_get_image_by_id.return_value = mock_txt2img_img_dto()

    response = client.get(f"/images/{test_id}/")
    assert response.status_code == 200
    assert isinstance(Txt2ImgImgDTO(**response.json()), Txt2ImgImgDTO)
