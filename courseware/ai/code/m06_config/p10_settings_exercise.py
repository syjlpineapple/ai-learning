"""第 10 题 · 读配置。

把 raise NotImplementedError 换成你的实现，然后：

    pytest tests/test_m06.py -k p10 -v

load_settings 不直接读 os.environ，而是接收一个「名字 → 字符串」的映射。
平时调用 load_settings(os.environ)；测试传一个普通字典，不用真的去改环境变量。
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass


class ConfigError(ValueError):
    """配置不对。消息里列出所有问题，而不是只说第一个。"""


@dataclass(frozen=True)
class Settings:
    api_key: str        # TODO 要求 5：打印 Settings 时不能出现密钥（提示：dataclasses.field）
    base_url: str
    timeout: float
    retries: int
    debug: bool


def load_settings(environ: Mapping[str, str]) -> Settings:
    """从 environ 读配置，见题目的要求 1-5。"""
    raise NotImplementedError("请完成第 10 题")
