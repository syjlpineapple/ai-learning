"""第 16 题评测用：在两个测试文件之间记录数据，并且记下每个 APIClient 有没有被关掉。"""

from __future__ import annotations

from typing import Any

from m07_client.p12_client_solution import APIClient

urls: list[str] = []                 # 每个测试拿到的服务地址
created: list[APIClient] = []        # 创建过的 APIClient
closed: list[APIClient] = []         # 被关掉的 APIClient

_original_init = APIClient.__init__
_original_close = APIClient.close


def _init(self: APIClient, *args: Any, **kwargs: Any) -> None:
    _original_init(self, *args, **kwargs)
    created.append(self)


def _close(self: APIClient) -> None:
    closed.append(self)
    _original_close(self)


APIClient.__init__ = _init  # type: ignore[method-assign]
APIClient.close = _close  # type: ignore[method-assign]


def not_closed() -> list[APIClient]:
    return [c for c in created if not any(c is d for d in closed)]
