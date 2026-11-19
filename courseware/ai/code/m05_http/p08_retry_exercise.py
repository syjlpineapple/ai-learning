"""第 8 题 · 失败了就重试。

把两个函数的 raise NotImplementedError 换成你的实现，然后：

    pytest tests/test_m05.py -k p08 -v
"""

from __future__ import annotations

import time
from collections.abc import Callable
from typing import TypeVar

import requests  # noqa: F401  —— 你会用到 requests.exceptions

# 「该不该重试」直接用第 7 题的参考答案
from m05_http.p07_classify_solution import classify, should_retry  # noqa: F401

T = TypeVar("T")

# TODO 要求 4：创建这个模块的 logger


def retry_after(exc: Exception) -> float | None:
    """如果 exc 是带 Retry-After 头的 HTTPError，返回要等的秒数；否则返回 None。

    只处理「秒数」这种写法（比如 "2"）。头不存在、或者写的不是数字，都返回 None。
    """
    raise NotImplementedError("请完成要求 3")


def with_retry(call: Callable[[], T], attempts: int = 3, base_delay: float = 0.5,
               sleep: Callable[[float], None] = time.sleep) -> T:
    """调用 call()，失败了按规则重试，成功就返回 call() 的结果。见题目的要求 1-4。

    sleep 用来等待。默认就是 time.sleep；测试会换成一个只记录、不真等的函数。
    """
    raise NotImplementedError("请完成要求 1-4")


def fetch_scores_with_retry(base_url: str, timeout: float = 5) -> list[dict[str, object]]:
    """组合起来用：第 6 题的 fetch_scores 加上重试。这个函数已经写好了，不用改。"""
    from m05_http.p06_fetch_solution import fetch_scores

    return with_retry(lambda: fetch_scores(base_url, timeout=timeout))
