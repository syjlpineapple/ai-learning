"""第 6 题 · 查询排行榜。

把 raise NotImplementedError 换成你的实现，然后：

    pytest tests/test_m05.py -k p06 -v

想先看看服务长什么样，开一个终端：

    python -m m05_http.server

再在浏览器里打开 http://127.0.0.1:8765/scores?limit=3
"""

from __future__ import annotations

from typing import Any


def fetch_scores(base_url: str, player: str | None = None, limit: int = 10,
                 timeout: float = 5) -> list[dict[str, Any]]:
    """GET {base_url}/scores，返回成绩列表。

    player 为 None 时不传这个参数；limit 总是要传。
    请求失败、状态码不是 2xx、正文不是 JSON 数组，都要抛异常（用 requests 自己的异常就行）。
    """
    raise NotImplementedError("请完成第 6 题")
