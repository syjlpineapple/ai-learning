"""第 2.3 章 · 参考答案。

这个文件本身就是一个测试文件，可以直接跑：

    pytest m02_testing/ch02_03_solution.py -v
"""

import re

import pytest

# ============================================================================
# 被测代码（和练习文件里一样）
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
# 练习 1 · 合法输入
#
# 1 和 100 两个边界值是必须的：
#   - 下边界改错的版本（比如 1 被拒绝）只有 "1" 能抓住
#   - 上边界改错的版本（比如 100 被拒绝）只有 "100" 能抓住
# 只测 "42"、"50" 这种中间值，两个改错版本都能混过去。
#
# ids 让失败报告更好读：test_valid[upper] 比 test_valid[100-100] 一眼就能看懂。
# 用英文是因为 pytest 默认会把中文 id 转义成 \u4e0a\u8fb9\u754c，反而更难读。
# ============================================================================


@pytest.mark.parametrize(
    ("raw", "expected"),
    [("1", 1), ("42", 42), ("100", 100), (" 7 ", 7), ("+3", 3)],
    ids=["lower", "middle", "upper", "spaces", "plus-sign"],
)
def test_parse_guess_valid(raw: str, expected: int) -> None:
    assert parse_guess(raw) == expected


# ============================================================================
# 练习 2 · 非法输入：区分两种错误
#
# 两个函数分别断言具体的子类。
# 只写 pytest.raises(GuessError) 的话，「格式错误被抛成了范围错误」这种 bug 抓不住。
#
# 范围这一组同样要有边界：0 和 101 正好贴着合法范围的外侧。
# ============================================================================


@pytest.mark.parametrize("raw", ["abc", "", "3.14", "²", "q"])
def test_parse_guess_format_error(raw: str) -> None:
    with pytest.raises(GuessFormatError):
        parse_guess(raw)


@pytest.mark.parametrize("raw", ["0", "101", "-5", "1000"])
def test_parse_guess_range_error(raw: str) -> None:
    with pytest.raises(GuessRangeError):
        parse_guess(raw)


# ============================================================================
# 练习 3 · 检查错误消息
#
# 不加 re.escape 时报错长这样：
#     Regex pattern did not match.
#     Expected regex: '必须在 [1, 100] 之间'
#     Actual message: '数字必须在 [1, 100] 之间，你输入的是 101'
# 两行看起来都有「必须在 [1, 100] 之间」，却说不匹配 —— 因为 [1, 100] 在正则里是
# 「1、逗号、空格、0 这四个字符中的任意一个」，它只能匹配一个字符。
#
# re.escape 把所有正则特殊字符都转义掉，让 match 按字面意思匹配。
# 凡是 match 里出现 . * + ? ( ) [ ] { } ^ $ | \ 这些字符，都要 re.escape。
# ============================================================================


def test_parse_guess_range_message() -> None:
    with pytest.raises(GuessRangeError, match=re.escape("必须在 [1, 100] 之间")):
        parse_guess("101")


# ============================================================================
# 练习 4 · pytest 会收集哪些测试
#
# 默认规则（pytest 9.2，没有任何自定义配置时）：
#   文件：test_*.py 或 *_test.py
#   函数：以 test 开头（是「test」，不是「test_」）
#   类：  以 Test 开头，且没有 __init__；类里的方法同样以 test 开头
#
# 两个反直觉的地方：
#   - testing_data 会被收集：它以 test 开头。一个辅助函数起了这种名字，
#     就会被当成测试执行一遍
#   - 命令行上显式写出的文件，不管名字是什么都会被收集（这里问的是 pytest names，
#     没有显式写文件名，所以 checks.py 不会被收集）
# ============================================================================

DISCOVERY: dict[str, bool | None] = {
    "test_names.py 里的 test_ok": True,
    # 以 check 开头，不是 test
    "test_names.py 里的 check_test": False,
    # 以 test 开头 —— 是的，它会被当成测试
    "test_names.py 里的 testing_data": True,
    # 大小写敏感：Test_ 不是 test
    "test_names.py 里的 Test_upper": False,
    "TestGame 类里的 test_inside_class": True,
    # 类名不是 Test 开头
    "GameTest 类里的 test_in_wrong_class": False,
    # 有 __init__ 的类会被跳过，并给出 PytestCollectionWarning
    "TestWithInit 类（有 __init__）里的 test_never_collected": False,
    # *_test.py 也是默认规则之一
    "game_test.py 里的 test_in_suffix_file": True,
    # tests_ 不是 test_
    "tests_game.py 里的 test_in_tests_prefix_file": False,
    # 名字不符合规则
    "checks.py 里的 test_in_plain_file": False,
}
