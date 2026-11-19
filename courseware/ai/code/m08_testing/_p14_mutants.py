"""第 14 题的「故意写错的版本」。每个都只改了一处，你的测试要把它们全部抓出来。

先别看。做完了、或者某一个死活抓不住时再来对照。
"""

from __future__ import annotations

import uuid
from types import TracebackType
from typing import Any

from m05_http.p08_retry_solution import with_retry
from m07_client.p12_client_solution import APIClient


class NoTimeout(APIClient):
    """请求没有带 timeout。"""

    def _request(self, method: str, endpoint: str, **kwargs: Any) -> Any:
        response = self._session.request(method, self.url_for(endpoint), **kwargs)
        response.raise_for_status()
        return response.json()


class NoRaiseForStatus(APIClient):
    """没有检查状态码，500 也当成功。"""

    def _request(self, method: str, endpoint: str, **kwargs: Any) -> Any:
        response = self._session.request(method, self.url_for(endpoint),
                                         timeout=self.settings.timeout, **kwargs)
        return response.json()


class DoubleSlash(APIClient):
    """endpoint 开头的 / 没有去掉，拼出 http://h//scores。"""

    def url_for(self, endpoint: str) -> str:
        return f"{self.settings.base_url.rstrip('/')}/{endpoint}"


class NoAuth(APIClient):
    """忘了设 Authorization 头。"""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._session.headers.pop("Authorization", None)


class FormUpload(APIClient):
    """上传时用了 data=，发出去的是表单。"""

    def upload(self, player: str, attempts: int) -> dict[str, Any]:
        key = uuid.uuid4().hex
        data: dict[str, Any] = self._with_retry(lambda: self._request(
            "POST", "/scores", data={"player": player, "attempts": attempts},
            headers={"Idempotency-Key": key}))
        return data


class NewKeyEachRetry(APIClient):
    """每次重试都生成新的 Idempotency-Key（第 9 题坑 3）。"""

    def upload(self, player: str, attempts: int) -> dict[str, Any]:
        data: dict[str, Any] = self._with_retry(lambda: self._request(
            "POST", "/scores", json={"player": player, "attempts": attempts},
            headers={"Idempotency-Key": uuid.uuid4().hex}))
        return data


class RetriesOffByOne(APIClient):
    """retries=2 时只请求了 2 次（应该是 3 次）。"""

    def _with_retry(self, call: Any) -> Any:
        return with_retry(call, attempts=max(self.settings.retries, 1), sleep=self._sleep)


class ExitSwallows(APIClient):
    """__exit__ 返回 True，with 块里的异常被吞掉了。"""

    def __exit__(  # type: ignore[override]
        self, exc_type: type[BaseException] | None, exc: BaseException | None,
        tb: TracebackType | None,
    ) -> bool:
        self.close()
        return True


MUTANTS: dict[str, type[APIClient]] = {
    "no_timeout": NoTimeout,
    "no_raise_for_status": NoRaiseForStatus,
    "double_slash": DoubleSlash,
    "no_auth": NoAuth,
    "form_upload": FormUpload,
    "new_key_each_retry": NewKeyEachRetry,
    "retries_off_by_one": RetriesOffByOne,
    "exit_swallows": ExitSwallows,
}
