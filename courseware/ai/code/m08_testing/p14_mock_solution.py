"""第 14 题 · 参考答案。

    pytest m08_testing/p14_mock_solution.py -v
"""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock

import pytest
import requests

from m06_config.p10_settings_solution import Settings
from m08_testing.p14_target import APIClient, fake_response

E = requests.exceptions
SCORES = [{"player": "张三", "attempts": 3}]


def make_client(*responses: Any, retries: int = 2, base_url: str = "http://h/api",
                timeout: float = 4.0) -> tuple[Any, MagicMock, list[float]]:
    """真的 Session，只把 request 方法换成 Mock。responses 依次作为每次请求的结果。

    不用 MagicMock(spec=requests.Session)：spec 传类时看不到 headers 这种
    在 __init__ 里才创建的属性，APIClient 一构造就报 AttributeError。
    """
    session = requests.Session()
    session.request = MagicMock(side_effect=list(responses))  # type: ignore[method-assign]
    delays: list[float] = []
    settings = Settings(api_key="sk-test", base_url=base_url, timeout=timeout,
                        retries=retries, debug=False)
    client = APIClient(settings, session=session, sleep=delays.append)
    return client, session.request, delays


def test_get_scores_sends_timeout_and_url() -> None:
    client, request, _ = make_client(fake_response(200, SCORES))

    result = client.get_scores(limit=5)

    assert result == SCORES
    request.assert_called_once()
    method, url = request.call_args.args
    assert (method, url) == ("GET", "http://h/api/scores")          # 行为 3
    assert request.call_args.kwargs["timeout"] == 4.0                # 行为 1
    assert request.call_args.kwargs["params"] == {"player": None, "limit": 5}


def test_auth_header() -> None:
    client, _, _ = make_client()
    assert client._session.headers["Authorization"] == "Bearer sk-test"     # 行为 4


def test_server_error_raises() -> None:
    client, request, _ = make_client(*[fake_response(500, {"error": "x"})] * 3)
    with pytest.raises(E.HTTPError):                                   # 行为 2
        client.get_scores()
    assert request.call_count == 3                                     # 行为 7：retries=2，一共 3 次


def test_upload_sends_json_and_same_key() -> None:
    client, request, delays = make_client(E.ReadTimeout("回答太慢"),
                                          fake_response(201, {"id": 8}))

    assert client.upload("张三", 3) == {"id": 8}

    first, second = request.call_args_list
    assert first.kwargs["json"] == {"player": "张三", "attempts": 3}   # 行为 5
    assert "data" not in first.kwargs
    keys = [c.kwargs["headers"]["Idempotency-Key"] for c in (first, second)]
    assert keys[0] == keys[1]                                          # 行为 6
    assert delays == [0.5], "只重试了一次，等了 0.5 秒"


def test_with_does_not_swallow() -> None:
    client, _, _ = make_client()
    with pytest.raises(KeyError), client:                              # 行为 8
        raise KeyError("with 块里的 bug")
