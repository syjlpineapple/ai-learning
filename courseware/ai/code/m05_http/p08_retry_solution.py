"""第 8 题 · 参考答案。"""

from __future__ import annotations

import logging
import time
from collections.abc import Callable
from typing import TypeVar

import requests

from m05_http.p07_classify_solution import classify, should_retry

T = TypeVar("T")

logger = logging.getLogger(__name__)


def retry_after(exc: Exception) -> float | None:
    if not isinstance(exc, requests.exceptions.HTTPError) or exc.response is None:
        return None
    value = exc.response.headers.get("Retry-After")   # 头的值永远是字符串
    if value is None:
        return None
    try:
        seconds = float(value)
    except ValueError:
        return None          # 也可能是一个日期，比如 "Wed, 21 Oct 2026 07:28:00 GMT"，这里不处理
    return seconds if seconds >= 0 else None


def with_retry(call: Callable[[], T], attempts: int = 3, base_delay: float = 0.5,
               sleep: Callable[[float], None] = time.sleep) -> T:
    for attempt in range(1, attempts + 1):
        try:
            return call()
        except requests.exceptions.RequestException as e:
            # 不值得重试、或者已经是最后一次：原样抛出去，让调用方看到真正的那个异常
            if not should_retry(e) or attempt == attempts:
                raise
            delay = retry_after(e)
            if delay is None:
                delay = base_delay * 2 ** (attempt - 1)      # 0.5、1、2……越来越长
            logger.warning("第 %d 次失败（%s），%.1f 秒后重试", attempt, classify(e), delay)
            sleep(delay)
    # attempts < 1 时一次都不会调用；走到这里说明参数不对
    raise ValueError(f"attempts 至少是 1，传进来的是 {attempts}")


def fetch_scores_with_retry(base_url: str, timeout: float = 5) -> list[dict[str, object]]:
    from m05_http.p06_fetch_solution import fetch_scores

    return with_retry(lambda: fetch_scores(base_url, timeout=timeout))
