"""M1 模块的测试。

两种用途：
  1. 验证参考答案和示例里的结论是对的 —— 讲解里写的每一个「运行结果」都在这里复核
  2. 检查你的练习 —— 没做完的题显示 skip

    pytest tests/test_m01.py -v
    pytest tests/test_m01.py -k ch01_02 -v
"""

from __future__ import annotations

import builtins
import os
import subprocess
import sys
from collections.abc import Callable, Iterator
from typing import Any

import pytest

from m01_basics import (
    ch01_01_example,
    ch01_02_example,
    ch01_03_example,
    ch01_04_example,
    ch01_05_example,
    ch01_06_example,
    ch01_07_example,
    ch01_08_example,
    ch01_09_example,
)
from m01_basics import ch01_01_exercise as ex1
from m01_basics import ch01_01_solution as sol1
from m01_basics import ch01_02_exercise as ex2
from m01_basics import ch01_02_solution as sol2
from m01_basics import ch01_03_exercise as ex3
from m01_basics import ch01_03_solution as sol3
from m01_basics import ch01_04_exercise as ex4
from m01_basics import ch01_04_solution as sol4
from m01_basics import ch01_05_exercise as ex5
from m01_basics import ch01_05_solution as sol5
from m01_basics import ch01_06_exercise as ex6
from m01_basics import ch01_06_solution as sol6
from m01_basics import ch01_07_exercise as ex7
from m01_basics import ch01_07_solution as sol7
from m01_basics import ch01_08_exercise as ex8
from m01_basics import ch01_08_solution as sol8
from m01_basics import ch01_09_exercise as ex9
from m01_basics import ch01_09_solution as sol9

# ============================================================================
# 工具
# ============================================================================


def run_or_skip(fn: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
    """调用练习里的函数。遇到 NotImplementedError 就跳过这条测试。"""
    try:
        return fn(*args, **kwargs)
    except NotImplementedError:
        pytest.skip(f"{fn.__name__} 还没完成")


def actual_repr(expr: str) -> str:
    """表达式的真实结果，按 PREDICTIONS 的填法格式化：值用 repr，报错用异常名。"""
    try:
        return repr(eval(expr))
    except Exception as e:  # noqa: BLE001
        return type(e).__name__


def run_module(*args: str) -> subprocess.CompletedProcess[str]:
    """用 python -m 跑一个模块，捕获输出。"""
    return subprocess.run(
        [sys.executable, "-m", *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        env={**os.environ, "PYTHONUTF8": "1"},
        check=False,
    )


@pytest.fixture
def fake_input(monkeypatch: pytest.MonkeyPatch) -> Callable[[list[str]], None]:
    """把 input() 换成按顺序返回预设值的假函数。

    这是第 8.1 章 Mock 的一个简化版。现在不需要看懂它，
    只需知道：它让需要键盘输入的函数也能自动测试。
    """

    def install(answers: list[str]) -> None:
        it: Iterator[str] = iter(answers)
        monkeypatch.setattr(builtins, "input", lambda _prompt="": next(it))

    return install


# ============================================================================
# 1.1 程序的三种结构与输入输出
# ============================================================================


@pytest.mark.parametrize("expr", list(sol1.PREDICTIONS))
def test_ch01_01_solution_predictions(expr: str) -> None:
    """参考答案里每一条预测都必须和真实运行结果一致。"""
    assert sol1.PREDICTIONS[expr] == actual_repr(expr), f"{expr} 的答案写错了"


def test_ch01_01_solution_check_num() -> None:
    assert sol1.check_num(3, 10) == "小了"
    assert sol1.check_num(10, 10) == "正确"
    assert sol1.check_num(30, 10) == "大了"


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("q", True), ("Q", True), (" q ", True), ("quit", True), ("QUIT  ", True),
        ("\tQuit\n", True),
        ("", False), ("qq", False), ("exit", False), ("42", False), ("q uit", False),
    ],
)
def test_ch01_01_solution_is_quit(raw: str, expected: bool) -> None:
    assert sol1.is_quit(raw) is expected


def test_ch01_01_example_play_v1(
    fake_input: Callable[[list[str]], None], capsys: pytest.CaptureFixture[str]
) -> None:
    fake_input(["3"])
    ch01_01_example.play_v1()
    assert "小了" in capsys.readouterr().out


def test_ch01_01_example_play_v1_crashes_on_text(
    fake_input: Callable[[list[str]], None],
) -> None:
    """讲解的结论：第一版输入 abc 会直接崩。"""
    fake_input(["abc"])
    with pytest.raises(ValueError, match="invalid literal"):
        ch01_01_example.play_v1()


def test_ch01_01_example_runs() -> None:
    done = run_module("m01_basics.ch01_01_example")
    assert done.returncode == 0, done.stderr
    assert "'9' > '10'   → True" in done.stdout
    assert "'181818'" in done.stdout


# --- 练习 ---


def test_ch01_01_exercise_1_predictions() -> None:
    unanswered = [k for k, v in ex1.PREDICTIONS.items() if v is None]
    if unanswered:
        pytest.skip(f"练习 1 还有 {len(unanswered)} 条没填")
    wrong = {
        expr: (guess, actual_repr(expr))
        for expr, guess in ex1.PREDICTIONS.items()
        if guess != actual_repr(expr)
    }
    assert not wrong, "猜错的（你的答案, 真实结果）：\n" + "\n".join(
        f"  {k:<16} 你写 {g!r:<14} 实际 {a!r}" for k, (g, a) in wrong.items()
    )


def test_ch01_01_exercise_2_check_num() -> None:
    assert run_or_skip(ex1.check_num, 3, 10) == "小了"
    assert ex1.check_num(10, 10) == "正确"
    assert ex1.check_num(30, 10) == "大了"
    assert ex1.check_num(-1, 0) == "小了", "负数也要能比"


def test_ch01_01_exercise_3_is_quit() -> None:
    run_or_skip(ex1.is_quit, "q")
    for raw in ("q", "Q", " q ", "quit", "QUIT  ", "\tQuit\n"):
        assert ex1.is_quit(raw) is True, f"{raw!r} 应该识别为退出"
    for raw in ("", "qq", "exit", "42", "q uit"):
        assert ex1.is_quit(raw) is False, f"{raw!r} 不应该识别为退出"


# ============================================================================
# 1.2 条件分支与真值测试
# ============================================================================


@pytest.mark.parametrize("expr", list(sol2.PREDICTIONS))
def test_ch01_02_solution_predictions(expr: str) -> None:
    assert sol2.PREDICTIONS[expr] == actual_repr(expr), f"{expr} 的答案写错了"


def test_ch01_02_solution_classify() -> None:
    assert sol2.classify(50, 42) == "大了"
    assert sol2.classify(42, 42) == "正确"
    assert sol2.classify(0, 42) == "超出范围"
    assert sol2.classify(101, 42) == "超出范围"
    # 边界：两端都包含
    assert sol2.classify(1, 42) == "小了"
    assert sol2.classify(100, 42) == "大了"
    assert sol2.classify(5, 3, low=3, high=5) == "大了"


# looks_like_int 必须和 int() 一致的输入。
# 下划线（如 "1_000"）故意不放进来 —— 参考答案的注释里说明了它是已知的不一致，
# 那是第 1.5 章引出 EAFP 的伏笔。
INT_CASES = [
    "0", "7", "123", "-5", "+7", " 42", "42 ", "\t-3\n", "007",
    "４２",            # 全角数字：int() 认
    "٣",               # 阿拉伯-印度数字 3：int() 也认
    "", " ", "-", "+", "+-1", "--1", "3.14", "1e3", "abc", "4 2", "²", "³", "一二三",
]


def int_accepts(raw: str) -> bool:
    try:
        int(raw)
    except ValueError:
        return False
    return True


@pytest.mark.parametrize("raw", INT_CASES)
def test_ch01_02_solution_looks_like_int_agrees_with_int(raw: str) -> None:
    assert sol2.looks_like_int(raw) is int_accepts(raw), (
        f"{raw!r}: looks_like_int={sol2.looks_like_int(raw)} 但 int() "
        f"{'能' if int_accepts(raw) else '不能'}转换"
    )


def test_ch01_02_isdigit_disagrees_with_int() -> None:
    """讲解第 4 节的核心结论：isdigit() 和 int() 在两个方向上都不一致。"""
    # 误杀：isdigit 说不行，int 说行
    for raw in ("-5", "+7", " 42"):
        assert raw.isdigit() is False and int_accepts(raw) is True
    # 漏放：isdigit 说行，int 说不行 —— 用 isdigit 做校验的程序会在这里崩溃
    assert "²".isdigit() is True
    assert int_accepts("²") is False
    # isdecimal 修正了漏放
    assert "²".isdecimal() is False


def test_ch01_02_known_gap_underscore() -> None:
    """参考答案注释里记录的已知不一致，留给第 1.5 章。"""
    assert int("1_000") == 1000
    assert sol2.looks_like_int("1_000") is False


def test_ch01_02_solution_format_remaining() -> None:
    assert sol2.format_remaining(None) == "不限次数"
    assert sol2.format_remaining(0) == "剩余 0 次"
    assert sol2.format_remaining(3) == "剩余 3 次"


def test_ch01_02_example_play_v2_crashes_on_superscript(
    fake_input: Callable[[list[str]], None],
) -> None:
    """讲解的结论：用 isdigit 做校验，输入 ² 会崩。"""
    fake_input(["²"])
    with pytest.raises(ValueError):
        ch01_02_example.play_v2()


def test_ch01_02_example_play_v2_rejects_negative(
    fake_input: Callable[[list[str]], None], capsys: pytest.CaptureFixture[str]
) -> None:
    """讲解的结论：用 isdigit 做校验，-5 被误判为非法。"""
    fake_input(["-5"])
    ch01_02_example.play_v2()
    assert "不是整数" in capsys.readouterr().out


def test_ch01_02_example_runs() -> None:
    done = run_module("m01_basics.ch01_02_example")
    assert done.returncode == 0, done.stderr
    assert "type(True) is int" in done.stdout


# --- 练习 ---


def test_ch01_02_exercise_1_predictions() -> None:
    unanswered = [k for k, v in ex2.PREDICTIONS.items() if v is None]
    if unanswered:
        pytest.skip(f"练习 1 还有 {len(unanswered)} 条没填")
    wrong = {
        expr: (guess, actual_repr(expr))
        for expr, guess in ex2.PREDICTIONS.items()
        if guess != actual_repr(expr)
    }
    assert not wrong, "猜错的（你的答案, 真实结果）：\n" + "\n".join(
        f"  {k:<24} 你写 {g!r:<10} 实际 {a!r}" for k, (g, a) in wrong.items()
    )


def test_ch01_02_exercise_2_classify() -> None:
    assert run_or_skip(ex2.classify, 50, 42) == "大了"
    assert ex2.classify(42, 42) == "正确"
    assert ex2.classify(0, 42) == "超出范围", "0 在范围外"
    assert ex2.classify(101, 42) == "超出范围", "101 在范围外"
    assert ex2.classify(1, 42) == "小了", "1 是下边界，应该算在范围内"
    assert ex2.classify(100, 42) == "大了", "100 是上边界，应该算在范围内"


def test_ch01_02_exercise_3_looks_like_int() -> None:
    run_or_skip(ex2.looks_like_int, "1")
    wrong = [raw for raw in INT_CASES if ex2.looks_like_int(raw) is not int_accepts(raw)]
    assert not wrong, "和 int() 判断不一致的输入：\n" + "\n".join(
        f"  {raw!r:<10} 你返回 {ex2.looks_like_int(raw)}，int() "
        f"{'能' if int_accepts(raw) else '不能'}转换"
        for raw in wrong
    )


def test_ch01_02_exercise_4_format_remaining() -> None:
    assert run_or_skip(ex2.format_remaining, None) == "不限次数"
    assert ex2.format_remaining(3) == "剩余 3 次"
    assert ex2.format_remaining(0) == "剩余 0 次", "0 是合法值，表示一次都不剩了"


# ============================================================================
# 1.3 循环与四个「结束」
# ============================================================================


def test_ch01_03_solution_sum_until_zero() -> None:
    assert sol3.sum_until_zero([3, -1, 4, 0, 100]) == 7
    assert sol3.sum_until_zero([]) == 0
    assert sol3.sum_until_zero([0, 5]) == 0
    assert sol3.sum_until_zero([-1, -2]) == 0
    assert sol3.sum_until_zero([1, 2, 3]) == 6


PLAY_CASES = [
    (["50", "abc", "42"], 42, 5, "猜中了，用了 2 次"),
    (["1", "2"], 42, 2, "次数用完"),
    (["1", " Q "], 42, 5, "主动退出"),
    (["1"], 42, 5, "输入结束"),
    ([], 42, 5, "输入结束"),
    (["42"], 42, 1, "猜中了，用了 1 次"),
    # 边界：最后一次机会猜中，必须算猜中，不能先判成次数用完
    (["1", "42"], 42, 2, "猜中了，用了 2 次"),
    # 非整数输入不计次数，所以 3 次机会能撑过 5 条输入
    (["x", "1", "y", "2", "42"], 42, 3, "猜中了，用了 3 次"),
    # 负数和带空格的数字都算有效输入
    ([" -5 ", "42"], 42, 5, "猜中了，用了 2 次"),
]


@pytest.mark.parametrize(("inputs", "target", "max_attempts", "expected"), PLAY_CASES)
def test_ch01_03_solution_play(
    inputs: list[str], target: int, max_attempts: int, expected: str
) -> None:
    assert sol3.play(inputs, target, max_attempts) == expected


def test_ch01_03_solution_play_buggy_raises_system_exit() -> None:
    """sys.exit() 的本质是抛 SystemExit。"""
    with pytest.raises(SystemExit) as caught:
        sol3.play_buggy(["42"], 42)
    assert caught.value.code is None


def test_ch01_03_system_exit_escapes_except_exception() -> None:
    """练习 3 第 (2) 问：except Exception 接不住 SystemExit。"""
    assert not issubclass(SystemExit, Exception)
    assert issubclass(SystemExit, BaseException)

    reached_except = False
    with pytest.raises(SystemExit):
        try:
            sol3.play_buggy(["42"], 42)
        except Exception:
            reached_except = True
    assert reached_except is False


def test_ch01_03_solution_play_fixed() -> None:
    assert sol3.play_fixed(["1", "42"], 42) == "猜中了"
    assert sol3.play_fixed(["1"], 42) == "输入结束"


@pytest.mark.parametrize(
    ("mode", "last_line_printed"),
    [("break", True), ("continue", True), ("exit", False)],
)
def test_ch01_03_example_ending(mode: str, last_line_printed: bool) -> None:
    """讲解里那张「四个结束」表的实测依据。

    重点是 exit 那一行：最后一行没打印，但退出码仍然是 0。
    """
    done = run_module("m01_basics.ch01_03_example", "ending", mode)
    assert done.returncode == 0, "三种方式的退出码都是 0 —— exit 也是"
    assert ("循环结束后" in done.stdout) is last_line_printed
    if mode == "continue":
        assert "第 2 次的循环体后半段" not in done.stdout
        assert "第 3 次尝试" in done.stdout
    if mode == "break":
        assert "第 3 次尝试" not in done.stdout


def test_ch01_03_exit_missing_without_site() -> None:
    """exit 是 site 模块塞进来的；python -S 下不存在。sys.exit 始终存在。"""
    no_site = subprocess.run(
        [sys.executable, "-S", "-c", "exit()"], capture_output=True, text=True, check=False
    )
    assert "NameError" in no_site.stderr

    with_sys = subprocess.run(
        [sys.executable, "-S", "-c", "import sys; sys.exit(3)"],
        capture_output=True, text=True, check=False,
    )
    assert with_sys.returncode == 3


def test_ch01_03_sys_exit_with_message_returns_1() -> None:
    """sys.exit("消息") 会把消息打到 stderr，退出码为 1。"""
    done = subprocess.run(
        [sys.executable, "-c", "import sys; sys.exit('出错了')"],
        capture_output=True, text=True, encoding="utf-8",
        env={**os.environ, "PYTHONUTF8": "1"}, check=False,
    )
    assert done.returncode == 1
    assert "出错了" in done.stderr


@pytest.mark.parametrize(
    ("answers", "expected_lines"),
    [
        (["50", "42"], ["大了", "用了 2 次", "本局结束"]),
        (["abc", "q"], ["不是整数", "你选择了退出", "本局结束"]),
        (["1", "2", "3", "4", "5"], ["次数用完了", "本局结束"]),
    ],
)
def test_ch01_03_example_play_v3(
    fake_input: Callable[[list[str]], None],
    capsys: pytest.CaptureFixture[str],
    answers: list[str],
    expected_lines: list[str],
) -> None:
    """三种结局下，「本局结束」都会打印 —— 因为没有用 exit()。"""
    fake_input(answers)
    ch01_03_example.play_v3()
    out = capsys.readouterr().out
    for line in expected_lines:
        assert line in out, f"缺少 {line!r}，实际输出：\n{out}"


def test_ch01_03_example_while_else_skipped_on_break(
    fake_input: Callable[[list[str]], None], capsys: pytest.CaptureFixture[str]
) -> None:
    """while ... else：被 break 打断时 else 不执行。"""
    fake_input(["42"])
    ch01_03_example.play_v3()
    assert "次数用完了" not in capsys.readouterr().out


# --- 练习 ---


def test_ch01_03_exercise_1_sum_until_zero() -> None:
    assert run_or_skip(ex3.sum_until_zero, [3, -1, 4, 0, 100]) == 7
    assert ex3.sum_until_zero([]) == 0, "空列表"
    assert ex3.sum_until_zero([0, 5]) == 0, "第一个就是 0"
    assert ex3.sum_until_zero([1, 2, 3]) == 6, "没有 0，全部加完"


@pytest.mark.parametrize(("inputs", "target", "max_attempts", "expected"), PLAY_CASES)
def test_ch01_03_exercise_2_play(
    inputs: list[str], target: int, max_attempts: int, expected: str
) -> None:
    assert run_or_skip(ex3.play, inputs, target, max_attempts) == expected


def test_ch01_03_exercise_3_buggy_unchanged() -> None:
    """play_buggy 要求保留原样。"""
    with pytest.raises(SystemExit):
        ex3.play_buggy(["42"], 42)


def test_ch01_03_exercise_3_fixed() -> None:
    assert run_or_skip(ex3.play_fixed, ["1", "42"], 42) == "猜中了"
    assert ex3.play_fixed(["1"], 42) == "输入结束"


def test_ch01_03_exercise_3_answered() -> None:
    unanswered = [
        line for line in ex3.EXERCISE_3_ANSWER.splitlines() if line.strip() in ("答：", "答:")
    ]
    if unanswered:
        pytest.skip(f"练习 3 还有 {len(unanswered)} 个问题没回答")


# ============================================================================
# 预测题的通用检查（1.4 / 1.5 共用）
# ============================================================================


def check_predictions(predictions: dict[str, str | None]) -> None:
    unanswered = [k for k, v in predictions.items() if v is None]
    if unanswered:
        pytest.skip(f"练习 1 还有 {len(unanswered)} 条没填")
    wrong = {
        expr: (guess, actual_repr(expr))
        for expr, guess in predictions.items()
        if guess != actual_repr(expr)
    }
    assert not wrong, "猜错的（你的答案, 真实结果）：\n" + "\n".join(
        f"  {k:<24} 你写 {g!r:<16} 实际 {a!r}" for k, (g, a) in wrong.items()
    )


# ============================================================================
# 1.4 模块与字符串格式化
# ============================================================================


@pytest.mark.parametrize("expr", list(sol4.PREDICTIONS))
def test_ch01_04_solution_predictions(expr: str) -> None:
    # '"随机数：{x}"' 这一条不需要 x 存在（没有 f，不会求值）
    assert sol4.PREDICTIONS[expr] == actual_repr(expr), f"{expr} 的答案写错了"


def test_ch01_04_from_random_import_random_is_a_function() -> None:
    """讲解第 2 节：from random import random 导入的是函数。"""
    scope: dict[str, Any] = {}
    exec("from random import random", scope)
    assert callable(scope["random"])
    assert not hasattr(scope["random"], "randint")


def test_ch01_04_randint_is_closed_interval() -> None:
    """讲解第 3 节：randint 两端都能取到。"""
    import random

    rng = random.Random(0)
    seen = {rng.randint(1, 3) for _ in range(1000)}
    assert seen == {1, 2, 3}
    assert list(range(1, 3)) == [1, 2]


def test_ch01_04_seed_reproducible() -> None:
    import random

    random.seed(42)
    first = [random.randint(1, 100) for _ in range(5)]
    random.seed(42)
    second = [random.randint(1, 100) for _ in range(5)]
    assert first == second == [82, 15, 4, 95, 36], "讲解里写的序列必须和实际一致"


def test_ch01_04_rounding_facts() -> None:
    """讲解第 7 节：五成双，以及 2.675 存不准。"""
    assert [round(x) for x in (0.5, 1.5, 2.5, 3.5)] == [0, 2, 2, 4]
    assert round(2.675, 2) == 2.67
    assert format(2.675, ".20f").startswith("2.674999")


def test_ch01_04_fstring_counts_chars_not_columns() -> None:
    """讲解第 8 节：f-string 按字符数补齐，中文会歪。"""
    padded = f"{'张三':<8}"
    assert len(padded) == 8
    assert ch01_04_example.display_width(padded) == 10


def test_ch01_04_example_make_target_reproducible() -> None:
    assert ch01_04_example.make_target(7) == ch01_04_example.make_target(7)
    assert 1 <= ch01_04_example.make_target(7) <= 100


def test_ch01_04_example_play_v4(
    fake_input: Callable[[list[str]], None], capsys: pytest.CaptureFixture[str]
) -> None:
    target = ch01_04_example.make_target(1)
    fake_input(["abc", str(target)])
    ch01_04_example.play_v4(seed=1)
    out = capsys.readouterr().out
    assert "'abc' 不是整数" in out
    assert f"{target:>3} → 正确" in out
    assert "机会使用率 14%" in out, "1/7 = 14%"
    assert "本局结束" in out


def test_ch01_04_example_runs() -> None:
    done = run_module("m01_basics.ch01_04_example")
    assert done.returncode == 0, done.stderr
    assert "随机数：{} 56" in done.stdout, "print 不会替换 {}"
    assert "随机数：{num}" in done.stdout, "漏掉 f 不会替换"


def test_ch01_04_solution_pick_target() -> None:
    assert sol4.pick_target(1, 100, seed=42) == sol4.pick_target(1, 100, seed=42)
    values = {sol4.pick_target(1, 3, seed=s) for s in range(200)}
    assert values == {1, 2, 3}, "两端都要能取到"


def test_ch01_04_solution_pick_target_does_not_touch_global() -> None:
    """不许用 random.seed()：调用 pick_target 不能改变全局随机序列。"""
    import random

    random.seed(123)
    expected = [random.random() for _ in range(3)]

    random.seed(123)
    sol4.pick_target(1, 100, seed=999)
    actual = [random.random() for _ in range(3)]
    assert actual == expected


def test_ch01_04_solution_formatting() -> None:
    assert sol4.format_feedback(2, 7, 50, "大了") == "[2/7]  50 → 大了"
    assert sol4.format_feedback(7, 7, 100, "正确") == "[7/7] 100 → 正确"
    assert sol4.format_feedback(1, 7, 5, "小了") == "[1/7]   5 → 小了"
    assert sol4.format_summary(2, 7) == "用了 2 次，机会使用率 29%"
    assert sol4.format_summary(7, 7) == "用了 7 次，机会使用率 100%"


def test_ch01_04_solution_alignment() -> None:
    assert sol4.pad("Tom", 6) == "Tom   "
    assert sol4.pad("张三", 6) == "张三  "
    assert sol4.pad("欧阳修文", 4) == "欧阳修文", "超宽时原样返回"
    assert sol4.format_row(1, "张三", 3) == " 1  张三       3 次"
    rows = [sol4.format_row(r, n, a) for r, n, a in
            [(1, "Tom", 3), (2, "张三", 4), (10, "欧阳修文", 12)]]
    widths = {sol4.display_width(row) for row in rows}
    assert len(widths) == 1, f"每一行显示宽度应该相同，实际 {widths}"


# --- 练习 ---


def test_ch01_04_exercise_1_predictions() -> None:
    check_predictions(ex4.PREDICTIONS)


def test_ch01_04_exercise_2_pick_target() -> None:
    first = run_or_skip(ex4.pick_target, 1, 100, 42)
    assert first == ex4.pick_target(1, 100, 42), "seed 相同，结果必须相同"
    values = {ex4.pick_target(1, 3, s) for s in range(200)}
    assert values == {1, 2, 3}, f"1 和 3 两端都要能取到，实际只取到 {values}"
    assert 5 <= ex4.pick_target(5, 9, 0) <= 9


def test_ch01_04_exercise_2_no_global_seed() -> None:
    import random

    run_or_skip(ex4.pick_target, 1, 100, 1)
    random.seed(123)
    expected = [random.random() for _ in range(3)]
    random.seed(123)
    ex4.pick_target(1, 100, 999)
    actual = [random.random() for _ in range(3)]
    assert actual == expected, "pick_target 改动了全局随机状态 —— 是不是用了 random.seed()？"


def test_ch01_04_exercise_3_formatting() -> None:
    assert run_or_skip(ex4.format_feedback, 2, 7, 50, "大了") == "[2/7]  50 → 大了"
    assert ex4.format_feedback(7, 7, 100, "正确") == "[7/7] 100 → 正确", "三位数"
    assert ex4.format_feedback(1, 7, 5, "小了") == "[1/7]   5 → 小了", "一位数"
    assert run_or_skip(ex4.format_summary, 2, 7) == "用了 2 次，机会使用率 29%"
    assert ex4.format_summary(7, 7) == "用了 7 次，机会使用率 100%"


def test_ch01_04_exercise_4_alignment() -> None:
    assert run_or_skip(ex4.pad, "张三", 6) == "张三  "
    assert ex4.pad("Tom", 6) == "Tom   "
    assert ex4.pad("欧阳修文", 4) == "欧阳修文", "超宽时原样返回，不截断"
    assert run_or_skip(ex4.format_row, 1, "张三", 3) == " 1  张三       3 次"
    rows = [ex4.format_row(r, n, a) for r, n, a in
            [(1, "Tom", 3), (2, "张三", 4), (10, "欧阳修文", 12)]]
    widths = [ex4.display_width(row) for row in rows]
    assert len(set(widths)) == 1, f"三行的显示宽度应该相同，实际是 {widths}"


# ============================================================================
# 1.5 异常处理入门
# ============================================================================


@pytest.mark.parametrize("expr", list(sol5.PREDICTIONS))
def test_ch01_05_solution_predictions(expr: str) -> None:
    assert sol5.PREDICTIONS[expr] == actual_repr(expr), f"{expr} 的答案写错了"


# EAFP 的 parse_int 必须和 int() 完全一致，包括 LBYL 版本对不上的下划线
PARSE_CASES = [*INT_CASES, "1_000", "1__000", "_1", "1_", "-1_0"]


@pytest.mark.parametrize("raw", PARSE_CASES)
def test_ch01_05_solution_parse_int_agrees_with_int(raw: str) -> None:
    expected = int(raw) if int_accepts(raw) else None
    assert sol5.parse_int(raw) == expected


def test_ch01_05_lbyl_vs_eafp_disagree_on_underscore() -> None:
    """讲解第 9 节：LBYL 和 EAFP 的分歧点。"""
    assert ch01_05_example.looks_like_int("1_000") is False
    assert ch01_05_example.parse_int("1_000") == 1000
    # 不合法的下划线写法，两者都拒绝
    for raw in ("1__000", "_1"):
        assert ch01_05_example.parse_int(raw) is None


def test_ch01_05_parse_int_does_not_hide_type_errors() -> None:
    """只捕获 ValueError：传错类型是调用方的 bug，必须暴露出来。"""
    with pytest.raises(TypeError):
        sol5.parse_int(None)  # type: ignore[arg-type]


def test_ch01_05_solution_trace() -> None:
    assert sol5.trace("42") == ["try", "else", "finally"]
    assert sol5.trace("abc") == ["try", "except", "finally"]


def test_ch01_05_example_trace_skips_rest_of_try() -> None:
    """异常抛出后，try 里剩下的代码不执行。"""
    assert ch01_05_example.trace("42") == ["try", "try 的后半段", "else", "finally"]
    assert ch01_05_example.trace("abc") == ["try", "except", "finally"]


def test_ch01_05_finally_facts() -> None:
    """讲解第 6 节的三个结论。"""
    assert ch01_05_example.returns_from_try() == "try 里的 return"
    assert ch01_05_example.finally_overrides() == 2
    assert ch01_05_example.finally_swallows() == "finally 的 return"


def test_ch01_05_bare_except_catches_system_exit() -> None:
    """讲解第 5 节：裸 except 会接住 sys.exit()。"""
    caught = False
    try:
        sys.exit(3)
    except:  # noqa: E722
        caught = True
    assert caught


def test_ch01_05_as_e_is_deleted() -> None:
    """讲解第 4 节：except ... as e 结束后 e 被删除。"""
    code = (
        "try:\n    int('x')\nexcept ValueError as e:\n    pass\n"
        "try:\n    e\nexcept NameError:\n    print('deleted')\n"
    )
    done = subprocess.run([sys.executable, "-c", code], capture_output=True,
                          text=True, check=True)
    assert done.stdout.strip() == "deleted"


def test_ch01_05_wide_try_hides_config_bug() -> None:
    assert sol5.bonus_wide("5", "10") == "得分 15"
    assert sol5.bonus_wide("abc", "10") == "输入无效"
    assert sol5.bonus_wide("5", "10分") == "输入无效", "这就是问题所在"


def test_ch01_05_solution_bonus_narrow() -> None:
    assert sol5.bonus_narrow("5", "10") == "得分 15"
    assert sol5.bonus_narrow("abc", "10") == "输入无效"
    with pytest.raises(ValueError, match="10分"):
        sol5.bonus_narrow("5", "10分")


@pytest.mark.parametrize(
    ("answers", "expected"),
    [
        (["abc", "q"], "'abc' 不是整数"),
        (["²", "q"], "'²' 不是整数"),
        (["0", "q"], "0 超出了 1-100"),
        (["101", "q"], "101 超出了 1-100"),
        (["1_000", "q"], "1000 超出了 1-100"),
    ],
)
def test_ch01_05_example_play_v5_rejects(
    fake_input: Callable[[list[str]], None],
    capsys: pytest.CaptureFixture[str],
    answers: list[str],
    expected: str,
) -> None:
    """第五版对 ² 不再崩溃；1_000 被正确解析成 1000 再判为超范围。"""
    fake_input(answers)
    ch01_05_example.play_v5(seed=1)
    out = capsys.readouterr().out
    assert expected in out
    assert "本局结束" in out


def test_ch01_05_example_play_v5_wins(
    fake_input: Callable[[list[str]], None], capsys: pytest.CaptureFixture[str]
) -> None:
    import random

    target = random.Random(1).randint(1, 100)
    fake_input([str(target)])
    ch01_05_example.play_v5(seed=1)
    assert "用了 1 次" in capsys.readouterr().out


def test_ch01_05_example_runs() -> None:
    done = run_module("m01_basics.ch01_05_example")
    assert done.returncode == 0, done.stderr
    assert "'1_000'    LBYL=False  EAFP=1000     ← 不一致" in done.stdout


# --- 练习 ---


def test_ch01_05_exercise_1_predictions() -> None:
    check_predictions(ex5.PREDICTIONS)


def test_ch01_05_exercise_2_parse_int() -> None:
    run_or_skip(ex5.parse_int, "1")
    wrong = []
    for raw in PARSE_CASES:
        expected = int(raw) if int_accepts(raw) else None
        if ex5.parse_int(raw) != expected:
            wrong.append(f"  {raw!r:<10} 你返回 {ex5.parse_int(raw)!r}，应该是 {expected!r}")
    assert not wrong, "和 int() 不一致：\n" + "\n".join(wrong)


def test_ch01_05_exercise_2_only_catches_value_error() -> None:
    run_or_skip(ex5.parse_int, "1")
    with pytest.raises(TypeError):
        ex5.parse_int(None)  # type: ignore[arg-type]


def test_ch01_05_exercise_3_trace() -> None:
    assert run_or_skip(ex5.trace, "42") == ["try", "else", "finally"]
    assert ex5.trace("abc") == ["try", "except", "finally"]


def test_ch01_05_exercise_4_wide_unchanged() -> None:
    assert ex5.bonus_wide("5", "10分") == "输入无效", "bonus_wide 要求保留原样"


def test_ch01_05_exercise_4_narrow() -> None:
    assert run_or_skip(ex5.bonus_narrow, "5", "10") == "得分 15"
    assert ex5.bonus_narrow("abc", "10") == "输入无效"
    with pytest.raises(ValueError):
        ex5.bonus_narrow("5", "10分")


# ============================================================================
# 1.6 函数
# ============================================================================


def scripted(answers: list[str]) -> Callable[[str], str]:
    """返回一个假的 ask 函数：每次调用按顺序返回下一个预设输入。

    这就是第 1.6 章练习 4 说的「依赖注入」—— 把它传给 play(ask=...) 即可，
    不需要 monkeypatch。
    """
    it = iter(answers)
    return lambda _prompt: next(it)


def test_ch01_06_call_before_def() -> None:
    """讲解第 2 节：def 是语句，调用在它之前会 NameError。"""
    out = ch01_06_example.last_error("f()\ndef f():\n    print('hi')")
    assert out == "NameError: name 'f' is not defined"


def test_ch01_06_mutable_default_shared() -> None:
    """讲解第 4 节：默认值在 def 时创建一次，所有调用共享。"""
    ns: dict[str, Any] = {}
    exec("def add_item(item, items=[]):\n    items.append(item)\n    return items", ns)
    assert ns["add_item"]("a") == ["a"]
    assert ns["add_item"]("b") == ["a", "b"]
    assert ns["add_item"].__defaults__ == (["a", "b"],)


@pytest.mark.parametrize(
    ("call", "message"),
    [
        ("check(1)", "missing 1 required positional argument: 'target'"),
        ("check(1, 2, 3)", "takes 2 positional arguments but 3 were given"),
        ("check(1, 2, goal=3)", "got an unexpected keyword argument 'goal'"),
        ("check(1, guess=2)", "got multiple values for argument 'guess'"),
        ("check_kw(50, 42)", "takes 0 positional arguments but 2 were given"),
    ],
)
def test_ch01_06_argument_errors(call: str, message: str) -> None:
    """讲解第 3 节那张报错表。"""
    with pytest.raises(TypeError, match=message):
        eval(call, vars(ch01_06_example))


def test_ch01_06_swapped_arguments_silent() -> None:
    assert ch01_06_example.check(50, 42) == 8
    assert ch01_06_example.check(42, 50) == -8


@pytest.mark.parametrize(
    ("code", "expected"),
    [
        ("count = 0\ndef inc():\n    count = count + 1\ninc()",
         "UnboundLocalError: cannot access local variable 'count'"),
        ("def f():\n    y = 1\nf()\nprint(y)", "NameError: name 'y' is not defined"),
        ("sum = 0\nprint(sum([1, 2, 3]))", "TypeError: 'int' object is not callable"),
        ("def g():\n    return 1\ng = g()\ng()", "TypeError: 'int' object is not callable"),
        ("def d(a, b):\n    return a // b, a % b\nq, r, x = d(17, 5)",
         "ValueError: not enough values to unpack (expected 3, got 2)"),
    ],
)
def test_ch01_06_scope_errors(code: str, expected: str) -> None:
    """讲解第 5 节的四个作用域错误 + 第 8 节的解包错误。"""
    assert ch01_06_example.last_error(code).startswith(expected)


def test_ch01_06_annotations_not_enforced() -> None:
    assert ch01_06_example.add(1, 2) == "hello"


def test_ch01_06_mypy_catches_annotation_errors(tmp_path: Any) -> None:
    """讲解第 7 节：注解在运行时不检查，但 mypy 能在运行前发现。"""
    bad = tmp_path / "bad.py"
    bad.write_text(
        "def add(a: int, b: int) -> int:\n    return 'hello'\n\n"
        "def check_num(guess: int, target: int) -> str:\n    return 'x'\n\n"
        "check_num('50', 42)\n",
        encoding="utf-8",
    )
    done = subprocess.run(
        [sys.executable, "-m", "mypy", str(bad), "--no-error-summary"],
        capture_output=True, text=True, encoding="utf-8", check=False,
    )
    assert 'Incompatible return value type (got "str", expected "int")' in done.stdout
    assert 'Argument 1 to "check_num" has incompatible type "str"; expected "int"' in done.stdout


def test_ch01_06_example_play_injected() -> None:
    """第六版的 play 通过参数接收 ask / say，不需要 monkeypatch。"""
    lines: list[str] = []
    result = ch01_06_example.play(42, ask=scripted(["abc", "50", "42"]), say=lines.append)
    assert result == "猜中了，用了 2 次"
    assert any("'abc' 不是 1-100 之间的整数" in line for line in lines)
    assert "    50 → 大了" in lines


def test_ch01_06_example_play_exhausted() -> None:
    result = ch01_06_example.play(42, max_attempts=2, ask=scripted(["1", "2"]),
                                  say=lambda _: None)
    assert result == "次数用完了，答案是 42"


def test_ch01_06_example_runs() -> None:
    done = run_module("m01_basics.ch01_06_example")
    assert done.returncode == 0, done.stderr
    assert "add_item.__defaults__ = (['a', 'b'],)" in done.stdout


def test_ch01_06_solution_record_guess() -> None:
    assert sol6.record_guess(5) == [5]
    assert sol6.record_guess(7) == [7], "两次调用不能共享列表"
    mine: list[int] = []
    returned = sol6.record_guess(3, mine)
    assert mine == [3] and returned is mine, "传了空列表就要往这个列表里加"


def test_ch01_06_buggy_record_guess_shares_state() -> None:
    """对照：原版确实会累积。用 exec 新建一份，避免和其他测试互相影响。"""
    ns: dict[str, Any] = {}
    exec("def r(g, h=[]):\n    h.append(g)\n    return h", ns)
    ns["r"](5)
    assert ns["r"](7) == [5, 7]


def test_ch01_06_solution_describe_and_hint() -> None:
    assert sol6.describe(50, 42) == ("大了", 8)
    assert sol6.describe(30, 42) == ("小了", 12)
    assert sol6.describe(42, 42) == ("正确", 0)
    assert sol6.format_hint(50, 42) == "大了（差 8）"
    assert sol6.format_hint(30, 42) == "小了（差 12）"
    assert sol6.format_hint(42, 42) == "正确"


def test_ch01_06_solution_keyword_only() -> None:
    assert sol6.check_num_kw(guess=50, target=42) == "大了"
    with pytest.raises(TypeError):
        sol6.check_num_kw(50, 42)  # type: ignore[call-arg]


PLAY6_CASES = [
    (["50", "abc", "42"], 42, 5, "猜中了，用了 2 次"),
    (["1", "2"], 42, 2, "次数用完"),
    (["1", " Q "], 42, 5, "主动退出"),
    (["1", "42"], 42, 2, "猜中了，用了 2 次"),
    (["x", "1", "y", "2", "42"], 42, 3, "猜中了，用了 3 次"),
]


@pytest.mark.parametrize(("answers", "target", "max_attempts", "expected"), PLAY6_CASES)
def test_ch01_06_solution_play(
    answers: list[str], target: int, max_attempts: int, expected: str
) -> None:
    assert sol6.play(target, max_attempts, ask=scripted(answers)) == expected


# --- 练习 ---


def test_ch01_06_exercise_1_buggy_unchanged() -> None:
    """record_guess_buggy 要求保留原样。用默认值的身份判断，不调用它（避免累积影响别的测试）。"""
    defaults = ex6.record_guess_buggy.__defaults__
    assert defaults is not None and isinstance(defaults[0], list)


def test_ch01_06_exercise_1_record_guess() -> None:
    assert run_or_skip(ex6.record_guess, 5) == [5]
    assert ex6.record_guess(7) == [7], "第二次调用得到了 [5, 7]？默认值被共享了"
    mine: list[int] = []
    returned = ex6.record_guess(3, mine)
    assert mine == [3], "传了一个空列表进来，应该往这个列表里加（是不是用了 if not history？）"
    assert returned is mine


def test_ch01_06_exercise_2_describe() -> None:
    assert run_or_skip(ex6.describe, 50, 42) == ("大了", 8)
    assert ex6.describe(30, 42) == ("小了", 12), "差距要是非负数"
    assert ex6.describe(42, 42) == ("正确", 0)


def test_ch01_06_exercise_2_format_hint() -> None:
    assert run_or_skip(ex6.format_hint, 50, 42) == "大了（差 8）"
    assert ex6.format_hint(30, 42) == "小了（差 12）"
    assert ex6.format_hint(42, 42) == "正确", "猜中时不显示差距"


def test_ch01_06_exercise_3_keyword_only() -> None:
    assert run_or_skip(ex6.check_num_kw, guess=50, target=42) == "大了"
    assert ex6.check_num_kw(guess=42, target=42) == "正确"
    with pytest.raises(TypeError):
        ex6.check_num_kw(50, 42)


@pytest.mark.parametrize(("answers", "target", "max_attempts", "expected"), PLAY6_CASES)
def test_ch01_06_exercise_4_play(
    answers: list[str], target: int, max_attempts: int, expected: str
) -> None:
    assert run_or_skip(ex6.play, target, max_attempts, ask=scripted(answers)) == expected


# ============================================================================
# 1.7 列表
# ============================================================================


@pytest.mark.parametrize("expr", list(sol7.PREDICTIONS))
def test_ch01_07_solution_predictions(expr: str) -> None:
    assert sol7.PREDICTIONS[expr] == actual_repr(expr), f"{expr} 的答案写错了"


def test_ch01_07_sort_returns_none() -> None:
    items = [3, 1, 2]
    assert items.sort() is None
    assert items == [1, 2, 3]


def test_ch01_07_assignment_is_reference() -> None:
    a = [1, 2, 3]
    b = a
    b.append(4)
    assert a == [1, 2, 3, 4] and a is b


def test_ch01_07_shallow_copy_shares_inner() -> None:
    import copy

    nested = [[1, 2], [3, 4]]
    shallow = nested.copy()
    shallow[0].append(99)
    assert nested == [[1, 2, 99], [3, 4]]

    nested = [[1, 2], [3, 4]]
    deep = copy.deepcopy(nested)
    deep[0].append(99)
    assert nested == [[1, 2], [3, 4]]


def test_ch01_07_grid_trap() -> None:
    g = [[0] * 3] * 3
    g[0][0] = 1
    assert g == [[1, 0, 0], [1, 0, 0], [1, 0, 0]]
    assert g[0] is g[1] is g[2]


def test_ch01_07_remove_while_iterating_skips() -> None:
    """讲解第 8 节：从 [-1, -2, 3, -4, 5] 删负数，-2 被跳过。"""
    items = [-1, -2, 3, -4, 5]
    for x in items:
        if x < 0:
            items.remove(x)
    assert items == [-2, 3, 5]


def test_ch01_07_function_mutates_caller() -> None:
    mine = [60, 70]
    ch01_07_example.add_bonus(mine)
    assert mine == [60, 70, 100]
    mine2 = [60, 70]
    ch01_07_example.rebind(mine2)
    assert mine2 == [60, 70]


def test_ch01_07_example_play_history() -> None:
    lines: list[str] = []
    history = ch01_07_example.play(
        42, ask=scripted(["50", "abc", "50", "30", "42"]), say=lines.append
    )
    assert history == [50, 30, 42], "重复的 50 和非法的 abc 都不计入"
    assert any("50 已经猜过了" in line for line in lines)
    assert ch01_07_example.summarize(history, 42) == "猜中了，用了 3 次。轨迹：50 → 30 → 42"


def test_ch01_07_example_summarize_edges() -> None:
    assert ch01_07_example.summarize([], 42) == "一次都没猜"
    assert ch01_07_example.summarize([1, 2], 42) == "没猜中，答案是 42。轨迹：1 → 2"


def test_ch01_07_example_runs() -> None:
    done = run_module("m01_basics.ch01_07_example")
    assert done.returncode == 0, done.stderr
    assert "[[1, 0, 0], [1, 0, 0], [1, 0, 0]]" in done.stdout


def test_ch01_07_solution_valid_guesses() -> None:
    raw = ["50", "abc", "0", " 7 ", "101", "42"]
    snapshot = list(raw)
    assert sol7.valid_guesses(raw, 1, 100) == [50, 7, 42]
    assert raw == snapshot, "不能修改输入"
    assert sol7.valid_guesses([]) == []


def test_ch01_07_solution_make_grid() -> None:
    g = sol7.make_grid(2, 3, 0)
    assert g == [[0, 0, 0], [0, 0, 0]]
    g[0][0] = 9
    assert g[1][0] == 0, "改一行不能影响其他行"
    assert sol7.make_grid(0, 3) == []


DROP_CASES = [
    ([0, -1, 50, 200, 300, 42], [50, 42]),
    ([], []),
    ([5, 6], [5, 6]),
    ([0, 0, 0], []),
    ([101, 1, 100, 0], [1, 100]),
]


@pytest.mark.parametrize(("before", "after"), DROP_CASES)
def test_ch01_07_solution_drop_out_of_range(before: list[int], after: list[int]) -> None:
    guesses = list(before)
    obj = id(guesses)
    assert sol7.drop_out_of_range(guesses, 1, 100) is None  # type: ignore[func-returns-value]
    assert guesses == after
    assert id(guesses) == obj


def test_ch01_07_buggy_drop_misses_elements() -> None:
    guesses = [0, -1, 50, 200, 300, 42]
    sol7.drop_out_of_range_buggy(guesses, 1, 100)
    assert guesses == [-1, 50, 300, 42], "讲解和练习里写的 bug 结果必须和实际一致"


# --- 练习 ---


def test_ch01_07_exercise_1_predictions() -> None:
    check_predictions(ex7.PREDICTIONS)


def test_ch01_07_exercise_2_valid_guesses() -> None:
    raw = ["50", "abc", "0", " 7 ", "101", "42"]
    snapshot = list(raw)
    assert run_or_skip(ex7.valid_guesses, raw, 1, 100) == [50, 7, 42]
    assert raw == snapshot, "raw_inputs 被修改了"
    assert ex7.valid_guesses([]) == [], "空列表"
    assert ex7.valid_guesses(["-5", "5"], -10, 0) == [-5], "范围用参数，不要写死 1-100"


def test_ch01_07_exercise_3_make_grid() -> None:
    g = run_or_skip(ex7.make_grid, 3, 2, 7)
    assert g == [[7, 7], [7, 7], [7, 7]]
    g[0][0] = 9
    assert g[1][0] == 7 and g[2][0] == 7, "改了第一行，其他行也变了 —— 几行指向的是同一个列表"


def test_ch01_07_exercise_4_buggy_unchanged() -> None:
    guesses = [0, -1, 50, 200, 300, 42]
    ex7.drop_out_of_range_buggy(guesses, 1, 100)
    assert guesses == [-1, 50, 300, 42], "drop_out_of_range_buggy 要求保留原样"


@pytest.mark.parametrize(("before", "after"), DROP_CASES)
def test_ch01_07_exercise_4_drop(before: list[int], after: list[int]) -> None:
    guesses = list(before)
    obj = id(guesses)
    returned = run_or_skip(ex7.drop_out_of_range, guesses, 1, 100)
    if guesses == before and before != after:
        pytest.fail(
            "调用方的列表一个元素都没变。如果你写的是 guesses = [...]，"
            "那只是让函数里的局部变量指向了新列表，调用方看不到 —— 试试 guesses[:] = [...]"
        )
    assert guesses == after, f"结果应该是 {after}，实际 {guesses}"
    assert id(guesses) == obj
    assert returned is None, "原地修改的函数应该返回 None"


# ============================================================================
# 1.8 字典、元组、集合
# ============================================================================


@pytest.mark.parametrize("expr", list(sol8.PREDICTIONS))
def test_ch01_08_solution_predictions(expr: str) -> None:
    assert sol8.PREDICTIONS[expr] == actual_repr(expr), f"{expr} 的答案写错了"


def test_ch01_08_equal_keys_merge() -> None:
    """讲解第 3 节：True、1、1.0 是同一个键。"""
    # ruff 的 F601 会拦住这种写法（讲解第 3 节），这里是故意的
    assert {1: "a", True: "b"} == {1: "b"}  # noqa: F601
    assert len({1: "a", 1.0: "b"}) == 1  # noqa: F601
    assert {True, 1, 1.0} == {True}
    assert hash(1) == hash(True) == hash(1.0)


def test_ch01_08_unhashable_key() -> None:
    with pytest.raises(TypeError, match="unhashable type: 'list'"):
        eval("{[1, 2]: 'x'}")
    with pytest.raises(TypeError, match="unhashable type: 'list'"):
        hash((1, [2]))


def test_ch01_08_dict_changed_during_iteration() -> None:
    d = {"a": 1, "b": 2, "c": 3}
    with pytest.raises(RuntimeError, match="dictionary changed size during iteration"):
        for k in d:
            if k == "a":
                del d[k]


def test_ch01_08_insertion_order_kept() -> None:
    d: dict[str, int] = {}
    d["z"] = 1
    d["a"] = 2
    d["m"] = 3
    d["z"] = 99
    assert list(d) == ["z", "a", "m"]


def test_ch01_08_tuple_augmented_assignment_paradox() -> None:
    """讲解第 6 节：t[0] += [3] 报错了，修改却生效了。"""
    t: tuple[list[int], int] = ([1, 2], 3)
    with pytest.raises(TypeError, match="does not support item assignment"):
        t[0] += [3]
    assert t == ([1, 2, 3], 3)


def test_ch01_08_single_element_tuple() -> None:
    assert type(eval("(1)")) is int, "括号里只有一个值，括号只是分组"
    assert type(eval("(1,)")) is tuple, "逗号才是元组的标志"
    assert type({}) is dict
    assert type(set()) is set


def test_ch01_08_set_order_not_guaranteed() -> None:
    """讲解第 7 节：整数集合的顺序不是插入顺序，也不一定是从小到大。"""
    assert list({30, 5, 100, 42, 7}) != [30, 5, 100, 42, 7]
    assert list(dict.fromkeys([3, 1, 3, 2])) == [3, 1, 2]


def test_ch01_08_string_set_order_varies_across_processes() -> None:
    """讲解第 7 节：字符串集合的顺序取决于哈希种子，不同进程可能不同。"""
    code = "print(list({'apple', 'banana', 'cherry', 'date'}))"
    orders = set()
    for seed in ("1", "2", "3", "4"):
        done = subprocess.run(
            [sys.executable, "-c", code], capture_output=True, text=True, check=True,
            env={**os.environ, "PYTHONHASHSEED": seed},
        )
        orders.add(done.stdout.strip())
    assert len(orders) > 1, "四个不同的哈希种子应该至少产生两种顺序"


def test_ch01_08_example_play_tracks_steps() -> None:
    lines: list[str] = []
    steps = ch01_08_example.play(
        42, ask=scripted(["50", "50", "abc", "30", "42"]), say=lines.append
    )
    assert steps == [(50, "大了"), (30, "小了"), (42, "正确")]
    assert any("50 已经猜过了" in line for line in lines)


def test_ch01_08_example_record_round() -> None:
    board: dict[str, int] = {}
    win3 = [(1, "小了"), (2, "小了"), (42, "正确")]
    win2 = [(1, "小了"), (42, "正确")]
    lose = [(1, "小了")]
    assert ch01_08_example.record_round(board, "张三", win3) is True
    assert ch01_08_example.record_round(board, "张三", lose) is False
    assert ch01_08_example.record_round(board, "张三", win2) is True
    assert ch01_08_example.record_round(board, "张三", win3) is False
    assert ch01_08_example.record_round(board, "李四", []) is False
    assert board == {"张三": 2}


def test_ch01_08_example_format_board() -> None:
    assert ch01_08_example.format_board({"张三": 4, "李四": 2}) == [
        " 1. 李四  2 次", " 2. 张三  4 次"
    ]
    assert ch01_08_example.format_board({}) == []


def test_ch01_08_example_runs() -> None:
    done = run_module("m01_basics.ch01_08_example")
    assert done.returncode == 0, done.stderr
    assert "{1: 'a', True: 'b'}" in done.stdout


def test_ch01_08_solution_count_results() -> None:
    assert sol8.count_results(["大了", "小了", "大了", "正确"]) == {"大了": 2, "小了": 1, "正确": 1}
    assert sol8.count_results([]) == {}


def test_ch01_08_solution_best_scores() -> None:
    records = [("张三", 5), ("李四", 3), ("张三", 2), ("李四", 4)]
    assert sol8.best_scores(records) == {"张三": 2, "李四": 3}
    assert sol8.best_scores([]) == {}
    assert sol8.best_scores([("王五", 0), ("王五", 3)]) == {"王五": 0}, "0 也是合法成绩"


FIRST_REPEAT_CASES = [
    ([50, 30, 50, 30], 50),
    ([1, 2, 3], None),
    ([], None),
    ([7, 7], 7),
    ([1, 2, 3, 2, 1], 2),
]

UNIQUE_CASES = [
    ([3, 1, 3, 2, 1], [3, 1, 2]),
    ([], []),
    ([5, 5, 5], [5]),
    ([30, 5, 100, 42, 7, 5], [30, 5, 100, 42, 7]),
]


@pytest.mark.parametrize(("guesses", "expected"), FIRST_REPEAT_CASES)
def test_ch01_08_solution_first_repeat(guesses: list[int], expected: int | None) -> None:
    assert sol8.first_repeat(guesses) == expected


@pytest.mark.parametrize(("guesses", "expected"), UNIQUE_CASES)
def test_ch01_08_solution_unique_in_order(guesses: list[int], expected: list[int]) -> None:
    assert sol8.unique_in_order(guesses) == expected


# --- 练习 ---


def test_ch01_08_exercise_1_predictions() -> None:
    check_predictions(ex8.PREDICTIONS)


def test_ch01_08_exercise_2_count_results() -> None:
    got = run_or_skip(ex8.count_results, ["大了", "小了", "大了", "正确"])
    assert got == {"大了": 2, "小了": 1, "正确": 1}
    assert ex8.count_results([]) == {}, "空列表应该得到空字典"


def test_ch01_08_exercise_3_best_scores() -> None:
    records = [("张三", 5), ("李四", 3), ("张三", 2), ("李四", 4)]
    assert run_or_skip(ex8.best_scores, records) == {"张三": 2, "李四": 3}
    assert ex8.best_scores([]) == {}
    assert ex8.best_scores([("王五", 0), ("王五", 3)]) == {"王五": 0}, (
        "0 是合法成绩 —— 是不是用了 if not best.get(name)？"
    )


@pytest.mark.parametrize(("guesses", "expected"), FIRST_REPEAT_CASES)
def test_ch01_08_exercise_4a_first_repeat(guesses: list[int], expected: int | None) -> None:
    assert run_or_skip(ex8.first_repeat, guesses) == expected


@pytest.mark.parametrize(("guesses", "expected"), UNIQUE_CASES)
def test_ch01_08_exercise_4b_unique_in_order(guesses: list[int], expected: list[int]) -> None:
    got = run_or_skip(ex8.unique_in_order, guesses)
    assert got == expected, (
        f"期望 {expected}，实际 {got}。如果用了 list(set(...))，顺序是不保证的"
    )


# ============================================================================
# 1.9 内置函数与边界条件
# ============================================================================


@pytest.mark.parametrize("expr", list(sol9.PREDICTIONS))
def test_ch01_09_solution_predictions(expr: str) -> None:
    assert sol9.PREDICTIONS[expr] == actual_repr(expr), f"{expr} 的答案写错了"


def test_ch01_09_max_empty_message_depends_on_version() -> None:
    """讲解第 2 节：3.13 起报错措辞变了，类型没变。"""
    with pytest.raises(ValueError) as caught:
        max([])
    msg = str(caught.value)
    if sys.version_info >= (3, 13):
        assert msg == "max() iterable argument is empty"
    else:
        assert msg == "max() arg is an empty sequence"


def test_ch01_09_float_sum_depends_on_version() -> None:
    """讲解第 6 节：3.12 起 sum() 对浮点数用了更精确的算法。"""
    if sys.version_info >= (3, 12):
        assert sum([0.1] * 10) == 1.0
    else:
        assert sum([0.1] * 10) == 0.9999999999999999
    assert 0.1 + 0.2 != 0.3, "两个数相加不经过 sum，任何版本都不等于 0.3"


def test_ch01_09_division_facts() -> None:
    import math

    assert 6 / 2 == 3.0 and isinstance(6 / 2, float)
    assert -7 // 2 == -4
    assert int(-3.5) == -3
    assert math.floor(-3.5) == -4
    assert -7 % 2 == 1
    assert 7 % -2 == -1
    assert divmod(-17, 5) == (-4, 3)


def test_ch01_09_split_edges() -> None:
    # 这几行就是要演示 split 在字面量上的结果，所以关掉 ruff 的 SIM905
    assert "".split(",") == [""]  # noqa: SIM905
    assert "".split() == []  # noqa: SIM905
    assert " a  b ".split(" ") == ["", "a", "", "b", ""]  # noqa: SIM905
    assert "50,".split(",") == ["50", ""]  # noqa: SIM905


def test_ch01_09_vacuous_truth() -> None:
    assert all([]) is True
    assert any([]) is False


def test_ch01_09_range_check_wrong_lets_zero_through() -> None:
    assert ch01_09_example.in_range_wrong(0) is True, "这正是 bug 所在"
    assert ch01_09_example.in_range_right(0) is False
    for x in (-1, 101):
        assert ch01_09_example.in_range_wrong(x) is False
        assert ch01_09_example.in_range_right(x) is False


def test_ch01_09_example_statistics_empty() -> None:
    """一次都没猜就退出，统计不能崩。"""
    history = ch01_09_example.play(42, ask=scripted(["q"]), say=lambda _: None)
    assert history == []
    assert ch01_09_example.statistics(history, 42) == ["有效猜测 0 次", "一次都没猜，暂无统计"]


def test_ch01_09_example_statistics_won() -> None:
    assert ch01_09_example.statistics([30, 70, 42], 42) == [
        "有效猜测 3 次", "最大 70，最小 30，平均 47.33", "猜中了，答案是 42",
    ]


def test_ch01_09_example_statistics_lost() -> None:
    assert ch01_09_example.statistics([50, 30, 45, 40], 42) == [
        "有效猜测 4 次", "最大 50，最小 30，平均 41.25", "没猜中，答案是 42，离它最近的一次是 40",
    ]


def test_ch01_09_example_runs() -> None:
    done = run_module("m01_basics.ch01_09_example")
    assert done.returncode == 0, done.stderr
    assert "''.split(',')" in done.stdout


def test_ch01_09_solution_average() -> None:
    assert sol9.average([30, 70, 50]) == 50.0
    assert sol9.average([]) is None
    assert sol9.average([-1, 1]) == 0.0, "平均值是 0 和没有数据是两回事"


def test_ch01_09_solution_summarize_stats() -> None:
    assert sol9.summarize_stats([30, 70, 50]) == "共 3 次｜最大 70｜最小 30｜平均 50.00"
    assert sol9.summarize_stats([]) == "共 0 次｜暂无统计数据"
    assert sol9.summarize_stats([1, 2]) == "共 2 次｜最大 2｜最小 1｜平均 1.50"


PARSE_LIST_CASES = [
    ("50,30,42", [50, 30, 42]),
    (" 50 , 30 ,, 42,", [50, 30, 42]),
    ("", []),
    ("   ", []),
    ("50", [50]),
    (",,,", []),
    ("-5, 7", [-5, 7]),
]


@pytest.mark.parametrize(("text", "expected"), PARSE_LIST_CASES)
def test_ch01_09_solution_parse_guess_list(text: str, expected: list[int]) -> None:
    assert sol9.parse_guess_list(text) == expected


def test_ch01_09_solution_parse_guess_list_rejects_garbage() -> None:
    with pytest.raises(ValueError, match="abc"):
        sol9.parse_guess_list("50,abc")


def test_ch01_09_naive_parse_fails_on_empty() -> None:
    """讲解里说的那个「第一版」：空字符串会被当成格式错误。"""
    with pytest.raises(ValueError):
        [int(p) for p in "".split(",")]  # noqa: SIM905


CLOSEST_CASES = [
    ([50, 30, 45, 40], 42, 40),
    ([44, 40], 42, 44),
    ([], 42, None),
    ([42], 42, 42),
    ([1, 100], 50, 1),
]


@pytest.mark.parametrize(("history", "target", "expected"), CLOSEST_CASES)
def test_ch01_09_solution_closest_guess(
    history: list[int], target: int, expected: int | None
) -> None:
    assert sol9.closest_guess(history, target) == expected


# --- 练习 ---


def test_ch01_09_exercise_1_predictions() -> None:
    check_predictions(ex9.PREDICTIONS)


def test_ch01_09_exercise_2_average() -> None:
    assert run_or_skip(ex9.average, [30, 70, 50]) == 50.0
    assert ex9.average([]) is None, "空列表要返回 None，不能报错，也不要返回 0"
    assert ex9.average([-1, 1]) == 0.0


def test_ch01_09_exercise_3_summarize_stats() -> None:
    assert run_or_skip(ex9.summarize_stats, [30, 70, 50]) == "共 3 次｜最大 70｜最小 30｜平均 50.00"
    assert ex9.summarize_stats([]) == "共 0 次｜暂无统计数据"
    assert ex9.summarize_stats([1, 2]) == "共 2 次｜最大 2｜最小 1｜平均 1.50", "平均值两位小数"


@pytest.mark.parametrize(("text", "expected"), PARSE_LIST_CASES)
def test_ch01_09_exercise_4a_parse_guess_list(text: str, expected: list[int]) -> None:
    assert run_or_skip(ex9.parse_guess_list, text) == expected


def test_ch01_09_exercise_4a_rejects_garbage() -> None:
    run_or_skip(ex9.parse_guess_list, "1")
    with pytest.raises(ValueError, match="abc"):
        ex9.parse_guess_list("50,abc")


@pytest.mark.parametrize(("history", "target", "expected"), CLOSEST_CASES)
def test_ch01_09_exercise_4b_closest_guess(
    history: list[int], target: int, expected: int | None
) -> None:
    assert run_or_skip(ex9.closest_guess, history, target) == expected
