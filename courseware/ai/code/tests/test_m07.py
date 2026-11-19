"""M7 每日一题的测试。请求都发给本机的排行榜服务（m05_http/server.py）。

    pytest tests/test_m07.py -k p12 -v
"""

from __future__ import annotations

import logging
import os
import subprocess
import sys
import time
from collections.abc import Callable, Iterator
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest
import requests

from m05_http.server import Running, running_server
from m06_config.p10_settings_solution import Settings
from m07_client import (
    p12_client_exercise,
    p12_client_solution,
    p13_main_exercise,
    p13_main_solution,
)

CODE_DIR = Path(__file__).resolve().parents[1]

E = requests.exceptions
SECRET = "sk-test-0123456789abcdef"


def run_or_skip(fn: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
    try:
        return fn(*args, **kwargs)
    except NotImplementedError:
        pytest.skip(f"{getattr(fn, '__name__', fn)} 还没完成")


@pytest.fixture
def server() -> Iterator[Running]:
    with running_server() as srv:
        srv.state.api_key = SECRET           # /scores 要求带 Authorization
        yield srv


class Recorder:
    def __init__(self) -> None:
        self.delays: list[float] = []

    def __call__(self, seconds: float) -> None:
        self.delays.append(seconds)


class TrackingSession(requests.Session):
    """真的 Session，只是记下 close 被调用了几次。"""

    def __init__(self) -> None:
        super().__init__()
        self.closed = 0

    def close(self) -> None:
        self.closed += 1
        super().close()


def settings_for(srv: Running, **overrides: Any) -> Settings:
    values: dict[str, Any] = {"api_key": SECRET, "base_url": srv.base_url, "timeout": 5.0,
                              "retries": 2, "debug": False}
    values.update(overrides)
    return Settings(**values)


# ============================================================================
# 第 12 题 · APIClient
# ============================================================================

P12 = {"exercise": p12_client_exercise, "solution": p12_client_solution}


@pytest.fixture(params=list(P12))
def p12(request: pytest.FixtureRequest) -> ModuleType:
    return P12[request.param]


def make(p12: ModuleType, settings: Settings, **kwargs: Any) -> Any:
    return run_or_skip(p12.APIClient, settings, **kwargs)


def test_p12_get_scores(p12: ModuleType, server: Running) -> None:
    client = make(p12, settings_for(server))
    assert client.get_scores(limit=2) == [{"player": "100%", "attempts": 1},
                                          {"player": "张三", "attempts": 2}]
    assert client.get_scores(player="A&B") == [{"player": "A&B", "attempts": 4}]
    client.close()


def test_p12_auth_header(p12: ModuleType, server: Running) -> None:
    """要求 1：每个请求都带上 Authorization: Bearer <api_key>。密钥不对是 401，不重试。"""
    sleep = Recorder()
    client = make(p12, settings_for(server, api_key="wrong-key"), sleep=sleep)
    with pytest.raises(E.HTTPError) as excinfo:
        client.get_scores()
    assert excinfo.value.response is not None and excinfo.value.response.status_code == 401
    assert sleep.delays == [], "401 不值得重试"
    client.close()


def test_p12_reuses_connection(p12: ModuleType, server: Running) -> None:
    """要求 1：一个客户端只用一个 Session，连续的请求走同一条 TCP 连接。"""
    client = make(p12, settings_for(server))
    for _ in range(3):
        client.get_scores(limit=1)
    ports = server.state.client_ports[-3:]
    assert len(set(ports)) == 1, (
        f"3 个请求用了 {len(set(ports))} 条连接（客户端端口 {ports}）—— Session 是不是每次都新建？")
    client.close()


@pytest.mark.parametrize(("base", "endpoint"), [
    ("http://h/api/v1", "scores"), ("http://h/api/v1/", "scores"),
    ("http://h/api/v1", "/scores"), ("http://h/api/v1//", "//scores")])
def test_p12_url_for(p12: ModuleType, base: str, endpoint: str) -> None:
    """要求 2：base_url 带路径时也不能丢掉一段，也不能出现 //。"""
    client = make(p12, Settings(api_key="k", base_url=base, timeout=1.0, retries=0, debug=False))
    assert client.url_for(endpoint) == "http://h/api/v1/scores"
    client.close()


def test_p12_uses_timeout(p12: ModuleType, server: Running) -> None:
    """要求 3：settings.timeout 要真的用上。服务端拖 2 秒，timeout=0.5，不重试，应该很快失败。"""
    server.state.fail_plan = ["slow"]
    client = make(p12, settings_for(server, timeout=0.5, retries=0))
    started = time.perf_counter()
    try:
        client.get_scores()
    except E.Timeout:
        assert time.perf_counter() - started < 1.5
    else:
        pytest.fail("服务端拖了 2 秒，timeout=0.5 却成功了 —— session.timeout = ... 这种写法不起作用，"
                    "每个请求要自己传 timeout")
    finally:
        client.close()


def test_p12_retries(p12: ModuleType, server: Running) -> None:
    """要求 4：retries=2 表示失败后最多再试 2 次，一共 3 次。"""
    server.state.fail_plan = [503] * 5
    sleep = Recorder()
    client = make(p12, settings_for(server, retries=2), sleep=sleep)
    with pytest.raises(E.HTTPError):
        client.get_scores()
    assert server.state.scores_gets == 3 and sleep.delays == [0.5, 1.0]
    client.close()


def test_p12_upload_no_duplicates(p12: ModuleType, server: Running) -> None:
    """要求 4：上传时第一次回答超时、成绩其实已经存好了，重试之后服务端只能有一条。"""
    server.state.slow_posts = 1
    client = make(p12, settings_for(server, timeout=0.5))
    row = client.upload("赵六", 5)
    assert row["player"] == "赵六"
    assert [r for r in server.state.scores if r["player"] == "赵六"] == \
        [{"player": "赵六", "attempts": 5}]
    client.close()


def test_p12_with_closes_session(p12: ModuleType, server: Running) -> None:
    """要求 5：with 块结束时关掉 Session。"""
    session = TrackingSession()
    client = make(p12, settings_for(server), session=session)
    with client as c:
        assert c is client, "__enter__ 要返回客户端自己"
        c.get_scores(limit=1)
    assert session.closed == 1


def test_p12_with_does_not_swallow(p12: ModuleType, server: Running) -> None:
    """要求 5：with 块里出了错，Session 照样关掉，异常照样抛出来。"""
    session = TrackingSession()
    client = make(p12, settings_for(server), session=session)
    with pytest.raises(KeyError), client:
        raise KeyError("with 块里的 bug")
    assert session.closed == 1


def test_p12_repr_has_no_secret(p12: ModuleType, server: Running) -> None:
    """要求 6：打印客户端时看得到地址，看不到密钥。"""
    client = make(p12, settings_for(server))
    text = repr(client)
    client.close()
    assert SECRET not in text, f"密钥出现在了 {text!r} 里"
    assert server.base_url in text, f"repr 里应该有 base_url，方便排查：{text!r}"
    assert "object at 0x" not in text, "要自己写 __repr__"


# --- 讲评里的实测结论 --------------------------------------------------------


def test_p12_review_urljoin_drops_segment() -> None:
    from urllib.parse import urljoin

    assert urljoin("https://x.com/api", "scores") == "https://x.com/scores"
    assert urljoin("https://x.com/api/", "/scores") == "https://x.com/scores"
    assert urljoin("https://x.com/api/", "scores") == "https://x.com/api/scores"


def test_p12_review_rstrip_is_a_set() -> None:
    assert "https://x.com/v1".rstrip("/v1") == "https://x.com"
    assert "abc".rstrip("cb") == "a"


def test_p12_review_session_timeout_attribute_ignored(server: Running) -> None:
    session = requests.Session()
    session.timeout = 0.5  # type: ignore[attr-defined]
    started = time.perf_counter()
    assert session.get(server.base_url + "/slow?seconds=1").status_code == 200
    assert time.perf_counter() - started >= 0.9, "session.timeout 没有任何作用"
    session.close()


def test_p12_review_connection_reuse(server: Running) -> None:
    for _ in range(3):
        requests.get(server.base_url + "/echo", timeout=5)
    plain = server.state.client_ports[-3:]
    with requests.Session() as session:
        for _ in range(3):
            session.get(server.base_url + "/echo", timeout=5)
    reused = server.state.client_ports[-3:]
    assert len(set(plain)) == 3 and len(set(reused)) == 1


def test_p12_review_headers_contain_secret() -> None:
    with requests.Session() as session:
        session.headers["Authorization"] = f"Bearer {SECRET}"
        assert SECRET in str(session.headers)


def test_p12_review_exit_true_swallows() -> None:
    class Swallow:
        def __enter__(self) -> Swallow:
            return self

        def __exit__(self, *exc: object) -> bool:
            return True

    def use() -> str:
        with Swallow():
            raise ValueError("请求失败")
        return "with 后面的代码照常执行"

    assert use() == "with 后面的代码照常执行"


# ============================================================================
# 第 13 题 · 程序入口
# ============================================================================

P13 = {"exercise": p13_main_exercise, "solution": p13_main_solution}


@pytest.fixture(params=list(P13))
def p13(request: pytest.FixtureRequest) -> ModuleType:
    return P13[request.param]


class Factory:
    """代替 APIClient 类传给 main：记下建了几个客户端，Session 有没有被关掉。"""

    def __init__(self, broken: bool = False) -> None:
        self.sessions: list[TrackingSession] = []
        self.broken = broken

    def __call__(self, settings: Settings) -> p12_client_solution.APIClient:
        session = TrackingSession()
        self.sessions.append(session)
        client = p12_client_solution.APIClient(settings, session=session, sleep=Recorder())
        if self.broken:
            def bug(*_args: object) -> object:
                empty: dict[str, int] = {}
                return empty["程序自己的 bug"]
            client.get_scores = bug  # type: ignore[method-assign, assignment]
        return client


def run_main(p13: ModuleType, argv: list[str], environ: dict[str, str],
             factory: Factory, capsys: pytest.CaptureFixture[str],
             caplog: pytest.LogCaptureFixture) -> tuple[int, str, str]:
    caplog.set_level(logging.INFO, logger=p13.__name__)
    code = run_or_skip(p13.main, argv, environ, p13_main_solution.CONFIG_DIR, factory)
    out = capsys.readouterr()
    return code, out.out, out.err


def dev_environ(srv: Running, **extra: str) -> dict[str, str]:
    return {"APP_ENV": "development", "API_BASE_URL": srv.base_url, "API_KEY": SECRET, **extra}


def test_p13_scores(p13: ModuleType, server: Running, capsys: pytest.CaptureFixture[str],
                    caplog: pytest.LogCaptureFixture) -> None:
    factory = Factory()
    code, out, _ = run_main(p13, ["scores", "张三"], dev_environ(server), factory, capsys, caplog)
    assert code == 0
    assert out.splitlines() == [" 1. 张三  2 次", " 2. 张三  5 次"]
    assert [s.closed for s in factory.sessions] == [1], "用完要关掉客户端"


def test_p13_no_scores(p13: ModuleType, server: Running, capsys: pytest.CaptureFixture[str],
                       caplog: pytest.LogCaptureFixture) -> None:
    code, out, _ = run_main(p13, ["scores", "没有这个人"], dev_environ(server), Factory(),
                            capsys, caplog)
    assert (code, out.strip()) == (0, "（还没有成绩）")


def test_p13_upload(p13: ModuleType, server: Running, capsys: pytest.CaptureFixture[str],
                    caplog: pytest.LogCaptureFixture) -> None:
    code, out, _ = run_main(p13, ["upload", "王五", "4"], dev_environ(server), Factory(),
                            capsys, caplog)
    assert (code, out.strip()) == (0, "已上传：第 8 条")


@pytest.mark.parametrize("argv", [[], ["scores", "a", "b"], ["upload", "王五"],
                                  ["upload", "王五", "四"], ["delete"]],
                         ids=["empty", "too_many", "missing", "not_int", "unknown"])
def test_p13_bad_arguments(p13: ModuleType, server: Running, argv: list[str],
                           capsys: pytest.CaptureFixture[str],
                           caplog: pytest.LogCaptureFixture) -> None:
    """要求 1：命令行不对，退出码 2，标准错误里打印用法，不发任何请求。"""
    factory = Factory()
    code, out, err = run_main(p13, argv, dev_environ(server), factory, capsys, caplog)
    assert code == 2
    assert p13_main_solution.USAGE in err and out == ""
    assert factory.sessions == [], "命令行都不对，就不该建客户端"


@pytest.mark.parametrize("extra", [{"APP_ENV": "staging"}, {"APP_ENV": "production",
                                                             "DEBUG": "1"},
                                   {"TIMEOUT": "ten"}], ids=["bad_env", "prod_debug", "bad_timeout"])
def test_p13_config_error(p13: ModuleType, server: Running, extra: dict[str, str],
                          capsys: pytest.CaptureFixture[str],
                          caplog: pytest.LogCaptureFixture) -> None:
    """要求 2：配置不对，退出码 2，记一条 ERROR 写明原因，不带 traceback，不建客户端。"""
    factory = Factory()
    code, out, _ = run_main(p13, ["scores"], dev_environ(server, **extra), factory, capsys, caplog)
    assert code == 2 and out == "" and factory.sessions == []
    errors = [r for r in caplog.records if r.levelno == logging.ERROR]
    assert len(errors) == 1, f"应该记一条 ERROR：{[r.getMessage() for r in caplog.records]}"
    assert errors[0].exc_info is None, "配置错误是预料之中的，说清楚原因就够了，不要 traceback"


def test_p13_network_error(p13: ModuleType, capsys: pytest.CaptureFixture[str],
                           caplog: pytest.LogCaptureFixture) -> None:
    """要求 4：连不上服务，退出码 3，日志写出是哪一类问题，客户端照样关掉。"""
    with running_server() as srv:
        dead = dev_environ(srv, RETRIES="0")
    factory = Factory()
    code, out, _ = run_main(p13, ["scores"], dead, factory, capsys, caplog)
    assert code == 3 and out == ""
    assert [s.closed for s in factory.sessions] == [1]
    text = "\n".join(r.getMessage() for r in caplog.records if r.levelno == logging.ERROR)
    assert "unreachable" in text, f"日志要写出是哪一类问题（第 7 题的 classify）：{text!r}"


def test_p13_wrong_key(p13: ModuleType, server: Running, capsys: pytest.CaptureFixture[str],
                       caplog: pytest.LogCaptureFixture) -> None:
    code, _, _ = run_main(p13, ["scores"], dev_environ(server, API_KEY="wrong"), Factory(),
                          capsys, caplog)
    assert code == 3
    assert "client_error" in caplog.text


def test_p13_bug(p13: ModuleType, server: Running, capsys: pytest.CaptureFixture[str],
                 caplog: pytest.LogCaptureFixture) -> None:
    """要求 5：程序自己的 bug（这里是 KeyError），退出码 1，记完整的 traceback，客户端照样关掉。"""
    factory = Factory(broken=True)
    code, out, _ = run_main(p13, ["scores"], dev_environ(server), factory, capsys, caplog)
    assert code == 1 and out == ""
    assert [s.closed for s in factory.sessions] == [1]
    with_tb = [r for r in caplog.records if r.exc_info is not None]
    assert with_tb and with_tb[0].exc_info is not None and with_tb[0].exc_info[0] is KeyError, (
        "bug 要用 logger.exception 记下完整的 traceback")


def test_p13_run_as_script(server: Running) -> None:
    """参考答案真的当作程序跑一遍：结果在标准输出，日志在标准错误，退出码正确。"""
    env = {**os.environ, "PYTHONUTF8": "1", "APP_ENV": "development",
           "API_BASE_URL": server.base_url, "API_KEY": SECRET}
    ok = subprocess.run([sys.executable, "-m", "m07_client.p13_main_solution", "scores", "李四"],
                        cwd=CODE_DIR, capture_output=True, text=True, encoding="utf-8", env=env,
                        check=False)
    assert ok.returncode == 0 and ok.stdout.strip() == "1. 李四  3 次"
    # 用 -m 运行时，入口模块的 __name__ 是 "__main__"（第 3.1 章），logger 的名字也跟着变
    assert "INFO __main__: 环境 development" in ok.stderr
    bad = subprocess.run([sys.executable, "-m", "m07_client.p13_main_solution", "delete"],
                         cwd=CODE_DIR, capture_output=True, text=True, encoding="utf-8", env=env,
                         check=False)
    assert bad.returncode == 2 and bad.stdout == ""


# --- 讲评里的实测结论 --------------------------------------------------------


def test_p13_review_finally_with_none() -> None:
    done = subprocess.run([sys.executable, "-c",
                           "client = None\ntry:\n    raise ValueError('配置不对')\n"
                           "finally:\n    client.close()"],
                          capture_output=True, text=True, encoding="utf-8", check=False)
    assert "ValueError: 配置不对" in done.stderr
    assert "During handling of the above exception, another exception occurred" in done.stderr
    assert done.stderr.strip().endswith(
        "AttributeError: 'NoneType' object has no attribute 'close'")
