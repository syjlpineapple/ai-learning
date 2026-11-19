"""第 2.3 章 · 讲解里的可运行示例。

这个文件有两种用法：

    python -m m02_testing.ch02_03_example
        在临时目录里搭几个小实验，跑 pytest，把真实输出打印出来：
        发现规则、退出码、参数化、raises、match 的正则陷阱。

    pytest m02_testing/ch02_03_example.py -v
        把这个文件本身当成测试文件来跑 —— 下面那几个 test_ 函数就是
        「本章推荐的写法」的样板。

文件名不是 test_ 开头，平时 `pytest` 不会收集它；显式写出路径时才会（讲解第 3 节）。
"""

import re
import subprocess
import sys
import tempfile
import textwrap
from pathlib import Path

import pytest

# ============================================================================
# 被测代码：和第 2.2 章一样的 parse_guess
# ============================================================================


class GuessError(ValueError):
    """猜测输入不合法。"""


class GuessFormatError(GuessError):
    """输入不是整数。"""


class GuessRangeError(GuessError):
    """数字超出范围。"""


def parse_guess(raw: str, low: int = 1, high: int = 100) -> int:
    try:
        n = int(raw)
    except ValueError:
        raise GuessFormatError(f"{raw!r} 不是整数") from None
    if not low <= n <= high:
        raise GuessRangeError(f"数字必须在 [{low}, {high}] 之间，你输入的是 {n}")
    return n


# ============================================================================
# 推荐写法的样板
# ============================================================================


@pytest.mark.parametrize(
    ("raw", "expected"),
    [("1", 1), ("42", 42), ("100", 100), (" 7 ", 7)],
    # ids 用英文：pytest 默认会把非 ASCII 的 id 转义成 \u4e0b\u8fb9\u754c 这种样子（讲解第 5 节）
    ids=["lower", "middle", "upper", "spaces"],
)
def test_parse_guess_valid(raw: str, expected: int) -> None:
    assert parse_guess(raw) == expected


@pytest.mark.parametrize("raw", ["abc", "", "3.14", "²"])
def test_parse_guess_format_error(raw: str) -> None:
    with pytest.raises(GuessFormatError):
        parse_guess(raw)


@pytest.mark.parametrize("raw", ["0", "101", "-5"])
def test_parse_guess_range_error(raw: str) -> None:
    with pytest.raises(GuessRangeError):
        parse_guess(raw)


def test_parse_guess_range_message() -> None:
    """match 是正则表达式。消息里有 [ ] 这类特殊字符时，必须 re.escape。"""
    with pytest.raises(GuessRangeError, match=re.escape("必须在 [1, 100] 之间")):
        parse_guess("101")


def test_excinfo_gives_the_exception() -> None:
    """as excinfo 拿到异常对象，可以继续检查它的各种属性。"""
    with pytest.raises(GuessFormatError) as excinfo:
        parse_guess("abc")
    assert isinstance(excinfo.value, ValueError), "GuessFormatError 应该也是 ValueError"
    assert excinfo.value.__suppress_context__ is True, "应该用了 from None"


# ============================================================================
# 演示：在临时目录里搭实验，跑真实的 pytest
# ============================================================================

LAB_FILES = {
    # 第 1 个实验：断言写在 if __name__ 里
    "main_guard/test_game.py": '''
        def check_num(guess, target):
            if guess == target:
                return "正确"
            return "小了" if guess < target else "大了"

        if __name__ == "__main__":
            assert check_num(10, 20) == "小了"
            assert check_num(20, 20) == "正确"
            print("所有测试通过")
    ''',
    # 第 2 个实验：命名规则
    "names/test_names.py": '''
        def test_ok():
            assert True

        def check_test():
            assert True

        def testing_data():
            return [1, 2, 3]

        def Test_upper():
            assert True

        class TestGame:
            def test_inside_class(self):
                assert True

        class GameTest:
            def test_in_wrong_class(self):
                assert True

        class TestWithInit:
            def __init__(self):
                pass
            def test_never_collected(self):
                assert True
    ''',
    "names/game_test.py": "def test_in_suffix_file():\n    assert True\n",
    "names/tests_game.py": "def test_in_tests_prefix_file():\n    assert True\n",
    "names/checks.py": "def test_in_plain_file():\n    assert True\n",
    # 第 3 个实验：循环里的 assert vs 参数化
    "behaviour/test_behaviour.py": '''
        import pytest

        def parse_guess(raw):
            n = int(raw)
            if not 1 <= n <= 100:
                raise ValueError("数字必须在 [1, 100] 之间")
            return n

        CASES = [("1", 1), ("50", 999), ("100", 100), ("7", 777)]

        def test_loop():
            for raw, expected in CASES:
                assert parse_guess(raw) == expected

        @pytest.mark.parametrize(("raw", "expected"), CASES)
        def test_parametrized(raw, expected):
            assert parse_guess(raw) == expected

        def test_match_is_regex():
            with pytest.raises(ValueError, match="必须在 [1, 100] 之间"):
                parse_guess("101")

        def test_raises_but_not_raised():
            with pytest.raises(ValueError):
                parse_guess("50")
    ''',
}


def build_lab(root: Path) -> None:
    for rel, content in LAB_FILES.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(textwrap.dedent(content).lstrip(), encoding="utf-8")


def pytest_in(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    """在 root 目录里跑 pytest。-p no:cacheprovider 避免在实验目录留下缓存。"""
    return subprocess.run(
        [sys.executable, "-m", "pytest", "-p", "no:cacheprovider", *args],
        cwd=root, capture_output=True, text=True, encoding="utf-8",
    )


def section(title: str) -> None:
    print("=" * 70)
    print(title)


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        build_lab(root)

        section("1. 断言写在 if __name__ == '__main__' 里")
        done = pytest_in(root, "main_guard", "-q")
        print("   pytest main_guard 的输出：")
        for line in done.stdout.strip().splitlines()[-2:]:
            print(f"      {line}")
        print(f"   退出码：{done.returncode}   ← 5 表示「一个测试都没收集到」")
        direct = subprocess.run([sys.executable, "main_guard/test_game.py"], cwd=root,
                                capture_output=True, text=True, encoding="utf-8")
        print(f"   直接 python 运行它：{direct.stdout.strip()}（退出码 {direct.returncode}）")

        section("2. 命名规则：pytest names --collect-only 收集了什么")
        done = pytest_in(root, "names", "--collect-only", "-q")
        for line in done.stdout.splitlines():
            if "::" in line:
                print(f"      {line}")
        print("   ↑ 注意 testing_data 也被当成了测试；Test_upper、check_test、GameTest 没有")
        if "cannot collect test class 'TestWithInit'" in done.stdout:
            print("   ↑ TestWithInit 有 __init__，pytest 给了一条警告后跳过了它")

        section("3. 显式写出路径时，不符合命名规则的文件也会被收集")
        done = pytest_in(root, "names/checks.py", "names/tests_game.py", "--collect-only", "-q")
        for line in done.stdout.splitlines():
            if "::" in line:
                print(f"      {line}")

        section("4. 循环里的 assert vs 参数化（同一组用例，第 2、4 条是错的）")
        done = pytest_in(root, "behaviour", "-q", "--tb=no", "-rf")
        for line in done.stdout.splitlines():
            if line.startswith("FAILED"):
                print(f"      {line}")
        print("   ↑ test_loop 只报了 50 那一条；参数化把 50 和 7 两条都报了")

        section("5. match 是正则表达式")
        done = pytest_in(root, "behaviour/test_behaviour.py::test_match_is_regex", "-q",
                         "--tb=short")
        for line in done.stdout.splitlines():
            if "regex" in line.lower() or "message" in line.lower():
                print(f"      {line.strip()}")
        print("   ↑ 两行看起来一样，但 [1, 100] 在正则里是「1、逗号、空格、0 中的任意一个字符」")

        section("6. 预期的异常没有抛出")
        done = pytest_in(root, "behaviour/test_behaviour.py::test_raises_but_not_raised",
                         "-q", "--tb=line")
        for line in done.stdout.splitlines():
            if "DID NOT RAISE" in line:
                print(f"      {line.strip()}")
                break

    print("=" * 70)
    print("把这个文件本身当测试跑：pytest m02_testing/ch02_03_example.py -v")


if __name__ == "__main__":
    main()
