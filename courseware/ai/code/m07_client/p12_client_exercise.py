"""第 12 题 · APIClient。

把下面的 raise NotImplementedError 换成你的实现，然后：

    pytest tests/test_m07.py -k p12 -v

前面几题写好的东西直接拿来用（都是参考答案）：
    Settings          第 10 题：api_key、base_url、timeout、retries、debug
    with_retry        第 8 题：失败了按规则重试
"""

from __future__ import annotations

import time
import uuid  # noqa: F401
from collections.abc import Callable
from types import TracebackType
from typing import Any

import requests

from m05_http.p08_retry_solution import with_retry  # noqa: F401
from m06_config.p10_settings_solution import Settings


class APIClient:
    def __init__(self, settings: Settings, session: requests.Session | None = None,
                 sleep: Callable[[float], None] = time.sleep) -> None:
        """session 不传就新建一个；测试会传一个假的进来，看你有没有关掉它。

        sleep 交给 with_retry 用。
        """
        raise NotImplementedError("请完成要求 1")

    def url_for(self, endpoint: str) -> str:
        """base_url 和 endpoint 之间正好一个 /。"""
        raise NotImplementedError("请完成要求 2")

    def get_scores(self, player: str | None = None, limit: int = 10) -> list[dict[str, Any]]:
        """GET /scores。失败了按 settings.retries 重试。"""
        raise NotImplementedError("请完成要求 3-4")

    def upload(self, player: str, attempts: int) -> dict[str, Any]:
        """POST /scores。失败了重试，同一条成绩不能存两次（第 9 题）。"""
        raise NotImplementedError("请完成要求 3-4")

    def close(self) -> None:
        raise NotImplementedError("请完成要求 5")

    def __enter__(self) -> APIClient:
        raise NotImplementedError("请完成要求 5")

    def __exit__(self, exc_type: type[BaseException] | None, exc: BaseException | None,
                 tb: TracebackType | None) -> None:
        raise NotImplementedError("请完成要求 5")

    # TODO 要求 6：__repr__
