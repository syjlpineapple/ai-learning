"""M8 每日一题的测试。

    pytest tests/test_m08.py -k p14 -v      （p15、p16 同理）

第 14 题是你写测试，这里评测你的测试：先用正确的 APIClient 跑一遍，再换成 8 个故意写错的版本，
每个版本跑一遍。每次都开一个新的 pytest 进程，并且把网络断掉。

第 16 题是你写 fixture，这里用你的 fixture 跑两个写好的测试文件，看每个测试的结果。
"""

from __future__ import annotations

import inspect
import logging
import os
import re
import subprocess
import sys
import time
from collections.abc import Callable
from pathlib import Path
from types import ModuleType
from typing import Any
from unittest.mock import MagicMock, call, create_autospec

import pytest
import requests

from m05_http.server import SEED_SCORES, ServerState, running_server
from m08_testing import p15_decorators_exercise, p15_decorators_solution
from m08_testing._p14_mutants import MUTANTS

CODE_DIR = Path(__file__).resolve().parents[1]

# 断网插件：任何 socket 连接都直接失败，并说明原因
NO_NETWORK_PLUGIN = '''
import socket

def _blocked(self, *args, **kwargs):
    raise RuntimeError("第 14 题的测试不能发真实的网络请求 —— 用 MagicMock 代替 Session 的方法")

socket.socket.connect = _blocked
socket.socket.connect_ex = _blocked
'''


def rootdir_for(files: list[str], tmp_path: Path | None) -> list[str]:
    """测试文件在临时目录里时，把 rootdir 也设成那个临时目录。

    不设的话，rootdir 是 code/ 和临时目录的公共上级（比如整个 Temp 目录），pytest 收集时会
    扫描那一层，别的程序在 Temp 里刚建又删掉的文件会让收集报 FileNotFoundError。
    """
    if tmp_path is not None and any(Path(f).is_absolute() for f in files):
        return ["--rootdir", str(tmp_path)]
    return []


def run_tests_in(module_file: str, tmp_path: Path,
                 mutant: str | None = None) -> subprocess.CompletedProcess[str]:
    (tmp_path / "pe_no_network.py").write_text(NO_NETWORK_PLUGIN, encoding="utf-8")
    env = {**os.environ, "PYTHONUTF8": "1",
           "PYTHONPATH": os.pathsep.join([str(tmp_path), str(CODE_DIR)])}
    env.pop("PE_P14_MUTANT", None)
    if mutant is not None:
        env["PE_P14_MUTANT"] = mutant
    return subprocess.run(
        [sys.executable, "-m", "pytest", module_file, "-q", "-p", "no:cacheprovider",
         "-p", "pe_no_network", "--tb=short", *rootdir_for([module_file], tmp_path)],
        cwd=CODE_DIR, capture_output=True, text=True, encoding="utf-8", env=env, check=False,
        stdin=subprocess.DEVNULL)    # 不继承终端的输入，否则在某些终端里子进程会卡住


SOLUTION = "m08_testing/p14_mock_solution.py"
EXERCISE = "m08_testing/p14_mock_exercise.py"


# ============================================================================
# 第 14 题 · 参考答案
# ============================================================================


def test_p14_solution_passes(tmp_path: Path) -> None:
    done = run_tests_in(SOLUTION, tmp_path)
    assert done.returncode == 0, done.stdout


@pytest.mark.parametrize("mutant", list(MUTANTS))
def test_p14_solution_kills_mutant(tmp_path: Path, mutant: str) -> None:
    done = run_tests_in(SOLUTION, tmp_path, mutant)
    assert done.returncode == 1, f"参考答案没抓住 {mutant}：\n{done.stdout}"


def test_p14_weak_suite_misses_all(tmp_path: Path) -> None:
    """对照：用 MagicMock 当 Session、只断言返回值的「弱测试」，8 个写错的版本全都能混过去。"""
    weak = CODE_DIR / "m08_testing" / f"_weak_{tmp_path.name}.py"
    tmp_path.mkdir(exist_ok=True)
    weak.write_text(
        "from unittest.mock import MagicMock\n"
        "from m06_config.p10_settings_solution import Settings\n"
        "from m08_testing.p14_target import APIClient\n"
        "def test_get_scores():\n"
        "    session = MagicMock()\n"
        "    session.request.return_value.json.return_value = [{'player': 'x', 'attempts': 1}]\n"
        "    s = Settings(api_key='k', base_url='http://h', timeout=1.0, retries=0, debug=False)\n"
        "    assert APIClient(s, session=session).get_scores() == [{'player': 'x', 'attempts': 1}]\n",
        encoding="utf-8")
    try:
        assert run_tests_in(str(weak), tmp_path).returncode == 0, "弱测试本身要能通过"
        survived = [m for m in MUTANTS if run_tests_in(str(weak), tmp_path, m).returncode == 0]
    finally:
        weak.unlink()
    assert survived == list(MUTANTS)


def test_p14_network_is_blocked(tmp_path: Path) -> None:
    probe = tmp_path / "test_probe.py"
    probe.write_text("import requests\ndef test_real():\n"
                     "    requests.get('http://127.0.0.1:9', timeout=1)\n", encoding="utf-8")
    done = run_tests_in(str(probe), tmp_path)
    assert done.returncode == 1
    assert "不能发真实的网络请求" in done.stdout


# ============================================================================
# 第 14 题 · 你的测试
# ============================================================================


def exercise_or_skip(tmp_path: Path) -> None:
    done = run_tests_in(EXERCISE, tmp_path)
    if done.returncode == 5:
        pytest.skip("p14_mock_exercise.py 里还没有测试（collected 0 items）")
    assert done.returncode == 0, (
        "你的测试在正确的 APIClient 上就没通过，先让它们通过：\n" + done.stdout)


def test_p14_exercise_passes(tmp_path: Path) -> None:
    exercise_or_skip(tmp_path)


@pytest.mark.parametrize("mutant", list(MUTANTS))
def test_p14_exercise_kills_mutant(tmp_path: Path, mutant: str) -> None:
    exercise_or_skip(tmp_path)
    done = run_tests_in(EXERCISE, tmp_path, mutant)
    assert done.returncode == 1, (
        f"你的测试没抓住「{MUTANTS[mutant].__doc__}」这个写错的版本 —— 它在你的测试下全部通过了")


# --- 讲评里的实测结论 --------------------------------------------------------


def test_p14_review_silent_attributes() -> None:
    m = MagicMock()
    assert bool(m.caled) is True, "把 called 拼错成 caled，assert m.caled 照样通过"
    assert isinstance(m.asssert_called_once(), MagicMock), "三个 s：保护没拦住，静默通过"
    with pytest.raises(AttributeError, match="is not a valid assertion"):
        m.assert_called_onse()


def test_p14_review_magicmock_response_never_fails() -> None:
    fake = MagicMock()
    fake.status_code = 503
    assert isinstance(fake.raise_for_status(), MagicMock), "503 也不会抛异常"
    assert not isinstance(fake.json(), list)


def test_p14_review_spec_with_class_misses_instance_attrs() -> None:
    with pytest.raises(AttributeError, match="no attribute 'headers'"):
        MagicMock(spec=requests.Session).headers  # noqa: B018
    with pytest.raises(AttributeError, match="no attribute 'status_code'"):
        MagicMock(spec=requests.Response).status_code  # noqa: B018
    assert isinstance(MagicMock(spec=requests.Response()).status_code, MagicMock)


def test_p14_review_spec_allows_setting() -> None:
    loose = MagicMock(spec=requests.Session)
    loose.pots = 1                                  # spec：读不存在的属性报错，写可以
    with pytest.raises(AttributeError):
        MagicMock(spec_set=requests.Session).pots = 1


def test_p14_review_autospec_checks_signature() -> None:
    assert isinstance(MagicMock(spec=requests.Session).request(), MagicMock)
    with pytest.raises(TypeError, match="missing a required argument: 'method'"):
        create_autospec(requests.Session, instance=True).request()


def test_p14_review_side_effect_list_runs_out() -> None:
    m = MagicMock(side_effect=[1, requests.exceptions.ReadTimeout("慢"), 3])
    assert m() == 1
    with pytest.raises(requests.exceptions.ReadTimeout):
        m()
    assert m() == 3
    with pytest.raises(StopIteration):
        m()


def test_p14_review_assert_called_with_is_last_call() -> None:
    m = MagicMock()
    m("a", x=1)
    m("b", x=2)
    with pytest.raises(AssertionError, match="expected call not found"):
        m.assert_called_with("a", x=1)
    assert m.call_args_list == [call("a", x=1), call("b", x=2)]
    assert m.call_args.kwargs == {"x": 2}


# ============================================================================
# 第 15 题 · 装饰器
# ============================================================================

P15 = {"exercise": p15_decorators_exercise, "solution": p15_decorators_solution}


@pytest.fixture(params=list(P15))
def p15(request: pytest.FixtureRequest) -> ModuleType:
    return P15[request.param]


class Flaky:
    """前 fail_times 次抛 ReadTimeout，之后返回 "ok"。"""

    def __init__(self, fail_times: int, exc: Exception | None = None) -> None:
        self.calls: list[tuple[Any, ...]] = []
        self.fail_times = fail_times
        self.exc = exc or requests.exceptions.ReadTimeout("慢")
        self.__name__ = self.__qualname__ = "flaky"     # 装起来像一个普通函数

    def __call__(self, *args: Any) -> str:
        self.calls.append(args)
        if len(self.calls) <= self.fail_times:
            raise self.exc
        return "ok"


def decorate_or_skip(decorator: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
    try:
        return decorator(*args, **kwargs)
    except NotImplementedError:
        pytest.skip("还没完成")


def test_p15_retrying_with_args(p15: ModuleType) -> None:
    """要求 1：@retrying(...) 带参数。"""
    delays: list[float] = []
    flaky = Flaky(2)
    wrapped = decorate_or_skip(p15.retrying, attempts=3, sleep=delays.append)(flaky)
    assert wrapped("张三") == "ok"
    assert flaky.calls == [("张三",)] * 3 and delays == [0.5, 1.0]


def test_p15_retrying_bare(p15: ModuleType) -> None:
    """要求 1：@retrying 不带括号，用默认参数：失败一次，真的等 0.5 秒再试。"""
    flaky = Flaky(1)
    wrapped = decorate_or_skip(p15.retrying, flaky)
    assert callable(wrapped) and not isinstance(wrapped, str), (
        "@retrying 不带括号时，retrying 收到的第一个参数就是被装饰的函数")
    started = time.perf_counter()
    assert wrapped() == "ok"
    assert len(flaky.calls) == 2
    assert time.perf_counter() - started >= 0.45, "默认的 base_delay 是 0.5 秒"


def test_p15_retrying_gives_up(p15: ModuleType) -> None:
    delays: list[float] = []
    flaky = Flaky(9)
    wrapped = decorate_or_skip(p15.retrying, attempts=2, sleep=delays.append)(flaky)
    with pytest.raises(requests.exceptions.ReadTimeout):
        wrapped()
    assert len(flaky.calls) == 2


def test_p15_retrying_not_retryable(p15: ModuleType) -> None:
    delays: list[float] = []
    flaky = Flaky(9, KeyError("bug"))
    wrapped = decorate_or_skip(p15.retrying, sleep=delays.append)(flaky)
    with pytest.raises(KeyError):
        wrapped()
    assert len(flaky.calls) == 1 and delays == []


def test_p15_decoration_does_not_call(p15: ModuleType) -> None:
    """装饰的时候不能调用被装饰的函数，调用的时候才调用。"""
    flaky = Flaky(0)
    decorate_or_skip(p15.retrying, flaky)
    decorate_or_skip(p15.retrying, sleep=lambda _s: None)(flaky)
    decorate_or_skip(p15.logged, logging.getLogger("x"))(flaky)
    assert flaky.calls == []


def sample(player: str, limit: int = 10) -> list[str]:
    """查排行榜。"""
    return [player] * limit


@pytest.mark.parametrize("which", ["retrying_bare", "retrying_args", "logged"])
def test_p15_keeps_metadata(p15: ModuleType, which: str) -> None:
    """要求 2：被装饰以后，名字、文档、参数签名都不变。"""
    if which == "retrying_bare":
        wrapped = decorate_or_skip(p15.retrying, sample)
    elif which == "retrying_args":
        wrapped = decorate_or_skip(p15.retrying, attempts=2)(sample)
    else:
        wrapped = decorate_or_skip(p15.logged, logging.getLogger("x"))(sample)
    assert wrapped.__name__ == "sample", f"名字变成了 {wrapped.__name__!r} —— functools.wraps"
    assert wrapped.__doc__ == "查排行榜。"
    assert str(inspect.signature(wrapped)) == str(inspect.signature(sample))
    assert wrapped("张三", 2) == ["张三", "张三"]


def test_p15_works_on_methods(p15: ModuleType) -> None:
    delays: list[float] = []
    retrying = decorate_or_skip(p15.retrying, sleep=delays.append)

    class Client:
        def __init__(self) -> None:
            self.flaky = Flaky(1)

        @retrying
        def fetch(self, player: str) -> str:
            return f"{self.flaky(player)}:{player}"

    assert Client().fetch("张三") == "ok:张三"


def test_p15_logged(p15: ModuleType, caplog: pytest.LogCaptureFixture) -> None:
    """要求 3：调用前后各一条 DEBUG；出错时一条 WARNING，异常原样抛出。"""
    log = logging.getLogger("pe.p15.logged")
    caplog.set_level(logging.DEBUG, logger=log.name)
    wrapped = decorate_or_skip(p15.logged, log)(sample)
    assert wrapped("张三", 1) == ["张三"]
    debug = [r.getMessage() for r in caplog.records if r.levelno == logging.DEBUG]
    assert len(debug) == 2 and "sample" in debug[0] and "秒" in debug[1], debug

    caplog.clear()
    error = requests.exceptions.ReadTimeout("慢")
    failing = decorate_or_skip(p15.logged, log)(Flaky(9, error))
    with pytest.raises(requests.exceptions.ReadTimeout) as excinfo:
        failing()
    assert excinfo.value is error, "要原样抛出同一个异常对象"
    warnings = [r for r in caplog.records if r.levelno == logging.WARNING]
    assert len(warnings) == 1 and "ReadTimeout" in warnings[0].getMessage()
    assert warnings[0].exc_info is None, "这里只说一句；traceback 留给真正处理它的地方"


def test_p15_stacking_order(p15: ModuleType, caplog: pytest.LogCaptureFixture) -> None:
    """要求 4：@logged 在外、@retrying 在里：重试成功了，就不该有 WARNING。"""
    log = logging.getLogger("pe.p15.stack")
    caplog.set_level(logging.DEBUG, logger=log.name)
    delays: list[float] = []
    flaky = Flaky(2)
    outer = decorate_or_skip(p15.logged, log)
    inner = decorate_or_skip(p15.retrying, sleep=delays.append)
    wrapped = outer(inner(flaky))

    def warnings() -> list[logging.LogRecord]:
        # 只数 logged 记的；第 8 题的 with_retry 自己也会记 WARNING，不算在内
        return [r for r in caplog.records if r.name == log.name and r.levelno == logging.WARNING]

    assert wrapped() == "ok"
    assert warnings() == []
    reversed_ = inner(outer(Flaky(2)))
    caplog.clear()
    reversed_()
    assert len(warnings()) == 2, (
        "顺序反过来，logged 在 retrying 里面，每一次失败都会记一条")


def test_p15_pytest_fixture_injection(p15: ModuleType, tmp_path: Path) -> None:
    """要求 2：被装饰的 pytest 测试函数，fixture 照样能注入。"""
    decorate_or_skip(p15.retrying, sample)          # 还没完成就跳过，不必开子进程
    test_file = tmp_path / "test_deco_fixture.py"
    test_file.write_text(
        "import logging\nimport pytest\n"
        f"from {p15.__name__} import logged, retrying\n"
        "@pytest.fixture\ndef player():\n    return '张三'\n"
        "@retrying\ndef test_bare(player):\n    assert player == '张三'\n"
        "@retrying(attempts=2)\ndef test_args(player):\n    assert player == '张三'\n"
        "@logged(logging.getLogger('t'))\ndef test_logged(player):\n    assert player == '张三'\n",
        encoding="utf-8")
    done = run_tests_in(str(test_file), tmp_path)
    assert done.returncode == 0, (
        "被你的装饰器装饰过的测试，fixture 没有注入进去（missing 1 required positional argument）"
        "—— pytest 靠 functools.wraps 留下的签名找参数：\n" + done.stdout[-1500:])


# --- 讲评里的实测结论 --------------------------------------------------------


def test_p15_review_no_wraps_breaks_fixture(tmp_path: Path) -> None:
    test_file = tmp_path / "test_nowraps.py"
    test_file.write_text(
        "import pytest\n"
        "def no_wraps(fn):\n    def wrapper(*args, **kwargs):\n"
        "        return fn(*args, **kwargs)\n    return wrapper\n"
        "@pytest.fixture\ndef player():\n    return '张三'\n"
        "@no_wraps\ndef test_x(player):\n    assert player\n", encoding="utf-8")
    done = run_tests_in(str(test_file), tmp_path)
    assert done.returncode == 1
    assert "test_x() missing 1 required positional argument: 'player'" in done.stdout


def test_p15_review_metadata_without_wraps() -> None:
    def no_wraps(fn: Callable[..., Any]) -> Callable[..., Any]:
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            return fn(*args, **kwargs)
        return wrapper

    wrapped = no_wraps(sample)
    assert (wrapped.__name__, wrapped.__doc__) == ("wrapper", None)
    assert list(inspect.signature(wrapped).parameters) == ["args", "kwargs"]


def test_p15_review_factory_without_parens() -> None:
    def factory(attempts: int = 3) -> Callable[[Callable[[], str]], Callable[[], str]]:
        def deco(fn: Callable[[], str]) -> Callable[[], str]:
            return fn
        return deco

    # 等于写了 @factory 不带括号：sample 被当成了 attempts。mypy 能查出这一行，所以这里要压掉
    broken: Any = factory(sample)  # type: ignore[arg-type]
    with pytest.raises(TypeError, match="missing 1 required positional argument: 'fn'"):
        broken()


def test_p15_review_decorator_runs_at_def_time() -> None:
    seen: list[str] = []

    def register(fn: Callable[..., Any]) -> Callable[..., Any]:
        seen.append(fn.__name__)        # 装饰器本身的代码：def 的那一刻就执行
        return fn

    @register
    def get_scores() -> None: ...

    assert seen == ["get_scores"]       # 一次都没调用 get_scores，装饰器已经跑过了


def test_p15_review_swallowing_returns_none(caplog: pytest.LogCaptureFixture) -> None:
    log = logging.getLogger("pe.p15.swallow")

    def swallowing(fn: Callable[..., Any]) -> Callable[..., Any]:
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return fn(*args, **kwargs)
            except Exception:
                log.exception("失败")    # 记了日志，但没有 raise
        return wrapper

    result = swallowing(Flaky(9))()
    assert result is None               # 调用方拿到 None，以为成功了
    assert caplog.records[-1].levelno == logging.ERROR


def test_p15_review_default_bound_at_def_time(monkeypatch: pytest.MonkeyPatch) -> None:
    original = time.sleep
    monkeypatch.setattr(time, "sleep", lambda _s: None)
    # 默认值 sleep=time.sleep 在 def retrying 的那一刻就取好了，后来再换 time.sleep 不影响它
    kwdefaults = p15_decorators_solution.retrying.__kwdefaults__
    assert kwdefaults is not None
    default = kwdefaults["sleep"]
    assert default is original and default is not time.sleep


def test_p15_review_swallowing_hides_failed_test(tmp_path: Path) -> None:
    test_file = tmp_path / "test_swallow.py"
    test_file.write_text(
        "import logging\n"
        "def swallowing(fn):\n    def wrapper(*args, **kwargs):\n        try:\n"
        "            return fn(*args, **kwargs)\n        except Exception:\n"
        "            logging.exception('失败')\n    return wrapper\n"
        "@swallowing\ndef test_always_wrong():\n    assert 1 + 1 == 3\n", encoding="utf-8")
    done = run_tests_in(str(test_file), tmp_path)
    # AssertionError 也是 Exception：断言失败被装饰器接住，pytest 以为测试通过了
    assert done.returncode == 0 and "1 passed" in done.stdout, done.stdout


# ============================================================================
# 第 16 题 · 给测试搭环境
# ============================================================================

P16 = {"exercise": "m08_testing.p16_fixtures_exercise",
       "solution": "m08_testing.p16_fixtures_solution"}
P16_CONSUMERS = ["m08_testing/_p16_consumer_a.py", "m08_testing/_p16_consumer_b.py"]
APP_ENV_KEYS = ("API_KEY", "API_BASE_URL", "TIMEOUT", "RETRIES", "APP_ENV", "DEBUG")


def run_with_plugin(files: list[str], plugin: str,
                    extra_path: Path | None = None) -> subprocess.CompletedProcess[str]:
    # 外面的环境里如果正好设了这几个变量，「测试结束后恢复原样」就检查不出来了，先去掉
    env = {k: v for k, v in os.environ.items() if k not in APP_ENV_KEYS}
    env["PYTHONUTF8"] = "1"
    env["PYTHONPATH"] = os.pathsep.join([str(p) for p in (extra_path, CODE_DIR) if p])
    return subprocess.run(
        [sys.executable, "-m", "pytest", *files, "-p", plugin, "-p", "no:cacheprovider",
         "-rA", "-q", "--tb=short", *rootdir_for(files, extra_path)],
        cwd=CODE_DIR, capture_output=True, text=True, encoding="utf-8", env=env, check=False,
        stdin=subprocess.DEVNULL, timeout=120)


def outcomes(stdout: str) -> dict[str, list[str]]:
    """从 -rA 的汇总里取出每个测试的结果。一个测试可能有两条（比如 PASSED 加清理时的 ERROR）。"""
    result: dict[str, list[str]] = {}
    # 文件不在 code/ 下面时，pytest 显示的测试 ID 前面没有路径，只有 ::test_xxx，所以是 \S*
    for m in re.finditer(r"^(PASSED|FAILED|ERROR|XFAIL|XPASS|SKIPPED) \S*::(\w+)", stdout, re.M):
        result.setdefault(m.group(2), []).append(m.group(1))
    return result


@pytest.fixture(scope="module", params=list(P16))
def p16(request: pytest.FixtureRequest) -> tuple[dict[str, list[str]], str]:
    # 用你的 fixture 跑一遍那两个测试文件。module 作用域：下面几个测试共用这一次的结果
    done = run_with_plugin(P16_CONSUMERS, P16[request.param])
    if "NotImplementedError" in done.stdout:
        pytest.skip("还没完成")
    return outcomes(done.stdout), done.stdout


def expect(p16: tuple[dict[str, list[str]], str], wanted: dict[str, str]) -> None:
    got, stdout = p16
    wrong = {name: got.get(name, ["没有运行"]) for name, outcome in wanted.items()
             if got.get(name) != [outcome]}
    assert not wrong, f"{wrong}\n\n{stdout[-3000:]}"


def test_p16_one_server(p16: tuple[dict[str, list[str]], str]) -> None:
    """要求 1：整个测试运行只开一个服务。"""
    expect(p16, {"test_another_file": "PASSED", "test_one_server_for_all": "PASSED"})


def test_p16_state_reset(p16: tuple[dict[str, list[str]], str]) -> None:
    """要求 2：每个测试开始时，服务是刚启动的样子。"""
    expect(p16, {"test_state_is_fresh": "PASSED"})


def test_p16_app_env(p16: tuple[dict[str, list[str]], str]) -> None:
    """要求 3：环境变量设上了，测试结束后恢复原样。"""
    expect(p16, {"test_dirty_everything": "PASSED", "test_env_is_restored": "PASSED"})


def test_p16_client_closed(p16: tuple[dict[str, list[str]], str]) -> None:
    """要求 4：client 测试结束后关掉，测试失败了也关。"""
    expect(p16, {"test_failing_test": "XFAIL", "test_clients_closed": "PASSED"})


# --- 讲评里的实测结论 --------------------------------------------------------


def test_p16_review_shutdown_takes_half_a_second() -> None:
    with running_server() as srv:
        requests.get(srv.base_url + "/scores", timeout=2)
        started = time.perf_counter()
    # serve_forever 每 0.5 秒才看一次「该停了吗」，shutdown 要等它看到
    assert time.perf_counter() - started >= 0.3


def test_p16_review_rebinding_state_does_nothing() -> None:
    with running_server() as srv:
        srv.state.fail_plan = [503]
        srv.state = ServerState()           # 只是 Running.state 指向了新对象
        status = requests.get(srv.base_url + "/scores", timeout=2).status_code
    assert status == 503                    # 服务端手里还是旧的那个


def test_p16_review_seed_alias_mutates_constant() -> None:
    snapshot = list(SEED_SCORES)
    try:
        with running_server() as srv:
            srv.state.scores = SEED_SCORES          # 没有复制，两个名字指向同一个列表
            requests.post(srv.base_url + "/scores", json={"player": "王五", "attempts": 3},
                          timeout=2)
        assert len(SEED_SCORES) == len(snapshot) + 1
    finally:
        SEED_SCORES[:] = snapshot                   # 把常量改回去，免得影响别的测试


P16_RULES_PLUGIN = '''
import os
import pytest

EVENTS = []

@pytest.fixture(scope="session")
def shared(monkeypatch):
    return 1

@pytest.fixture(scope="session")
def shared_tmp(tmp_path):
    return tmp_path

@pytest.fixture
def leaky_env():
    os.environ["PE_LEAK"] = "1"

@pytest.fixture
def tracked():
    EVENTS.append("setup")
    yield
    EVENTS.append("teardown")

@pytest.fixture
def broken_setup():
    EVENTS.append("broken-setup")
    raise RuntimeError("setup 半路出错")
    yield
    EVENTS.append("broken-teardown")
'''

P16_RULES_TESTS = '''
import os
import pe_p16_rules

def test_scope_mismatch(shared): pass
def test_scope_mismatch_tmp(shared_tmp): pass
def test_leak_a(leaky_env): pass
def test_leak_b(): assert "PE_LEAK" not in os.environ
def test_fails(tracked): assert 1 + 1 == 3
def test_after_fails(): assert pe_p16_rules.EVENTS == ["setup", "teardown"]
def test_broken(broken_setup): pass
def test_after_broken(): assert pe_p16_rules.EVENTS[-1] == "broken-setup"
'''


def test_p16_review_fixture_rules(tmp_path: Path) -> None:
    (tmp_path / "pe_p16_rules.py").write_text(P16_RULES_PLUGIN, encoding="utf-8")
    (tmp_path / "test_rules.py").write_text(P16_RULES_TESTS, encoding="utf-8")
    done = run_with_plugin([str(tmp_path / "test_rules.py")], "pe_p16_rules", tmp_path)
    got = outcomes(done.stdout)
    # session 的 fixture 不能用 function 的 fixture
    assert got["test_scope_mismatch"] == got["test_scope_mismatch_tmp"] == ["ERROR"]
    assert ("You tried to access the function scoped fixture monkeypatch "
            "with a session scoped request object") in done.stdout
    assert "function scoped fixture tmp_path" in done.stdout
    # 直接改 os.environ，下一个测试还看得见
    assert got["test_leak_b"] == ["FAILED"]
    # 测试失败了，yield 后面照样执行
    assert got["test_fails"] == ["FAILED"] and got["test_after_fails"] == ["PASSED"]
    # yield 前面就出错了，yield 后面不会执行
    assert got["test_broken"] == ["ERROR"] and got["test_after_broken"] == ["PASSED"]
