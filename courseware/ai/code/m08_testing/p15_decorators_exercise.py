"""第 15 题 · 装饰器。

把两个装饰器的 raise NotImplementedError 换成你的实现，然后：

    pytest tests/test_m08.py -k p15 -v

写完以后，下面两种用法都要能工作：

    @retrying                                   # 不带括号，用默认参数
    def get_scores(...): ...

    @retrying(attempts=5, sleep=delays.append)  # 带参数
    def get_scores(...): ...

    @logged(logger)
    def upload(...): ...
"""

from __future__ import annotations

import functools  # noqa: F401  —— 要求 2 用得上
import logging
import time
from collections.abc import Callable
from typing import Any

from m05_http.p08_retry_solution import with_retry  # noqa: F401  —— 第 8 题的参考答案

Func = Callable[..., Any]


def retrying(fn: Func | None = None, *, attempts: int = 3, base_delay: float = 0.5,
             sleep: Callable[[float], None] = time.sleep) -> Any:
    """让被装饰的函数失败时按第 8 题的规则重试。见题目的要求 1、2。"""
    raise NotImplementedError("请完成要求 1-2")


def logged(logger: logging.Logger) -> Callable[[Func], Func]:
    """记录被装饰的函数的调用。见题目的要求 3。"""
    raise NotImplementedError("请完成要求 3")
