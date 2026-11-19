"""第 16 题 · 给测试搭环境。

把四个 fixture 的 raise NotImplementedError 换成你的实现，然后：

    pytest tests/test_m08.py -k p16 -v

评测会用你的 fixture 跑两个写好的测试文件 m08_testing/_p16_consumer_a.py 和 _p16_consumer_b.py
（不要改它们）。想直接看那两个文件的运行结果：

    pytest m08_testing/_p16_consumer_a.py m08_testing/_p16_consumer_b.py -p m08_testing.p16_fixtures_exercise -v

要求（详见题目页面）：
    1. leaderboard：整个测试运行只开一个排行榜服务（第 5 题的 running_server），全部测完再关
    2. server：每个测试开始前，把服务的状态恢复成刚启动的样子，然后返回这个服务
    3. app_env：设置 API_KEY、API_BASE_URL、TIMEOUT、RETRIES 四个环境变量，服务端也设上同一个密钥；
       测试结束后环境变量恢复原样
    4. client：按环境变量创建第 12 题的 APIClient 交给测试，测试结束后关掉，测试失败了也要关

需要什么参数（别的 fixture、pytest 自带的 fixture），就在函数的参数里写上它的名字。
"""

from __future__ import annotations

import os  # noqa: F401
from collections.abc import Iterator  # noqa: F401

import pytest

from m05_http.server import Running, ServerState, running_server  # noqa: F401
from m06_config.p10_settings_solution import load_settings  # noqa: F401
from m07_client.p12_client_solution import APIClient  # noqa: F401

API_KEY = "sk-p16-test"


@pytest.fixture
def leaderboard():
    """要求 1。"""
    raise NotImplementedError("请完成要求 1")


@pytest.fixture
def server():
    """要求 2。"""
    raise NotImplementedError("请完成要求 2")


@pytest.fixture
def app_env():
    """要求 3。"""
    raise NotImplementedError("请完成要求 3")


@pytest.fixture
def client():
    """要求 4。"""
    raise NotImplementedError("请完成要求 4")
