"""第 16 题 · 参考答案。"""

from __future__ import annotations

import os
from collections.abc import Iterator

import pytest

from m05_http.server import Running, ServerState, running_server
from m06_config.p10_settings_solution import load_settings
from m07_client.p12_client_solution import APIClient

API_KEY = "sk-p16-test"


@pytest.fixture(scope="session")
def leaderboard() -> Iterator[Running]:
    # 整个测试运行只开这一个。关服务要等 0.5 秒左右，每个测试开一个就每个测试多等 0.5 秒
    with running_server() as srv:
        yield srv
    # with 块结束时服务关掉：所有用到它的测试都跑完以后才走到这里


@pytest.fixture
def server(leaderboard: Running) -> Running:
    # 服务是大家共用的，上一个测试改过的状态还在。每个测试开始前恢复成刚启动的样子。
    # 不能写 leaderboard.state = ServerState()：那只是让 Running.state 指向一个新对象，
    # 服务端手里拿的还是旧的那个。要在原来的对象上改
    vars(leaderboard.state).update(vars(ServerState()))
    return leaderboard


@pytest.fixture
def app_env(server: Running, monkeypatch: pytest.MonkeyPatch) -> dict[str, str]:
    values = {"API_KEY": API_KEY, "API_BASE_URL": server.base_url,
              "TIMEOUT": "2", "RETRIES": "0"}
    for name, value in values.items():
        # monkeypatch 记下每个变量原来的样子（包括「原来没有」），测试结束后恢复
        monkeypatch.setenv(name, value)
    server.state.api_key = API_KEY        # 服务端要求同一个密钥
    return values


@pytest.fixture
def client(app_env: dict[str, str]) -> Iterator[APIClient]:
    # 和程序真正运行时一样，从环境变量读配置
    with APIClient(load_settings(os.environ)) as api:
        yield api
    # 测试失败时 pytest 照样回到这里继续执行，with 块结束就会关掉 client
