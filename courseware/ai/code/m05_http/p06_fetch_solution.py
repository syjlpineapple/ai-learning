"""第 6 题 · 参考答案。"""

from __future__ import annotations

from typing import Any

import requests


def fetch_scores(base_url: str, player: str | None = None, limit: int = 10,
                 timeout: float = 5) -> list[dict[str, Any]]:
    # params 的值是 None 时，requests 会直接丢掉这个参数，所以 player 不用单独判断
    params = {"player": player, "limit": limit}
    response = requests.get(f"{base_url}/scores", params=params, timeout=timeout)
    response.raise_for_status()          # 先看状态码：404 的正文是 HTML，先 json() 会报一个误导人的错
    data = response.json()
    if not isinstance(data, list):       # json() 只保证是合法 JSON，不保证是数组
        raise requests.exceptions.InvalidJSONError(
            f"期望 JSON 数组，实际是 {type(data).__name__}", response=response)
    return data
