from unittest.mock import MagicMock

import pytest
import requests

from tests.dailypractice.Day22.api_client import APIClient


@pytest.fixture
def api_client():
     client = APIClient("https://example.com","test_key")
     try:
         yield client
     finally:
         client.close()

def test_success(api_client):
     mock_response = MagicMock()
     mock_response.status_code = 200
     mock_response.json.return_value = {
          "id":1,
          "email":"abc@gmail.com",
     }
     api_client.session.post = MagicMock(return_value=mock_response)
     resp = api_client.post("/user_info",{"name":"jack"})
     assert resp.status_code == 200
     mock_response.raise_for_status.assert_called_once()
     api_client.session.post.assert_called_once_with(
         "https://example.com/user_info",
         json={"name": "jack"},
         timeout=10,
     )
     assert resp == {
          "id":1,
          "email":"abc@gmail.com"
     }


def test_post_fail(api_client):
    mock_response = MagicMock()

    mock_response.raise_for_status.side_effect = (
        requests.exceptions.HTTPError("500 Server Error")
    )

    api_client.session.post = MagicMock(
        return_value=mock_response
    )

    with pytest.raises(requests.exceptions.HTTPError):
        api_client.post("/users", {"name": "jack"})


def test_call_close(api_client):
    client = APIClient("https://example.com", "test_key")
    client.session.close = MagicMock()
    client.close()
    client.session.close.assert_called_once()