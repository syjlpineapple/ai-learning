"""第 2.3 章 · 练习。

这一章的练习不一样：**你要写的是测试本身。**

检查方法也不一样。tests/test_m02.py 会用 pytest 跑你这个文件两轮：

    第一轮：被测代码是对的 —— 你的测试应该全部通过
    第二轮：把 parse_guess 换成 4 个「故意改错的版本」，一次换一个
            —— 你的测试应该每次都至少失败一条，否则说明你的测试抓不住这个 bug

这正是第 2.1 章「故意改错代码，验证测试有效」的自动化版本。

    pytest tests/test_m02.py -k ch02_03 -v       # 检查你的练习
    pytest m02_testing/ch02_03_exercise.py -v    # 只跑你写的测试，看它们本身过没过
"""

import re  # noqa: F401  练习 3 要用

import pytest  # noqa: F401  练习 1-3 要用

# ============================================================================
# 被测代码（已经写好，不要改）
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
# 练习 1（基础）· 合法输入：用参数化
#
# 写一个 test_ 开头的函数，用 @pytest.mark.parametrize 测至少 3 个合法输入。
# 每条用例是 (输入字符串, 期望的整数)。
#
# 第二轮检查里有两个改错版本和这一题有关：
#   - 一个版本把下边界改错了
#   - 一个版本把上边界改错了
# 想一想你的用例里必须包含哪两个值，才能抓住它们。
# ============================================================================

# TODO 练习 1：在这里写 @pytest.mark.parametrize(...) 和 def test_...(...)


# ============================================================================
# 练习 2（基础）· 非法输入：区分两种错误
#
# 写两个参数化的测试函数：
#   - 一个测「不是整数」的输入，断言抛出 GuessFormatError
#   - 一个测「超出范围」的输入，断言抛出 GuessRangeError
#
# 用 with pytest.raises(...)。
#
# 注意：不要两个都只写 pytest.raises(GuessError) —— 那样分不清是哪种错误。
# 第二轮检查里有一个改错版本，把格式错误抛成了普通的 ValueError。
# ============================================================================

# TODO 练习 2：在这里写两个测试函数


# ============================================================================
# 练习 3（进阶）· 检查错误消息
#
# 写一个测试，断言 parse_guess("101") 的错误消息里包含「必须在 [1, 100] 之间」。
#
# 用 pytest.raises 的 match 参数。先不加 re.escape 跑一次，看看报错长什么样
# （讲解第 6 节），再改对。
#
# 第二轮检查里有一个改错版本，把消息改成了「数字必须在 1 到 100 之间」。
# ============================================================================

# TODO 练习 3：在这里写测试函数


# ============================================================================
# 练习 4（基础）· pytest 会收集哪些测试
#
# 示例 ch02_03_example.py 第 2 节搭了一个 names/ 目录，然后运行
#     pytest names --collect-only
#
# 不要先跑示例，先判断下面每一项会不会被收集。填 True 或 False。
# 测试会真的搭一遍这个目录、跑一遍 pytest 来核对你的答案。
#
# 目录里的文件：
#     names/test_names.py   names/game_test.py   names/tests_game.py   names/checks.py
# ============================================================================

DISCOVERY: dict[str, bool | None] = {
    "test_names.py 里的 test_ok": None,
    "test_names.py 里的 check_test": None,
    "test_names.py 里的 testing_data": None,
    "test_names.py 里的 Test_upper": None,
    "TestGame 类里的 test_inside_class": None,
    "GameTest 类里的 test_in_wrong_class": None,
    "TestWithInit 类（有 __init__）里的 test_never_collected": None,
    "game_test.py 里的 test_in_suffix_file": None,
    "tests_game.py 里的 test_in_tests_prefix_file": None,
    "checks.py 里的 test_in_plain_file": None,
}
