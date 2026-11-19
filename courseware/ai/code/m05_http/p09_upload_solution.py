"""第 9 题 · 参考答案。"""

from __future__ import annotations

import uuid
from typing import Any

import requests

from m05_http.p08_retry_solution import with_retry


def upload_score(base_url: str, player: str, attempts: int, key: str | None = None,
                 timeout: float = 5) -> dict[str, Any]:
    headers = {"Idempotency-Key": key} if key is not None else {}
    response = requests.post(
        f"{base_url}/scores",
        json={"player": player, "attempts": attempts},   # json= 才会发 JSON；data= 发的是表单
        headers=headers,
        timeout=timeout,
    )
    response.raise_for_status()
    data = response.json()
    if not isinstance(data, dict):
        raise requests.exceptions.InvalidJSONError(
            f"期望 JSON 对象，实际是 {type(data).__name__}", response=response)
    return data


def upload_with_retry(base_url: str, player: str, attempts: int,
                      timeout: float = 5) -> dict[str, Any]:
    # key 在重试之前生成一次，每次重试都用同一个。
    # 写进 lambda 里的话，每次重试都会生成一个新 key，服务端就分不出这是同一条成绩了
    key = uuid.uuid4().hex
    return with_retry(lambda: upload_score(base_url, player, attempts, key=key, timeout=timeout))
