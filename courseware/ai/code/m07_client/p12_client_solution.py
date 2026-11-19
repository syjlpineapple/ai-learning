"""第 12 题 · 参考答案。"""

from __future__ import annotations

import time
import uuid
from collections.abc import Callable
from types import TracebackType
from typing import Any

import requests

from m05_http.p08_retry_solution import with_retry
from m06_config.p10_settings_solution import Settings


class APIClient:
    def __init__(self, settings: Settings, session: requests.Session | None = None,
                 sleep: Callable[[float], None] = time.sleep) -> None:
        self.settings = settings
        self._sleep = sleep
        # Session 只建这一次：同一条 TCP 连接、同一套请求头，后面每个请求都复用
        self._session = session if session is not None else requests.Session()
        self._session.headers.update({
            "Authorization": f"Bearer {settings.api_key}",
            "Accept": "application/json",
        })

    def url_for(self, endpoint: str) -> str:
        # 不用 urllib.parse.urljoin：base_url 带路径（.../api/v1）时它会把最后一段丢掉
        return f"{self.settings.base_url.rstrip('/')}/{endpoint.lstrip('/')}"

    def _request(self, method: str, endpoint: str, **kwargs: Any) -> Any:
        # Session 没有「默认超时」：session.timeout = 5 这种写法不会报错，也不会生效。
        # 每个请求都要自己带上 timeout
        response = self._session.request(method, self.url_for(endpoint),
                                         timeout=self.settings.timeout, **kwargs)
        response.raise_for_status()
        return response.json()

    def _with_retry(self, call: Callable[[], Any]) -> Any:
        return with_retry(call, attempts=self.settings.retries + 1, sleep=self._sleep)

    def get_scores(self, player: str | None = None, limit: int = 10) -> list[dict[str, Any]]:
        params = {"player": player, "limit": limit}
        data = self._with_retry(lambda: self._request("GET", "/scores", params=params))
        if not isinstance(data, list):
            raise requests.exceptions.InvalidJSONError(
                f"期望 JSON 数组，实际是 {type(data).__name__}")
        return data

    def upload(self, player: str, attempts: int) -> dict[str, Any]:
        key = uuid.uuid4().hex                       # 重试之前生成一次（第 9 题）
        data = self._with_retry(lambda: self._request(
            "POST", "/scores", json={"player": player, "attempts": attempts},
            headers={"Idempotency-Key": key}))
        if not isinstance(data, dict):
            raise requests.exceptions.InvalidJSONError(
                f"期望 JSON 对象，实际是 {type(data).__name__}")
        return data

    def close(self) -> None:
        self._session.close()

    def __enter__(self) -> APIClient:
        return self

    def __exit__(self, exc_type: type[BaseException] | None, exc: BaseException | None,
                 tb: TracebackType | None) -> None:
        # 返回 None（也就是假）：with 块里的异常照常抛出去。返回 True 会把它吞掉
        self.close()

    def __repr__(self) -> str:
        # settings 的 repr 已经不含密钥（第 10 题），但不要把 session.headers 放进来：
        # 里面有完整的 Authorization 头
        return f"APIClient(base_url={self.settings.base_url!r}, timeout={self.settings.timeout})"
