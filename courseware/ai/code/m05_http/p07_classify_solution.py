"""第 7 题 · 参考答案。"""

from __future__ import annotations

import requests

E = requests.exceptions

RETRYABLE: dict[str, bool] = {
    "unreachable": True,
    "slow": True,
    "rate_limited": True,
    "server_error": True,
    "client_error": False,
    "bad_response": False,
    "bad_url": False,
}


def classify(exc: Exception) -> str:
    # 顺序就是答案：每一个多重继承的异常，都要在它的任何一个父类之前判断。
    #   ConnectTimeout  同时是 ConnectionError 和 Timeout       → 先于 Timeout 判断
    #   JSONDecodeError 同时是 RequestException 和 ValueError   → 用 InvalidJSONError 精确判断
    #   MissingSchema / InvalidSchema / InvalidURL 也都是 ValueError → 不能用 ValueError 判断「回应格式不对」
    if isinstance(exc, E.ConnectionError):          # 包括 ConnectTimeout
        return "unreachable"
    if isinstance(exc, E.Timeout):                  # 走到这里只剩 ReadTimeout
        return "slow"
    if isinstance(exc, E.HTTPError):
        status = exc.response.status_code if exc.response is not None else None
        if status == 429:
            return "rate_limited"
        if status is not None and 400 <= status < 500:
            return "client_error"
        return "server_error"                       # 5xx，或者拿不到状态码
    if isinstance(exc, E.InvalidJSONError):         # 包括 JSONDecodeError
        return "bad_response"
    if isinstance(exc, (E.MissingSchema, E.InvalidSchema, E.InvalidURL)):
        return "bad_url"
    raise exc                                       # 不认识的异常不要硬归类


def should_retry(exc: Exception) -> bool:
    return RETRYABLE[classify(exc)]
