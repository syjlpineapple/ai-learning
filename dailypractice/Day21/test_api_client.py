from unittest.mock import MagicMock

import requests.exceptions

from tests.dailypractice.Day20.api_client import APIClient

"""
模拟成功
"""
def test_post_success():
    client = APIClient("https://example.com", "test_key")
    try:
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "id":1,
            "email":"abc@gmail.com"
        }

        client.session.post = MagicMock(
            return_value=mock_response
        )

        resp = client.post("/user_info",{"name":"jack"})

        assert resp == {
            "id":1,
            "email":"abc@gmail.com"
        }

        # 验证是否正确调用了 POST,
        # 校验请求地址、请求参数、timeout 是否符合预期
        client.session.post.assert_called_once_with(
            "https://example.com/user_info",
            json={"name": "jack"},
            timeout=10,
        )

        # 验证是否检查了 HTTP 状态码
        mock_response.raise_for_status.assert_called_once()
    finally:
        client.close()


"""
模拟失败
"""
def test_post_fail():
    client = APIClient("https://example.com", "test_key")
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = (
        requests.exceptions.HTTPError("500 Server Error")
    )

    client.session.post = MagicMock(
        return_value=mock_response
    )
    try:
        client.post("/users", {"name": "jack"})
        assert False, "应该抛出 HTTPError"
    except requests.exceptions.HTTPError:
        pass
    finally:
        client.close()

"""
这里这样写更好
    try:
        with pytest.raises(requests.exceptions.HTTPError):
            client.post("/users", {"name": "jack"})
    finally:
        client.close()
"""


def test_call_close():
    client = APIClient("https://example.com", "test_key")
    client.session.close = MagicMock()
    client.close()
    client.session.close.assert_called_once()
