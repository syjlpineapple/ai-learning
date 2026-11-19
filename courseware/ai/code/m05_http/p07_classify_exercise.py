"""第 7 题 · 失败分类。

把 raise NotImplementedError 换成你的实现，然后：

    pytest tests/test_m05.py -k p07 -v
"""

from __future__ import annotations

# 七种失败，以及每一种值不值得重试
RETRYABLE: dict[str, bool] = {
    "unreachable": True,     # 连不上服务器（包括连接阶段就超时）
    "slow": True,            # 连上了，但等回应时超时
    "rate_limited": True,    # 429：请求太频繁，等一会儿再试
    "server_error": True,    # 5xx：服务端出错
    "client_error": False,   # 其他 4xx：请求本身有问题，重试也一样
    "bad_response": False,   # 回应不是期望的 JSON（JSONDecodeError、InvalidJSONError）
    "bad_url": False,        # URL 写错了（MissingSchema、InvalidSchema、InvalidURL）
}


def classify(exc: Exception) -> str:
    """把 requests 抛出的异常归到 RETRYABLE 的某一类，返回类别名。

    不是 requests 的异常（比如 KeyError），不要归类，原样抛出去。
    """
    raise NotImplementedError("请完成第 7 题")


def should_retry(exc: Exception) -> bool:
    """这个异常值不值得重试。"""
    raise NotImplementedError("请完成第 7 题")
