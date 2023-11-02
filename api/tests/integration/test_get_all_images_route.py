import pytest
from fastapi.testclient import TestClient

from repository import DBError
from src.main import app
from tests.mocks import mock_txt2img_img_dto

client = TestClient(app, raise_server_exceptions=False)


def mock_get_all_images(limit=20, offset=0):
    return [mock_txt2img_img_dto() for _ in range(limit)]


def test_get_all_images_default(mocker):
    mocker.patch("src.main.get_all_images", mock_get_all_images)

    response = client.get("/images/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) <= 20  # default limit


def test_get_all_images_no_images(mocker):
    mocker.patch("src.main.get_all_images", return_value=[])

    response = client.get("/images/")

    assert response.status_code == 200
    assert response.json() == []


def test_get_all_images_custom_limit(mocker):
    custom_limit = 10
    mocker.patch("src.main.get_all_images", mock_get_all_images)

    response = client.get(f"/images/?limit={custom_limit}")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) == custom_limit


def test_get_all_images_offset(mocker):
    mocker.patch("src.main.get_all_images", mock_get_all_images)

    response1 = client.get("/images/?limit=5")
    response2 = client.get("/images/?limit=5&offset=5")

    assert response1.status_code == 200
    assert response2.status_code == 200

    # Ensure that data is different because of the offset
    assert response1.json() != response2.json()


def test_get_all_images_generic_exception(mocker):
    mocker.patch("src.main.get_all_images",
                 side_effect=Exception("Unexpected error"))
    response = client.get("/images/")

    assert response.status_code == 500
    assert response.json().get(
        "detail") == "An unexpected error occurred. Please try again later."


def test_get_all_images_db_exception(mocker):
    mocker.patch("src.main.get_all_images",
                 side_effect=DBError("Mocked DB error"))
    response = client.get("/images/")

    assert response.status_code == 500
    assert response.json().get(
        "detail") == "An internal error occurred. Please try again later."


@pytest.mark.parametrize(
    "limit,offset",
    [
        ("-1", "0"),     # negative limit
        ("1", "-1"),     # negative offset
        ("0", "-1"),     # zero limit
        ("notanint", "0"),  # non-integer limit
        ("1", "notanint"),  # non-integer offset
        ("999999999999999999999999999", "0"),   # extremely large limit
        ("@", "0"),     # special character in limit
        ("0", "@"),     # special character in offset
    ]
)
def test_get_all_images_invalid_params(mocker, limit, offset):
    mocker.patch("src.main.get_all_images", mock_get_all_images)

    response = client.get(f"/images/?limit={limit}&offset={offset}")
    assert response.status_code == 422  # Expecting a validation error
