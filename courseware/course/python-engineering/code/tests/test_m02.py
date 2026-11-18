"""M2 模块的测试。

两种用途：
  1. 验证参考答案（ch02_01_solution）本身是对的
  2. 检查你的练习（ch02_01_exercise）做得对不对 —— 没做完的题会显示 skip

跑法：
    pytest tests/test_m02.py -v
    pytest tests/test_m02.py -k ch02_01 -v
"""

from __future__ import annotations

import os
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

from m02_testing import ch02_01_example as example
from m02_testing import ch02_01_exercise as exercise
from m02_testing import ch02_01_solution as solution
from m02_testing import ch02_02_example as example22
from m02_testing import ch02_02_exercise as ex22
from m02_testing import ch02_02_solution as sol22
from m02_testing import ch02_03_example as example23
from m02_testing import ch02_03_exercise as ex23
from m02_testing import ch02_03_solution as sol23

CODE_DIR = Path(__file__).resolve().parents[1]

# ============================================================================
# 工具：练习还没做的题自动 skip，而不是报 fail
# ============================================================================


def run_or_skip(fn: Callable[..., Any], *args: Any) -> Any:
    """调用练习里的函数。遇到 NotImplementedError 就跳过这条测试。"""
    try:
        return fn(*args)
    except NotImplementedError:
        pytest.skip(f"{fn.__name__} 还没完成")


# ============================================================================
# 示例代码的测试：讲解里的结论必须站得住
# ============================================================================


def test_ch02_01_example_check_num() -> None:
    """讲解第 2 节：check_num 的三个场景。"""
    assert example.check_num(30, 50) == "小了"
    assert example.check_num(50, 50) == "正确"
    assert example.check_num(70, 50) == "大了"


def test_ch02_01_example_assert_message_in_plain_python() -> None:
    """讲解第 3 节：纯 Python 下，不带消息的 AssertionError 里什么都没有。

    必须开子进程验证，不能直接写在这个测试函数里 ——
    pytest 会重写本文件里的所有 assert（见下一条测试）。
    """
    code = (
        "from m02_testing.ch02_01_example import check_num\n"
        "try:\n"
        "    assert check_num(30, 50) == '大了'\n"
        "except AssertionError as e:\n"
        "    print('args =', repr(e.args))\n"
        "try:\n"
        "    r = check_num(30, 50)\n"
        "    assert r == '大了', f'预期 大了，实际得到 {r}'\n"
        "except AssertionError as e:\n"
        "    print('msg  =', e)\n"
    )
    done = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        encoding="utf-8",
        env={**os.environ, "PYTHONUTF8": "1"},
        check=True,
    )
    assert "args = ()" in done.stdout, f"实际输出: {done.stdout}"
    assert "msg  = 预期 大了，实际得到 小了" in done.stdout


def test_ch02_01_example_pytest_rewrites_assertions() -> None:
    """pytest 会改写 assert，自动补上两边的值。

    所以在 pytest 里，即使不写消息，失败信息也很详细。
    这是 pytest 的「断言重写」机制，不是 Python 本身的行为。
    """
    with pytest.raises(AssertionError) as caught:
        assert example.check_num(30, 50) == "大了"

    # 纯 Python 下这里是 ()，pytest 下它被塞进了详细的比较结果
    assert caught.value.args != (), "pytest 应该补上了断言详情"
    detail = caught.value.args[0]
    assert "小了" in detail and "大了" in detail, f"实际内容: {detail!r}"


def test_ch02_01_example_always_true_assert() -> None:
    """讲解第 5 节：恒为真的断言为什么无效。

    check_num 的三个返回值都是非空字符串，所以 `assert check_num(...)`
    对任何输入都通过，哪怕实现完全写反。
    """
    for returned in ("小了", "正确", "大了"):
        assert bool(returned) is True


def test_ch02_01_example_raise_version_validates() -> None:
    """讲解第 4 节：raise 版本的校验在普通模式下生效。"""
    assert example.parse_age_right("30") == 30
    with pytest.raises(ValueError, match="年龄不合法"):
        example.parse_age_right("200")


def test_ch02_01_example_assert_removed_under_optimize() -> None:
    """讲解第 4 节的核心结论：-O 模式下 assert 校验失效。

    这条测试真的开一个 -O 子进程来验证，而不是只看字节码。
    """
    code = (
        "from m02_testing.ch02_01_example import parse_age_wrong, parse_age_right;"
        "print('assert 版:', parse_age_wrong('200'));"
    )
    done = subprocess.run(
        [sys.executable, "-O", "-c", code],
        capture_output=True,
        text=True,
        check=False,
    )
    # -O 下 assert 被删除，200 这个非法年龄被原样放过
    assert done.returncode == 0, f"预期 -O 下不报错，实际 stderr: {done.stderr}"
    assert "assert 版: 200" in done.stdout

    # 同一份输入，普通模式会被拦住
    done_normal = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        check=False,
    )
    assert done_normal.returncode != 0
    assert "AssertionError" in done_normal.stderr


def test_ch02_01_example_raise_survives_optimize() -> None:
    """对比：raise 版本在 -O 下依然拦得住。"""
    code = (
        "from m02_testing.ch02_01_example import parse_age_right;"
        "parse_age_right('200')"
    )
    done = subprocess.run(
        [sys.executable, "-O", "-c", code],
        capture_output=True,
        text=True,
        check=False,
    )
    assert done.returncode != 0
    assert "ValueError" in done.stderr


# ============================================================================
# 参考答案的测试
# ============================================================================


def test_ch02_01_solution_leap_year() -> None:
    solution.test_is_leap_year()
    solution.test_fixed()
    solution.test_format_leap_year_message()


def test_ch02_01_solution_catches_broken_impl(monkeypatch: pytest.MonkeyPatch) -> None:
    """练习 3 的核心：参考答案的测试能不能发现被改错的实现。

    这是整章最重要的一条测试 —— 它验证「测试本身有效」。
    """

    def broken_is_leap_year(year: int) -> bool:
        # 故意改错：!= 改成 ==
        return (year % 4 == 0 and year % 100 == 0) or year % 400 == 0

    monkeypatch.setattr(solution, "is_leap_year", broken_is_leap_year)

    with pytest.raises(AssertionError):
        solution.test_is_leap_year()


def test_ch02_01_solution_two_cases_miss_the_400_bug(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """练习 3 第 (2) 问：只测 2024 和 2023 会漏掉什么。

    把 `% 400 == 0` 改成 `% 400 == 1`，两个正常值用例察觉不到，
    必须靠 2000 / 1600 这类边界用例才能发现。
    """

    def broken_400(year: int) -> bool:
        return (year % 4 == 0 and year % 100 != 0) or year % 400 == 1

    # 只有正常值的「弱测试」：察觉不到
    assert broken_400(2024) is True
    assert broken_400(2023) is False

    # 边界值用例：立刻暴露
    assert broken_400(2000) is False, "改错后 2000 被判成平年"
    monkeypatch.setattr(solution, "is_leap_year", broken_400)
    with pytest.raises(AssertionError):
        solution.test_is_leap_year()


# ============================================================================
# 练习的测试：没做完会 skip
# ============================================================================


def test_ch02_01_exercise_1() -> None:
    """练习 1：你写的 test_is_leap_year 必须通过。"""
    run_or_skip(exercise.test_is_leap_year)


def test_ch02_01_exercise_2() -> None:
    """练习 2：你改对的三条断言必须通过。"""
    run_or_skip(exercise.test_fixed)


def test_ch02_01_exercise_3_answered() -> None:
    """练习 3：两个问题都要写上答案。

    判断依据很简单：模板里「答：」后面是空的。只要还有这样的空行，
    就说明那一问没答。
    """
    unanswered = [
        line
        for line in exercise.EXERCISE_3_ANSWER.splitlines()
        if line.strip() in ("答：", "答:")
    ]
    if unanswered:
        pytest.skip(f"练习 3 还有 {len(unanswered)} 个问题没回答")


def test_ch02_01_exercise_4_pure_function() -> None:
    """练习 4：拆出来的纯函数要能直接断言。"""
    msg = run_or_skip(exercise.format_leap_year_message, 2024)
    assert "2024" in msg, "返回的文字里应该包含年份"
    assert "是闰年" in msg, "2024 是闰年，文字里应该说明这一点"

    msg_2023 = exercise.format_leap_year_message(2023)
    assert "不是闰年" in msg_2023, "2023 不是闰年"


def test_ch02_01_exercise_4_has_test() -> None:
    """练习 4：你自己写的测试也要能通过。"""
    run_or_skip(exercise.test_format_leap_year_message)


def test_ch02_01_exercise_broken_asserts_still_pass() -> None:
    """对照用：原题那三条无效断言在当前实现下是通过的。

    这正是它们危险的地方 —— 看起来「测试通过」，实际没有验证力。
    这个函数要求保留原样，所以它应该一直通过。
    """
    exercise.test_broken()


# ============================================================================
# 通用工具（2.2 / 2.3）
# ============================================================================


def actual_repr(expr: str) -> str:
    """表达式的真实结果：值用 repr，报错用异常名。和 test_m01 里的同名函数一致。"""
    try:
        return repr(eval(expr))
    except Exception as e:  # noqa: BLE001
        return type(e).__name__


def run_snippet_lines(code: str) -> str:
    done = subprocess.run(
        [sys.executable, "-c", code], capture_output=True, text=True, encoding="utf-8",
        env={**os.environ, "PYTHONUTF8": "1"}, check=False,
    )
    return done.stdout + done.stderr


# ============================================================================
# 2.2 异常体系与 raise
# ============================================================================


@pytest.mark.parametrize("expr", list(sol22.PREDICTIONS))
def test_ch02_02_solution_predictions(expr: str) -> None:
    assert sol22.PREDICTIONS[expr] == actual_repr(expr), f"{expr} 的答案写错了"


def test_ch02_02_requests_json_error_is_both() -> None:
    """讲解第 4 节：requests 的 JSONDecodeError 同时继承 RequestException 和 ValueError。"""
    import requests

    cls = requests.exceptions.JSONDecodeError
    assert issubclass(cls, requests.exceptions.RequestException)
    assert issubclass(cls, ValueError)
    assert issubclass(cls, OSError), "RequestException 本身继承自 OSError"


def test_ch02_02_except_order_dead_branch() -> None:
    assert example22.parse_response_buggy("<html>") == "请求失败"
    assert example22.parse_response_fixed("<html>") == "响应格式不对"


def test_ch02_02_except_order_not_flagged_by_tools(tmp_path: Path) -> None:
    """讲解第 4 节：except 顺序写反，课程用的 ruff 规则集和 mypy 都不会提示。"""
    src = tmp_path / "order.py"
    src.write_text(
        "def describe(action: object) -> str:\n"
        "    try:\n        pass\n"
        "    except OSError:\n        return '其他 IO 错误'\n"
        "    except FileNotFoundError:\n        return '文件不存在'\n"
        "    return '成功'\n",
        encoding="utf-8",
    )
    ruff = subprocess.run(
        [sys.executable, "-m", "ruff", "check", str(src), "--no-cache",
         "--select", "F,E,W,N,UP,SIM"],
        capture_output=True, text=True, check=False,
    )
    assert ruff.returncode == 0, ruff.stdout
    mypy = subprocess.run(
        [sys.executable, "-m", "mypy", str(src), "--warn-unreachable", "--no-error-summary"],
        capture_output=True, text=True, check=False,
    )
    assert mypy.stdout.strip() == "", mypy.stdout


def test_ch02_02_raise_class_needing_args() -> None:
    out = run_snippet_lines("import json\nraise json.JSONDecodeError")
    assert "TypeError: JSONDecodeError.__init__() missing 3 required positional arguments" in out


@pytest.mark.parametrize(
    ("form", "link", "shows_original"),
    [
        ("", "During handling of the above exception, another exception occurred", True),
        (" from e", "The above exception was the direct cause of the following exception", True),
        (" from None", None, False),
    ],
)
def test_ch02_02_chaining_tracebacks(form: str, link: str | None, shows_original: bool) -> None:
    code = ("try:\n    int('abc')\nexcept ValueError as e:\n"
            f"    raise RuntimeError('解析配置失败'){form}")
    out = run_snippet_lines(code)
    assert ("ValueError: invalid literal" in out) is shows_original
    if link:
        assert link in out
    assert "RuntimeError: 解析配置失败" in out, "from None 只改变显示，异常照样抛"


@pytest.mark.parametrize(
    ("form", "cause", "suppress"),
    [("", None, False), (" from e", ValueError, True), (" from None", None, True)],
)
def test_ch02_02_chaining_attributes(
    form: str, cause: type[BaseException] | None, suppress: bool
) -> None:
    code = f"try:\n    int('abc')\nexcept ValueError as e:\n    raise RuntimeError('x'){form}"
    with pytest.raises(RuntimeError) as excinfo:
        exec(code)
    err = excinfo.value
    assert (type(err.__cause__) if err.__cause__ else None) is cause
    assert isinstance(err.__context__, ValueError), "三种写法 __context__ 都会被记录"
    assert err.__suppress_context__ is suppress


def test_ch02_02_raise_e_keeps_original_frame() -> None:
    """讲解第 3 节的更正：Python 3 里 raise e 不会丢掉原始出错位置，只是多一层。"""
    base = "def inner():\n    int('abc')\ndef outer():\n    try:\n        inner()\n"
    bare = run_snippet_lines(base + "    except ValueError:\n        raise\nouter()")
    named = run_snippet_lines(base + "    except ValueError as e:\n        raise e\nouter()")
    assert "line 2, in inner" in bare and "line 2, in inner" in named
    assert named.count('File "') == bare.count('File "') + 1
    assert "raise e" in named


def test_ch02_02_catching_own_raise() -> None:
    for raw in ("abc", "101"):
        with pytest.raises(ValueError, match="输入格式错误"):
            example22.parse_wrong(raw)


def test_ch02_02_example_parse_guess() -> None:
    assert example22.parse_guess("42") == 42
    with pytest.raises(example22.GuessFormatError):
        example22.parse_guess("abc")
    with pytest.raises(example22.GuessRangeError) as excinfo:
        example22.parse_guess("101")
    assert excinfo.value.value == 101
    assert (excinfo.value.low, excinfo.value.high) == (1, 100)
    with pytest.raises(ValueError):
        example22.parse_guess("0")  # 继承 ValueError：老代码照样接得住


def test_ch02_02_example_play() -> None:
    it = iter(["abc", "101", "50", "42"])
    lines: list[str] = []
    history = example22.play(42, ask=lambda _p: next(it), say=lines.append)
    assert history == [50, 42]
    assert "   'abc' 不是整数，这次不算" in lines
    assert "   101 不在 1-100 之间，这次不算" in lines


def test_ch02_02_example_runs() -> None:
    done = subprocess.run(
        [sys.executable, "-m", "m02_testing.ch02_02_example"], cwd=CODE_DIR,
        capture_output=True, text=True, encoding="utf-8",
        env={**os.environ, "PYTHONUTF8": "1"}, check=False,
    )
    assert done.returncode == 0, done.stderr
    assert "顺序写反 → '请求失败'" in done.stdout


def test_ch02_02_solution_parse_guess() -> None:
    assert sol22.parse_guess("42") == 42
    assert sol22.parse_guess("1") == 1 and sol22.parse_guess("100") == 100
    with pytest.raises(sol22.GuessFormatError, match="abc") as fmt:
        sol22.parse_guess("abc")
    assert fmt.value.__suppress_context__ is True
    with pytest.raises(sol22.GuessRangeError, match="101"):
        sol22.parse_guess("101")
    assert issubclass(sol22.GuessFormatError, sol22.GuessError)
    assert issubclass(sol22.GuessError, ValueError)


def open_missing_file() -> None:
    with open("这个文件一定不存在-pe-course.txt", encoding="utf-8"):
        pass


def raise_permission_error() -> None:
    raise PermissionError("拒绝访问")


def raise_key_error() -> None:
    empty: dict[str, int] = {}
    empty["k"]


DESCRIBE_CASES: list[tuple[Callable[[], object], str]] = [
    (open_missing_file, "文件不存在"),
    (raise_permission_error, "其他 IO 错误"),
    (lambda: int("abc"), "格式错误"),
    (lambda: None, "成功"),
]


@pytest.mark.parametrize(("action", "expected"), DESCRIBE_CASES)
def test_ch02_02_solution_describe_failure(action: Callable[[], object], expected: str) -> None:
    assert sol22.describe_failure(action) == expected


def test_ch02_02_buggy_describe_failure() -> None:
    assert sol22.describe_failure_buggy(DESCRIBE_CASES[0][0]) == "其他 IO 错误"


def test_ch02_02_solution_describe_failure_lets_others_through() -> None:
    with pytest.raises(KeyError):
        sol22.describe_failure(raise_key_error)


def test_ch02_02_solution_expect_raises() -> None:
    err = sol22.expect_raises(sol22.GuessRangeError, sol22.parse_guess, "101")
    assert isinstance(err, sol22.GuessRangeError)
    # 子类也算
    assert isinstance(sol22.expect_raises(ValueError, sol22.parse_guess, "abc"), ValueError)
    with pytest.raises(AssertionError, match="预期 ValueError，但没有抛出"):
        sol22.expect_raises(ValueError, sol22.parse_guess, "42")
    with pytest.raises(sol22.GuessFormatError):
        sol22.expect_raises(sol22.GuessRangeError, sol22.parse_guess, "abc")


# --- 练习 ---


def test_ch02_02_exercise_1_predictions() -> None:
    unanswered = [k for k, v in ex22.PREDICTIONS.items() if v is None]
    if unanswered:
        pytest.skip(f"练习 1 还有 {len(unanswered)} 条没填")
    wrong = [f"  {k:<46} 你写 {v!r:<8} 实际 {actual_repr(k)!r}"
             for k, v in ex22.PREDICTIONS.items() if v != actual_repr(k)]
    assert not wrong, "猜错的：\n" + "\n".join(wrong)


def test_ch02_02_exercise_2_hierarchy() -> None:
    if not issubclass(ex22.GuessError, ValueError):
        pytest.skip("练习 2 还没完成（GuessError 还不是 ValueError 的子类）")
    assert issubclass(ex22.GuessFormatError, ex22.GuessError)
    assert issubclass(ex22.GuessRangeError, ex22.GuessError)


def test_ch02_02_exercise_2_parse_guess() -> None:
    assert run_or_skip(ex22.parse_guess, "42") == 42
    assert ex22.parse_guess("1") == 1 and ex22.parse_guess("100") == 100, "边界要算合法"
    with pytest.raises(ex22.GuessFormatError, match="abc") as fmt:
        ex22.parse_guess("abc")
    assert fmt.value.__suppress_context__ is True, "格式错误要用 from None 隐藏原来的 ValueError"
    try:
        ex22.parse_guess("101")
    except ex22.GuessRangeError as e:
        assert "101" in str(e), "范围错误的消息里要包含那个数字"
    except ex22.GuessFormatError:
        pytest.fail("101 被报成了格式错误 —— 你自己 raise 的异常是不是被 except ValueError 接住了？")
    else:
        pytest.fail("parse_guess('101') 没有抛出异常")


@pytest.mark.parametrize(("action", "expected"), DESCRIBE_CASES)
def test_ch02_02_exercise_3_describe_failure(
    action: Callable[[], object], expected: str
) -> None:
    assert run_or_skip(ex22.describe_failure, action) == expected


def test_ch02_02_exercise_3_lets_others_through() -> None:
    run_or_skip(ex22.describe_failure, lambda: None)
    with pytest.raises(KeyError):
        ex22.describe_failure(raise_key_error)


def test_ch02_02_exercise_4_expect_raises() -> None:
    def boom() -> None:
        raise ValueError("x")

    err = run_or_skip(ex22.expect_raises, ValueError, boom)
    assert isinstance(err, ValueError), "要返回捕获到的异常对象"
    with pytest.raises(AssertionError):
        ex22.expect_raises(ValueError, lambda: 42)
    with pytest.raises(KeyError):
        ex22.expect_raises(ValueError, raise_key_error)


# ============================================================================
# 2.3 从 assert 到 pytest
# ============================================================================

# 4 个「故意改错」的 parse_guess。第 2.3 章练习 1-3 写的测试，必须每个都能抓住。
MUTANT_PLUGIN = '''
import importlib
import os

import pytest

TARGET = os.environ["PE_MUTANT_TARGET"]
MUTANT = os.environ["PE_MUTANT_NAME"]


def _make(mod):
    fmt_err, range_err = mod.GuessFormatError, mod.GuessRangeError

    def lower_bound(raw, low=1, high=100):
        try:
            n = int(raw)
        except ValueError:
            raise fmt_err(f"{raw!r} 不是整数") from None
        if not low < n <= high:
            raise range_err(f"数字必须在 [{low}, {high}] 之间，你输入的是 {n}")
        return n

    def upper_bound(raw, low=1, high=100):
        try:
            n = int(raw)
        except ValueError:
            raise fmt_err(f"{raw!r} 不是整数") from None
        if not low <= n < high:
            raise range_err(f"数字必须在 [{low}, {high}] 之间，你输入的是 {n}")
        return n

    def plain_value_error(raw, low=1, high=100):
        n = int(raw)
        if not low <= n <= high:
            raise range_err(f"数字必须在 [{low}, {high}] 之间，你输入的是 {n}")
        return n

    def message_changed(raw, low=1, high=100):
        try:
            n = int(raw)
        except ValueError:
            raise fmt_err(f"{raw!r} 不是整数") from None
        if not low <= n <= high:
            raise range_err(f"数字必须在 {low} 到 {high} 之间，你输入的是 {n}")
        return n

    return {
        "lower_bound": lower_bound,
        "upper_bound": upper_bound,
        "plain_value_error": plain_value_error,
        "message_changed": message_changed,
    }[MUTANT]


@pytest.fixture(autouse=True)
def _swap_in_mutant(monkeypatch):
    mod = importlib.import_module(TARGET)
    monkeypatch.setattr(mod, "parse_guess", _make(mod))
'''

MUTANTS = {
    "lower_bound": "下边界改错（1 被拒绝）",
    "upper_bound": "上边界改错（100 被拒绝）",
    "plain_value_error": "格式错误抛成了普通 ValueError",
    "message_changed": "错误消息改成了「数字必须在 1 到 100 之间」",
}


def run_learner_tests(
    module: str, tmp_path: Path, mutant: str | None = None
) -> subprocess.CompletedProcess[str]:
    """用 pytest 跑某个练习文件。mutant 不为 None 时，先把 parse_guess 换成改错的版本。"""
    path = "m02_testing/" + module.split(".")[-1] + ".py"
    args = [sys.executable, "-m", "pytest", path, "-q", "-p", "no:cacheprovider", "--tb=no"]
    env = {**os.environ, "PYTHONUTF8": "1"}
    if mutant is not None:
        (tmp_path / "pe_mutant_plugin.py").write_text(MUTANT_PLUGIN, encoding="utf-8")
        args += ["-p", "pe_mutant_plugin"]
        env["PYTHONPATH"] = os.pathsep.join([str(tmp_path), str(CODE_DIR)])
        env["PE_MUTANT_TARGET"] = module
        env["PE_MUTANT_NAME"] = mutant
    return subprocess.run(args, cwd=CODE_DIR, capture_output=True, text=True,
                          encoding="utf-8", env=env, check=False)


@pytest.fixture(scope="module")
def discovery_truth(tmp_path_factory: pytest.TempPathFactory) -> dict[str, bool]:
    """真的搭一遍 names/ 目录、跑一遍 pytest --collect-only，得到标准答案。"""
    root = tmp_path_factory.mktemp("discovery")
    example23.build_lab(root)
    done = example23.pytest_in(root, "names", "--collect-only", "-q")
    collected = {line.strip() for line in done.stdout.splitlines() if "::" in line}
    nodes = {
        "test_names.py 里的 test_ok": "names/test_names.py::test_ok",
        "test_names.py 里的 check_test": "names/test_names.py::check_test",
        "test_names.py 里的 testing_data": "names/test_names.py::testing_data",
        "test_names.py 里的 Test_upper": "names/test_names.py::Test_upper",
        "TestGame 类里的 test_inside_class": "names/test_names.py::TestGame::test_inside_class",
        "GameTest 类里的 test_in_wrong_class":
            "names/test_names.py::GameTest::test_in_wrong_class",
        "TestWithInit 类（有 __init__）里的 test_never_collected":
            "names/test_names.py::TestWithInit::test_never_collected",
        "game_test.py 里的 test_in_suffix_file": "names/game_test.py::test_in_suffix_file",
        "tests_game.py 里的 test_in_tests_prefix_file":
            "names/tests_game.py::test_in_tests_prefix_file",
        "checks.py 里的 test_in_plain_file": "names/checks.py::test_in_plain_file",
    }
    return {key: node in collected for key, node in nodes.items()}


def test_ch02_03_solution_discovery(discovery_truth: dict[str, bool]) -> None:
    assert discovery_truth == sol23.DISCOVERY


def test_ch02_03_testing_prefix_is_collected(discovery_truth: dict[str, bool]) -> None:
    """讲解第 3 节最反直觉的一条：testing_data 会被当成测试。"""
    assert discovery_truth["test_names.py 里的 testing_data"] is True


def test_ch02_03_main_guard_collects_nothing(tmp_path: Path) -> None:
    """讲解第 2 节：断言写在 if __name__ 里，collected 0 items，退出码 5。"""
    example23.build_lab(tmp_path)
    done = example23.pytest_in(tmp_path, "main_guard", "-q")
    assert done.returncode == 5
    assert "no tests ran" in done.stdout


def test_ch02_03_explicit_path_collects_any_name(tmp_path: Path) -> None:
    example23.build_lab(tmp_path)
    done = example23.pytest_in(tmp_path, "names/checks.py", "--collect-only", "-q")
    assert "names/checks.py::test_in_plain_file" in done.stdout


def test_ch02_03_loop_hides_later_failures(tmp_path: Path) -> None:
    """讲解第 4 节：循环里的 assert 只报第一个失败，参数化全部报出。"""
    example23.build_lab(tmp_path)
    done = example23.pytest_in(tmp_path, "behaviour", "-q", "--tb=no", "-rf")
    failed = [line for line in done.stdout.splitlines() if line.startswith("FAILED")]
    loop = [line for line in failed if "test_loop" in line]
    param = [line for line in failed if "test_parametrized" in line]
    assert len(loop) == 1 and "50 == 999" in loop[0]
    assert len(param) == 2


def test_ch02_03_match_is_regex(tmp_path: Path) -> None:
    example23.build_lab(tmp_path)
    done = example23.pytest_in(
        tmp_path, "behaviour/test_behaviour.py::test_match_is_regex", "-q", "--tb=short"
    )
    assert done.returncode == 1
    assert "Regex pattern did not match" in done.stdout


def test_ch02_03_example_self_tests_pass() -> None:
    """示例文件本身的样板测试应该全部通过。"""
    done = subprocess.run(
        [sys.executable, "-m", "pytest", "m02_testing/ch02_03_example.py", "-q",
         "-p", "no:cacheprovider"],
        cwd=CODE_DIR, capture_output=True, text=True, encoding="utf-8", check=False,
    )
    assert done.returncode == 0, done.stdout
    assert "13 passed" in done.stdout


def test_ch02_03_example_runs() -> None:
    done = subprocess.run(
        [sys.executable, "-m", "m02_testing.ch02_03_example"], cwd=CODE_DIR,
        capture_output=True, text=True, encoding="utf-8",
        env={**os.environ, "PYTHONUTF8": "1"}, check=False,
    )
    assert done.returncode == 0, done.stderr
    assert "退出码：5" in done.stdout
    assert "names/test_names.py::testing_data" in done.stdout


def test_ch02_03_solution_tests_pass(tmp_path: Path) -> None:
    done = run_learner_tests("m02_testing.ch02_03_solution", tmp_path)
    assert done.returncode == 0, done.stdout


@pytest.mark.parametrize("mutant", list(MUTANTS))
def test_ch02_03_solution_kills_mutant(mutant: str, tmp_path: Path) -> None:
    done = run_learner_tests("m02_testing.ch02_03_solution", tmp_path, mutant)
    assert done.returncode == 1, f"参考答案没抓住「{MUTANTS[mutant]}」：\n{done.stdout}"


def test_ch02_03_mutants_pass_a_weak_suite(tmp_path: Path) -> None:
    """对照：只测中间值、只断言基类的「弱测试」，4 个改错版本全都能混过去。

    这证明了改错版本本身不是「随便什么测试都能抓住」的 —— 它们确实在考验测试的质量。
    """
    weak = tmp_path / "weak_suite.py"
    # 注意用 m.parse_guess 而不是 from ... import parse_guess：
    # 后者在导入时就把原函数绑定到了本地名字上，改错插件的替换对它不起作用，
    # 「改错版本没被抓住」就会变成一个虚假的结论。
    weak.write_text(
        "import pytest\n"
        "import m02_testing.ch02_03_solution as m\n"
        "def test_middle():\n    assert m.parse_guess('42') == 42\n"
        "def test_bad():\n"
        "    with pytest.raises(ValueError):\n        m.parse_guess('abc')\n",
        encoding="utf-8",
    )
    (tmp_path / "pe_mutant_plugin.py").write_text(MUTANT_PLUGIN, encoding="utf-8")
    survived = []
    for mutant in MUTANTS:
        env = {**os.environ, "PYTHONUTF8": "1",
               "PYTHONPATH": os.pathsep.join([str(tmp_path), str(CODE_DIR)]),
               "PE_MUTANT_TARGET": "m02_testing.ch02_03_solution", "PE_MUTANT_NAME": mutant}
        done = subprocess.run(
            [sys.executable, "-m", "pytest", str(weak), "-q", "-p", "no:cacheprovider",
             "-p", "pe_mutant_plugin", "--rootdir", str(tmp_path)],
            cwd=CODE_DIR, capture_output=True, text=True, encoding="utf-8", env=env,
            check=False,
        )
        if done.returncode == 0:
            survived.append(mutant)
    assert survived == list(MUTANTS)


# --- 练习 ---


def test_ch02_03_exercise_tests_pass(tmp_path: Path) -> None:
    done = run_learner_tests("m02_testing.ch02_03_exercise", tmp_path)
    if done.returncode == 5:
        pytest.skip("练习 1-3 还没写测试（collected 0 items）")
    assert done.returncode == 0, (
        "你写的测试在「正确的 parse_guess」上就失败了 —— 先让它们本身通过：\n" + done.stdout
    )


@pytest.mark.parametrize("mutant", list(MUTANTS))
def test_ch02_03_exercise_kills_mutant(mutant: str, tmp_path: Path) -> None:
    normal = run_learner_tests("m02_testing.ch02_03_exercise", tmp_path)
    if normal.returncode == 5:
        pytest.skip("练习 1-3 还没写测试（collected 0 items）")
    if normal.returncode != 0:
        pytest.skip("你的测试在正确版本上就没通过，先修那个")
    done = run_learner_tests("m02_testing.ch02_03_exercise", tmp_path, mutant)
    assert done.returncode == 1, (
        f"你的测试没抓住「{MUTANTS[mutant]}」这个改错版本 —— 它在你的测试下全部通过了。"
    )


def test_ch02_03_exercise_4_discovery(discovery_truth: dict[str, bool]) -> None:
    unanswered = [k for k, v in ex23.DISCOVERY.items() if v is None]
    if unanswered:
        pytest.skip(f"练习 4 还有 {len(unanswered)} 条没填")
    wrong = [f"  {k:<48} 你写 {ex23.DISCOVERY[k]!s:<6} 实际 {v}"
             for k, v in discovery_truth.items() if ex23.DISCOVERY[k] != v]
    assert not wrong, "判断错的：\n" + "\n".join(wrong)
