"""第 16 题的评测：用你写的 fixture 的测试（第一个文件）。不要改这个文件。

这里的测试按顺序执行，前一个测试会故意把环境弄脏，后一个检查脏东西有没有被清掉。
"""

from __future__ import annotations

import os

import pytest
import requests

from m05_http.server import SEED_SCORES, Running
from m07_client.p12_client_solution import APIClient
from m08_testing import _p16_record as record

ENV_KEYS = ("API_KEY", "API_BASE_URL", "TIMEOUT", "RETRIES")


def test_dirty_everything(server: Running, client: APIClient) -> None:
    """要求 3、4：client 连的是这个服务，带着 app_env 设的密钥。然后把服务弄脏。"""
    record.urls.append(server.base_url)
    assert os.environ.get("API_BASE_URL") == server.base_url, (
        "要求 3：环境变量 API_BASE_URL 要指向 server 这个服务")
    assert server.state.api_key == os.environ.get("API_KEY"), "要求 3：服务端也要设上同一个密钥"
    assert len(client.get_scores(limit=50)) == 7
    assert client.upload("王五", 3)["id"] == 8

    server.state.fail_plan = [503] * 5             # 弄脏：接下来的 5 次查询都返回 503


def test_state_is_fresh(server: Running) -> None:
    """要求 2：上一个测试把服务弄脏了，这个测试开始时它应该是刚启动的样子。"""
    record.urls.append(server.base_url)
    assert len(SEED_SCORES) == 7, (
        "要求 2：常量 SEED_SCORES 被改了。恢复成绩列表时要复制一份，不能直接拿它来用")
    response = requests.get(server.base_url + "/scores", params={"limit": 50}, timeout=2)
    assert response.status_code == 200, (
        f"要求 2：服务的状态没有恢复，GET /scores 返回了 {response.status_code}"
        "（503 是上一个测试的失败计划，401 是上一个测试设的密钥）")
    assert len(response.json()) == 7, (
        f"要求 2：成绩应该是最初的 7 条，实际是 {len(response.json())} 条（上一个测试上传过一条）")


def test_env_is_restored() -> None:
    """要求 3：用过 app_env 的测试结束以后，环境变量恢复原样。"""
    leaked = [name for name in ENV_KEYS if name in os.environ]
    assert leaked == [], f"要求 3：前面的测试设的环境变量 {leaked} 还在"


@pytest.mark.xfail(strict=True, reason="故意失败：看 client 会不会照样被关掉")
def test_failing_test(client: APIClient) -> None:
    assert client.get_scores(limit=1) == "这个断言故意写错"


def test_clients_closed() -> None:
    """要求 4：用过的 client 都要关掉，测试失败了也要关。"""
    assert len(record.created) == 2, f"前面两个测试应该各拿到一个 client，实际创建了 {len(record.created)} 个"
    assert record.not_closed() == [], (
        f"要求 4：有 {len(record.not_closed())} 个 client 测试结束后没有关")
