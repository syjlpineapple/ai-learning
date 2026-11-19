"""第 11 题 · 多环境配置。

把 raise NotImplementedError 换成你的实现，然后：

    pytest tests/test_m06.py -k p11 -v

一个配置目录里可能有这些文件（都是「名字=值」格式）：

    .env                 所有环境共用，也可以在这里写 APP_ENV
    .env.development     各环境自己的（至少要有当前环境的这一个）
    .env.testing
    .env.production
    .env.local           只在你自己电脑上的真实密钥，不提交（可选）
"""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path

from dotenv import dotenv_values  # noqa: F401  —— 只读文件、不碰 os.environ

from m06_config.p10_settings_solution import ConfigError, Settings, load_settings  # noqa: F401

ENVIRONMENTS = ("development", "testing", "production")
KNOWN_KEYS = ("APP_ENV", "API_KEY", "API_BASE_URL", "TIMEOUT", "RETRIES", "DEBUG")


def merge_layers(config_dir: Path, environ: Mapping[str, str]) -> tuple[str, dict[str, str],
                                                                         dict[str, str]]:
    """按优先级合并所有来源，返回 (环境名, 合并后的值, 每个值来自哪里)。

    「来自哪里」是文件名（比如 ".env.testing"）或者 "环境变量"。
    不能修改 os.environ。
    """
    raise NotImplementedError("请完成要求 1-4")


def load_for(config_dir: Path, environ: Mapping[str, str]) -> tuple[str, Settings]:
    """合并之后交给第 10 题的 load_settings，返回 (环境名, Settings)。"""
    raise NotImplementedError("请完成要求 5")
