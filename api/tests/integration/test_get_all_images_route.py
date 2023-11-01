from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import pytest
from repository import DBError

from src.main import app
from tests.mocks import mock_txt2img_img_dto

client = TestClient(app)


def mock_get_all_images(limit=20, offset=0):
    return [mock_txt2img_img_dto() for _ in range(limit)]


def test_get_all_images_default(mocker):
    mocker.patch("src.main.get_all_images", mock_get_all_images)

    response = client.get("/images/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) <= 20  # default limit


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


def mock_cursor(fetchall_result):
    """Helper function to mock cursor."""
    cursor = MagicMock()
    cursor.fetchall.return_value = fetchall_result
    return cursor


def mock_connection(cursor):
    """Helper function to mock connection."""
    conn = MagicMock()
    conn.cursor.return_value = cursor
    return conn


def test_get_all_images_error():
    # Create a mock connection that simulates the context manager behavior
    mock_conn = MagicMock()
    # This simulates the `as conn` in the with statement
    mock_conn.__enter__.return_value = MagicMock()
    mock_conn.__exit__.return_value = None  # This is needed for a context manager

    # Mock the get_connection function to raise a DBError
    with patch('handlers.TrinoRepository.get_connection', return_value=mock_conn):
        with patch('handlers.TrinoRepository.get_all_images', side_effect=DBError("Mocked DB error")):
            response = client.get("/images/")

            assert response.status_code == 500
            assert response.json() == {
                "detail": "An internal error occurred. Please try again later."}
