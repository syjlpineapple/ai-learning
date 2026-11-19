"""M5 每日一题的测试。所有请求都发给本机的排行榜服务（m05_http/server.py），不需要联网。

    pytest tests/test_m05.py -k p06 -v
"""

from __future__ import annotations

import logging
import time
from collections.abc import Callable, Iterator
from types import ModuleType
from typing import Any

import pytest
import requests

from m05_http import (
    p06_fetch_exercise,
    p06_fetch_solution,
    p07_classify_exercise,
    p07_classify_solution,
    p08_retry_exercise,
    p08_retry_solution,
    p09_upload_exercise,
    p09_upload_solution,
)
from m05_http.server import Running, ServerState, running_server

E = requests.exceptions


def run_or_skip(fn: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
    try:
        return fn(*args, **kwargs)
    except NotImplementedError:
        pytest.skip(f"{fn.__name__} 还没完成")


@pytest.fixture
def server() -> Iterator[Running]:
    with running_server() as srv:
        yield srv


@pytest.fixture
def dead_url() -> str:
    """一个刚刚还在、现在已经关掉的服务地址：连接会被拒绝。"""
    with running_server() as srv:
        url = srv.base_url
    return url


# ============================================================================
# 第 6 题 · 查询排行榜
# ============================================================================

P06 = {"exercise": p06_fetch_exercise, "solution": p06_fetch_solution}


@pytest.fixture(params=list(P06))
def p06(request: pytest.FixtureRequest) -> ModuleType:
    return P06[request.param]


def test_p06_basic(p06: ModuleType, server: Running) -> None:
    rows = run_or_skip(p06.fetch_scores, server.base_url, limit=3)
    assert rows == [{"player": "100%", "attempts": 1}, {"player": "张三", "attempts": 2},
                    {"player": "李四", "attempts": 3}]


def test_p06_no_player_means_everyone(p06: ModuleType, server: Running) -> None:
    rows = run_or_skip(p06.fetch_scores, server.base_url)
    assert len(rows) == len(ServerState().scores), "player 为 None 时不要传这个参数"


@pytest.mark.parametrize("player", ["张三", "A&B", "C#", "100%"])
def test_p06_special_characters(p06: ModuleType, server: Running, player: str) -> None:
    """要求 1：名字里有 & # % 中文，都要能查到。"""
    rows = run_or_skip(p06.fetch_scores, server.base_url, player=player)
    assert rows, (f"查 {player!r} 什么都没查到 —— 是不是自己拼了 URL？"
                  "& 会把参数切成两半，# 后面的部分根本不会发给服务器")
    assert {r["player"] for r in rows} == {player}


def test_p06_uses_timeout(p06: ModuleType, server: Running) -> None:
    """要求 2：timeout 参数要真的用上。服务端拖 2 秒，timeout=0.5 应该在 1 秒内失败。"""
    server.state.scores_delay = 2
    started = time.perf_counter()
    try:
        p06.fetch_scores(server.base_url, timeout=0.5)
    except NotImplementedError:
        pytest.skip("fetch_scores 还没完成")
    except E.Timeout:
        assert time.perf_counter() - started < 1.5
    else:
        pytest.fail("服务端拖了 2 秒，timeout=0.5 却成功返回了 —— timeout 参数没有传给 requests.get")


def test_p06_wrong_path_is_http_error(p06: ModuleType, server: Running) -> None:
    """要求 3：base_url 写错，服务器返回 404 和一段 HTML。要报 HTTPError，不是 JSON 解析错误。"""
    with pytest.raises(E.RequestException) as excinfo:
        run_or_skip(p06.fetch_scores, server.base_url + "/api")
    assert type(excinfo.value) is E.HTTPError, (
        f"抛的是 {type(excinfo.value).__name__} —— 先 raise_for_status()，再 json()")
    assert excinfo.value.response is not None
    assert excinfo.value.response.status_code == 404


def test_p06_bad_limit(p06: ModuleType, server: Running) -> None:
    with pytest.raises(E.HTTPError) as excinfo:
        run_or_skip(p06.fetch_scores, server.base_url, limit=0)
    assert excinfo.value.response is not None
    assert excinfo.value.response.json() == {"error": "limit 必须在 1-50 之间"}


def test_p06_server_error(p06: ModuleType, server: Running) -> None:
    server.state.scores_status = 500
    with pytest.raises(E.HTTPError):
        run_or_skip(p06.fetch_scores, server.base_url)


def test_p06_not_a_list(p06: ModuleType, server: Running) -> None:
    """要求 4：200 而且是合法 JSON，但不是数组。"""
    server.state.scores_override = {"player": "张三", "attempts": 5}
    try:
        result = run_or_skip(p06.fetch_scores, server.base_url)
    except E.InvalidJSONError:
        return
    pytest.fail(f"返回了 {result!r}。json() 只保证是合法 JSON，调用方要的是列表")


# --- 讲评里的实测结论 --------------------------------------------------------


def test_p06_review_manual_query_string(server: Running) -> None:
    b = server.base_url
    assert requests.get(f"{b}/echo?player=A&B", timeout=5).json()["query"] == \
        {"player": ["A"], "B": [""]}
    hashed = requests.get(f"{b}/echo?player=C#", timeout=5)
    assert hashed.json()["query"] == {"player": ["C"]}
    assert hashed.request.url == f"{b}/echo?player=C"
    via_params = requests.get(f"{b}/echo", params={"player": "A&B", "x": ["1", "2"], "n": None},
                              timeout=5)
    assert via_params.url == f"{b}/echo?player=A%26B&x=1&x=2"


def test_p06_review_json_before_status(server: Running) -> None:
    response = requests.get(server.base_url + "/nope", timeout=5)
    with pytest.raises(E.JSONDecodeError, match="Expecting value: line 1 column 1"):
        response.json()
    with pytest.raises(E.HTTPError, match="404 Client Error: Not Found"):
        response.raise_for_status()


def test_p06_review_timeout_is_not_total(server: Running) -> None:
    """timeout 管的是「两次收到数据之间」最多等多久，不是整个请求最多多久。"""
    started = time.perf_counter()
    response = requests.get(server.base_url + "/trickle", params={"seconds": 3}, timeout=1)
    elapsed = time.perf_counter() - started
    assert response.status_code == 200
    assert elapsed > 2, f"每 0.5 秒来一个字节，timeout=1 从来没触发，整个请求花了 {elapsed:.1f} 秒"


def test_p06_review_status_codes_not_raised(server: Running) -> None:
    not_modified = requests.get(server.base_url + "/status/304", timeout=5)
    not_modified.raise_for_status()      # 304 不是 4xx/5xx，不抛
    assert not_modified.status_code == 304
    with pytest.raises(E.HTTPError, match="429 Client Error: Too Many Requests"):
        requests.get(server.base_url + "/status/429", timeout=5).raise_for_status()


# ============================================================================
# 第 7 题 · 失败分类
# ============================================================================

P07 = {"exercise": p07_classify_exercise, "solution": p07_classify_solution}


@pytest.fixture(params=list(P07))
def p07(request: pytest.FixtureRequest) -> ModuleType:
    return P07[request.param]


def caught(call: Callable[[], object]) -> Exception:
    try:
        call()
    except Exception as e:  # noqa: BLE001 —— 收集各种真实异常用
        return e
    raise AssertionError("预期会抛异常")


def get_json(url: str, **kwargs: Any) -> object:
    response = requests.get(url, timeout=kwargs.pop("timeout", 5), **kwargs)
    response.raise_for_status()
    return response.json()


@pytest.fixture(scope="module")
def real_failures() -> dict[str, list[tuple[str, Exception]]]:
    """真的发请求，收集每一类失败的真实异常对象。"""
    with running_server() as srv:
        b = srv.base_url
        failures = {
            "slow": [("ReadTimeout", caught(lambda: get_json(b + "/slow?seconds=2", timeout=0.3)))],
            "rate_limited": [("429", caught(lambda: get_json(b + "/status/429")))],
            "server_error": [("500", caught(lambda: get_json(b + "/status/500"))),
                             ("503", caught(lambda: get_json(b + "/status/503")))],
            "client_error": [("404", caught(lambda: get_json(b + "/nope"))),
                             ("400", caught(lambda: get_json(b + "/scores?limit=0")))],
            "bad_response": [("JSONDecodeError", caught(lambda: get_json(b + "/html")))],
        }
        srv.state.scores_override = {"not": "a list"}
        failures["bad_response"].append(
            ("InvalidJSONError", caught(lambda: p06_fetch_solution.fetch_scores(b))))
    dead = b
    failures["unreachable"] = [
        ("ConnectionError", caught(lambda: get_json(dead + "/scores", timeout=5))),
        ("ConnectTimeout", E.ConnectTimeout("连接阶段超时")),
    ]
    failures["bad_url"] = [
        ("MissingSchema", caught(lambda: get_json("example.com/scores"))),
        ("InvalidSchema", caught(lambda: get_json("127.0.0.1:8765/scores"))),
        ("InvalidURL", caught(lambda: get_json("http://"))),
    ]
    return failures


CASES = [(cat, i) for cat, n in [("unreachable", 2), ("slow", 1), ("rate_limited", 1),
                                 ("server_error", 2), ("client_error", 2), ("bad_response", 2),
                                 ("bad_url", 3)] for i in range(n)]


@pytest.mark.parametrize(("category", "index"), CASES,
                         ids=[f"{c}-{i}" for c, i in CASES])
def test_p07_classify(p07: ModuleType, real_failures: dict[str, list[tuple[str, Exception]]],
                      category: str, index: int) -> None:
    name, exc = real_failures[category][index]
    got = run_or_skip(p07.classify, exc)
    assert got == category, (
        f"{name}（{type(exc).__name__}，MRO: {[c.__name__ for c in type(exc).__mro__][:5]}）"
        f"应该归为 {category}，你归成了 {got}")


def test_p07_real_exception_types(real_failures: dict[str, list[tuple[str, Exception]]]) -> None:
    """收集到的真实异常确实是题目说的那些类型。"""
    names = {name: type(exc) for cases in real_failures.values() for name, exc in cases}
    assert names["ReadTimeout"] is E.ReadTimeout
    assert names["ConnectionError"] in (E.ConnectionError, E.ConnectTimeout)
    assert names["JSONDecodeError"] is E.JSONDecodeError
    assert names["MissingSchema"] is E.MissingSchema
    assert names["InvalidSchema"] is E.InvalidSchema


def test_p07_unknown_exception_is_reraised(p07: ModuleType) -> None:
    run_or_skip(p07.classify, E.ReadTimeout("x"))
    with pytest.raises(KeyError):
        p07.classify(KeyError("不是 requests 的异常"))


def test_p07_should_retry(p07: ModuleType,
                          real_failures: dict[str, list[tuple[str, Exception]]]) -> None:
    for category, cases in real_failures.items():
        for name, exc in cases:
            assert run_or_skip(p07.should_retry, exc) is p07_classify_solution.RETRYABLE[category], name


# --- 讲评里的实测结论 --------------------------------------------------------


def test_p07_review_multiple_inheritance() -> None:
    assert issubclass(E.ConnectTimeout, E.ConnectionError) and issubclass(E.ConnectTimeout, E.Timeout)
    assert not issubclass(E.ReadTimeout, E.ConnectionError)
    for cls in (E.JSONDecodeError, E.MissingSchema, E.InvalidSchema, E.InvalidURL):
        assert issubclass(cls, ValueError) and issubclass(cls, E.RequestException), cls


def test_p07_review_builtin_names_do_not_match(dead_url: str) -> None:
    """except ConnectionError（没写 requests.exceptions.）接的是内置的那个，接不住。"""
    import builtins

    assert not issubclass(E.ConnectionError, builtins.ConnectionError)
    assert not issubclass(E.Timeout, builtins.TimeoutError)
    exc = caught(lambda: requests.get(dead_url + "/scores", timeout=5))
    assert isinstance(exc, E.ConnectionError)
    assert not isinstance(exc, builtins.ConnectionError)


def test_p07_review_http_error_carries_response(server: Running) -> None:
    response = requests.get(server.base_url + "/status/503", timeout=5)
    exc = caught(response.raise_for_status)
    assert isinstance(exc, E.HTTPError)
    assert exc.response is response and exc.response.json() == {"error": "服务端按要求返回了 503"}
    assert E.HTTPError("自己构造的").response is None


# ============================================================================
# 第 8 题 · 失败了就重试
# ============================================================================

P08 = {"exercise": p08_retry_exercise, "solution": p08_retry_solution}


@pytest.fixture(params=list(P08))
def p08(request: pytest.FixtureRequest) -> ModuleType:
    return P08[request.param]


class Recorder:
    """代替 time.sleep：只记下要等多久，不真的等。"""

    def __init__(self) -> None:
        self.delays: list[float] = []

    def __call__(self, seconds: float) -> None:
        self.delays.append(seconds)


def scores_call(srv: Running, timeout: float = 5) -> Callable[[], object]:
    return lambda: p06_fetch_solution.fetch_scores(srv.base_url, limit=1, timeout=timeout)


def retry(p08: ModuleType, call: Callable[[], object], sleep: Recorder, **kwargs: Any) -> Any:
    return run_or_skip(p08.with_retry, call, sleep=sleep, **kwargs)


def test_p08_success_first_time(p08: ModuleType, server: Running) -> None:
    sleep = Recorder()
    assert retry(p08, scores_call(server), sleep) == [{"player": "100%", "attempts": 1}]
    assert sleep.delays == [] and server.state.scores_gets == 1


def test_p08_recovers_after_failures(p08: ModuleType, server: Running) -> None:
    """要求 1、3：两次 503 之后成功。等待 0.5 秒、1 秒，一共请求 3 次。"""
    server.state.fail_plan = [503, 503]
    sleep = Recorder()
    assert retry(p08, scores_call(server), sleep) == [{"player": "100%", "attempts": 1}]
    assert server.state.scores_gets == 3
    assert sleep.delays == [0.5, 1.0], f"等待时间应该是 0.5、1（翻倍），实际 {sleep.delays}"


def test_p08_gives_up_with_original_error(p08: ModuleType, server: Running) -> None:
    """要求 1、4：一直失败，最多请求 attempts 次，最后把原来的 HTTPError 抛出来。"""
    server.state.fail_plan = [503] * 5
    sleep = Recorder()
    try:
        result = retry(p08, scores_call(server), sleep, attempts=3)
    except E.HTTPError as e:
        assert e.response is not None and e.response.status_code == 503
    else:
        pytest.fail(f"3 次都失败了，却返回了 {result!r} —— 最后一次的异常要抛出来")
    assert server.state.scores_gets == 3, f"应该请求 3 次，实际 {server.state.scores_gets} 次"
    assert sleep.delays == [0.5, 1.0], f"最后一次失败之后不用再等了，实际等了 {sleep.delays}"


def test_p08_does_not_retry_client_error(p08: ModuleType, server: Running) -> None:
    """要求 2：404 不值得重试，立刻抛出，一秒都不等。"""
    sleep = Recorder()
    calls: list[int] = []

    def call() -> object:
        calls.append(1)
        return p06_fetch_solution.fetch_scores(server.base_url + "/api", timeout=5)

    with pytest.raises(E.HTTPError):
        retry(p08, call, sleep)
    assert len(calls) == 1 and sleep.delays == [], f"请求了 {len(calls)} 次，等了 {sleep.delays}"


def test_p08_does_not_retry_bugs(p08: ModuleType) -> None:
    """要求 2：不是 requests 的异常（程序自己的 bug）直接抛出。"""
    sleep = Recorder()

    def buggy() -> object:
        empty: dict[str, int] = {}
        return empty["没有这个键"]

    with pytest.raises(KeyError):
        retry(p08, buggy, sleep)
    assert sleep.delays == []


def test_p08_retries_timeout(p08: ModuleType, server: Running) -> None:
    server.state.fail_plan = ["slow"]
    sleep = Recorder()
    assert retry(p08, scores_call(server, timeout=0.5), sleep) == [{"player": "100%", "attempts": 1}]
    assert sleep.delays == [0.5]


@pytest.mark.parametrize(("header", "expected"), [("2", [2.0]), ("0.25", [0.25]),
                                                  ("Wed, 21 Oct 2026 07:28:00 GMT", [0.5]),
                                                  (None, [0.5])],
                         ids=["seconds", "fraction", "http_date", "missing"])
def test_p08_retry_after(p08: ModuleType, server: Running, header: str | None,
                         expected: list[float]) -> None:
    """要求 3：429 带了 Retry-After（秒数）就按它等；没有或看不懂就按翻倍的规则。"""
    server.state.fail_plan = [429]
    server.state.retry_after = header
    sleep = Recorder()
    retry(p08, scores_call(server), sleep)
    assert sleep.delays == expected


def test_p08_retry_after_function(p08: ModuleType, server: Running) -> None:
    server.state.fail_plan = [429]
    server.state.retry_after = "3"
    exc = caught(scores_call(server))
    assert run_or_skip(p08.retry_after, exc) == 3.0
    assert p08.retry_after(E.ReadTimeout("x")) is None
    assert p08.retry_after(E.HTTPError("没有 response")) is None


def test_p08_logs_each_retry(p08: ModuleType, server: Running,
                             caplog: pytest.LogCaptureFixture) -> None:
    """要求 4：每次重试前记一条 WARNING，写明第几次、什么类别、等多久。"""
    server.state.fail_plan = [503, "slow"]
    caplog.set_level(logging.DEBUG, logger=p08.__name__)
    retry(p08, scores_call(server, timeout=0.5), Recorder())
    warnings = [r.getMessage() for r in caplog.records
                if r.levelno == logging.WARNING and r.name == p08.__name__]
    assert len(warnings) == 2, f"重试了 2 次，应该有 2 条 WARNING：{warnings}"
    for message, nth, category, delay in [(warnings[0], 1, "server_error", "0.5"),
                                          (warnings[1], 2, "slow", "1.0")]:
        missing = [part for part in (f"第 {nth} 次", category, delay) if part not in message]
        assert not missing, f"这条日志里缺了 {missing}：{message!r}"


def test_p08_combined_with_real_sleep(server: Running) -> None:
    """参考答案组合起来用，真的等 0.5 秒。"""
    server.state.fail_plan = [503]
    started = time.perf_counter()
    assert len(p08_retry_solution.fetch_scores_with_retry(server.base_url)) == 7
    assert 0.45 < time.perf_counter() - started < 3


# ============================================================================
# 第 9 题 · 上传成绩
# ============================================================================

P09 = {"exercise": p09_upload_exercise, "solution": p09_upload_solution}


@pytest.fixture(params=list(P09))
def p09(request: pytest.FixtureRequest) -> ModuleType:
    return P09[request.param]


def stored(srv: Running, player: str) -> list[dict[str, object]]:
    return [r for r in srv.state.scores if r["player"] == player]


def test_p09_upload(p09: ModuleType, server: Running) -> None:
    """要求 1：发 JSON，返回服务端的回答；上传的成绩能查到。"""
    row = run_or_skip(p09.upload_score, server.base_url, "欧阳修文", 3)
    assert row == {"id": 8, "player": "欧阳修文", "attempts": 3}
    assert {"player": "欧阳修文", "attempts": 3} in p06_fetch_solution.fetch_scores(
        server.base_url, player="欧阳修文")


def test_p09_validation_error(p09: ModuleType, server: Running) -> None:
    """要求 2：服务端拒绝时抛 HTTPError，原因在 e.response 里。"""
    with pytest.raises(E.HTTPError) as excinfo:
        run_or_skip(p09.upload_score, server.base_url, "张三", 0)
    assert excinfo.value.response is not None
    assert excinfo.value.response.status_code == 400
    assert excinfo.value.response.json() == {"error": "attempts 必须是 1-100 的整数"}


def test_p09_idempotency_key(p09: ModuleType, server: Running) -> None:
    """要求 1：key 放进 Idempotency-Key 头。同一个 key 上传两次，只存一条。"""
    first = run_or_skip(p09.upload_score, server.base_url, "王五", 4, key="k-1")
    second = p09.upload_score(server.base_url, "王五", 4, key="k-1")
    assert first == second
    assert len(stored(server, "王五")) == 1, "同一个 key 存了两条 —— Idempotency-Key 头没有发出去"


def test_p09_retry_does_not_duplicate(p09: ModuleType, server: Running) -> None:
    """要求 3：第一次上传其实成功了，只是回答太慢、客户端超时了。重试之后，服务端只能有一条。"""
    server.state.slow_posts = 1
    try:
        row = p09.upload_with_retry(server.base_url, "赵六", 5, timeout=0.5)
    except NotImplementedError:
        pytest.skip("upload_with_retry 还没完成")
    except E.Timeout:
        pytest.fail("第一次超时以后没有重试 —— 用 with_retry 包起来")
    assert row["player"] == "赵六"
    rows = stored(server, "赵六")
    assert len(rows) == 1, (
        f"服务端存了 {len(rows)} 条。第一次请求超时时成绩其实已经存好了，重试时又存了一条 —— "
        "每次重试要带同一个 Idempotency-Key")


def test_p09_upload_with_retry_normal(p09: ModuleType, server: Running) -> None:
    row = run_or_skip(p09.upload_with_retry, server.base_url, "钱七", 2)
    assert row == {"id": 8, "player": "钱七", "attempts": 2}
    assert len(stored(server, "钱七")) == 1


# --- 讲评里的实测结论 --------------------------------------------------------


def test_p09_review_data_sends_form(server: Running) -> None:
    response = requests.post(server.base_url + "/scores", data={"player": "张三", "attempts": 3},
                             timeout=5)
    assert response.status_code == 415
    assert "application/x-www-form-urlencoded" in response.json()["error"]
    echo = requests.post(server.base_url + "/echo", data={"player": "张三", "attempts": 3},
                         timeout=5).json()
    assert echo["body"] == "player=%E5%BC%A0%E4%B8%89&attempts=3"


def test_p09_review_key_inside_lambda_duplicates(server: Running) -> None:
    """key 写进 lambda：每次重试都生成新 key，服务端存了两条。"""
    import uuid

    server.state.slow_posts = 1
    p08_retry_solution.with_retry(lambda: p09_upload_solution.upload_score(
        server.base_url, "孙八", 6, key=uuid.uuid4().hex, timeout=0.5))
    assert len(stored(server, "孙八")) == 2


def test_p09_review_no_key_duplicates(server: Running) -> None:
    server.state.slow_posts = 1
    p08_retry_solution.with_retry(lambda: p09_upload_solution.upload_score(
        server.base_url, "周九", 6, timeout=0.5))
    assert len(stored(server, "周九")) == 2
