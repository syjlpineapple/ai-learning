"""第 9 题 · 上传成绩。

把两个函数的 raise NotImplementedError 换成你的实现，然后：

    pytest tests/test_m05.py -k p09 -v
"""

from __future__ import annotations

import uuid  # noqa: F401  —— 要求 3 用得到：uuid.uuid4().hex 生成一个不会重复的字符串
from typing import Any

import requests  # noqa: F401

# 第 8 题的参考答案
from m05_http.p08_retry_solution import with_retry  # noqa: F401


def upload_score(base_url: str, player: str, attempts: int, key: str | None = None,
                 timeout: float = 5) -> dict[str, Any]:
    """POST {base_url}/scores，上传一条成绩，返回服务端的回答（JSON 对象）。

    key 不为 None 时，放进请求头 Idempotency-Key。
    """
    raise NotImplementedError("请完成要求 1-2")


def upload_with_retry(base_url: str, player: str, attempts: int,
                      timeout: float = 5) -> dict[str, Any]:
    """上传失败时用 with_retry 重试，并且保证同一条成绩不会被存两次。"""
    raise NotImplementedError("请完成要求 3")
