"""第 14 题的被测对象：第 12 题参考答案里的 APIClient。

你写的测试要从这里导入：

    from m08_testing.p14_target import APIClient, fake_response

评测时会设置环境变量 PE_P14_MUTANT，让这里的 APIClient 变成一个故意写错的版本
（都在 _p14_mutants.py 里），看你的测试能不能发现。平时没有这个变量，就是正确的版本。
"""

from __future__ import annotations

import json
import os
from typing import Any

import requests

from m07_client.p12_client_solution import APIClient as _RealClient


def fake_response(status: int = 200, body: Any = None,
                  headers: dict[str, str] | None = None) -> requests.Response:
    """造一个真的 requests.Response 对象，不用发请求。

        fake_response(200, [{"player": "张三", "attempts": 3}])
        fake_response(503, {"error": "忙"}, {"Retry-After": "1"})

    用真的 Response 而不是 MagicMock：raise_for_status()、json() 都按真实的规则工作。
    """
    response = requests.Response()
    response.status_code = status
    response._content = json.dumps(body, ensure_ascii=False).encode("utf-8")
    response.headers.update(headers or {})
    response.url = "http://fake.invalid/"
    return response


_mutant = os.environ.get("PE_P14_MUTANT")
if _mutant:
    from m08_testing._p14_mutants import MUTANTS

    APIClient: type[_RealClient] = MUTANTS[_mutant]
else:
    APIClient = _RealClient
