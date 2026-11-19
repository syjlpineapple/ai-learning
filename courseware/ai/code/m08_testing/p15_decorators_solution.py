"""第 15 题 · 参考答案。"""

from __future__ import annotations

import functools
import logging
import time
from collections.abc import Callable
from typing import Any

from m05_http.p08_retry_solution import with_retry

Func = Callable[..., Any]


def retrying(fn: Func | None = None, *, attempts: int = 3, base_delay: float = 0.5,
             sleep: Callable[[float], None] = time.sleep) -> Any:
    def decorate(func: Func) -> Func:
        # functools.wraps 把 func 的名字、文档、签名「搬」到 wrapper 上，
        # 并且留下 wrapper.__wrapped__ = func。pytest 就是靠它看到真正的参数列表的
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # 每次调用都重新包一层 lambda：参数是这一次调用的参数
            return with_retry(lambda: func(*args, **kwargs), attempts=attempts,
                              base_delay=base_delay, sleep=sleep)
        return wrapper

    # @retrying 不带括号：Python 直接把函数传进来，fn 就是它
    if fn is not None:
        return decorate(fn)
    # @retrying(...) 带括号：先调用 retrying(...)，返回真正的装饰器
    return decorate


def logged(logger: logging.Logger) -> Callable[[Func], Func]:
    def decorate(func: Func) -> Func:
        name = func.__qualname__

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            logger.debug("调用 %s", name)
            started = time.perf_counter()
            try:
                result = func(*args, **kwargs)
            except Exception as e:
                logger.warning("%s 失败：%s", name, type(e).__name__)
                raise                       # 原样抛出：记日志不等于处理了这个异常
            logger.debug("%s 用了 %.3f 秒", name, time.perf_counter() - started)
            return result
        return wrapper
    return decorate
