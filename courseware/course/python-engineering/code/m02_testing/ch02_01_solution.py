"""第 2.1 章 · 参考答案。

先自己做完 ch02_01_exercise.py 再看这里。
每道题下面都写了「为什么这样做」，那部分比答案本身重要。
"""


def is_leap_year(year: int) -> bool:
    """判断是否闰年。

    公历闰年规则：能被 4 整除且不能被 100 整除，或者能被 400 整除。
    """
    return (year % 4 == 0 and year % 100 != 0) or year % 400 == 0


# ============================================================================
# 练习 1 · 补全测试用例
# ============================================================================


def test_is_leap_year() -> None:
    """覆盖三类输入。

    注意每条断言都写成 `== True` / `== False` 而不是 `assert f(x)`：
    前者验证「返回值等于 True」，后者只验证「返回值是真值」。
    对 bool 函数来说两者结果相同，但写成前者意图更明确，
    而且万一实现被改成返回字符串或 1/0，前者会立刻失败。
    """
    # 正常值：典型的闰年和平年
    assert is_leap_year(2024) is True, "2024 能被 4 整除、不能被 100 整除，是闰年"
    assert is_leap_year(2023) is False, "2023 不能被 4 整除，不是闰年"

    # 边界值：100 和 400 的分界 —— 这是闰年规则最容易写错的地方
    assert is_leap_year(1900) is False, "1900 能被 100 整除但不能被 400 整除，不是闰年"
    assert is_leap_year(2000) is True, "2000 能被 400 整除，是闰年"

    # 再补两个边界，覆盖 400 的另一侧
    assert is_leap_year(2100) is False, "2100 同 1900，不是闰年"
    assert is_leap_year(1600) is True, "1600 能被 400 整除，是闰年"

    # 异常值：规则对 0 和负数怎么表现？
    # 这里只断言「不抛异常且返回 bool」，因为公历在这个范围本来就没定义。
    # 把这件事写进测试，是在说明「我们知道这个边界，并且接受当前行为」。
    assert isinstance(is_leap_year(0), bool)
    assert isinstance(is_leap_year(-4), bool)


# ============================================================================
# 练习 2 · 找出三条无效断言
#
# 原题：
#     assert is_leap_year(2024)                      # 问题 1
#     assert is_leap_year(2023) == False or True      # 问题 2
#     assert len(str(is_leap_year(2024))) == 4        # 问题 3
# ============================================================================

PROBLEM_1 = """
问题 1：assert is_leap_year(2024)

这条本身能跑，但它是「单侧测试」——只验证了「是闰年」这一侧。
如果把实现改成 `return True`（永远返回真），这条断言照样通过。

另外它只验证了「返回值是真值」，没验证「返回值是 True」。
实现若被改成返回 "yes" 这样的非空字符串，它也通过。

改法：补上 False 一侧的用例，并把断言写明确。
"""

PROBLEM_2 = """
问题 2：assert is_leap_year(2023) == False or True

这条恒为真，永远不会失败。原因是运算符优先级：
`==` 的优先级高于 `or`，所以表达式被解析成

    (is_leap_year(2023) == False) or True

而 `任何值 or True` 的结果永远是 True。
实测：False == False or True  →  True
      True  == False or True  →  True      ← 实现写反了也通过

改法：去掉多余的 `or True`，直接断言返回值。
"""

PROBLEM_3 = """
问题 3：assert len(str(is_leap_year(2024))) == 4

这条能通过（str(True) == "True"，长度 4），但有两个毛病：

1. 意图不明。它绕了两层（转字符串、数长度）才间接验证「返回 True」，
   读代码的人要反推半天。测试是文档，看不懂的测试没有文档价值。
2. 脆弱。如果实现返回 1 而不是 True，str(1) == "1" 长度是 1，这条会失败——
   但失败信息是「长度不等于 4」，完全指不到真正的问题。

改法：直接断言返回值，不要绕。
"""


def test_broken() -> None:
    """原题，保留原样作对照。

    三条断言在当前实现下都能通过 —— 这正是它们危险的地方：
    看起来「测试通过」，实际没有验证力。
    """
    assert is_leap_year(2024)
    assert is_leap_year(2023) == False or True  # noqa: E712
    assert len(str(is_leap_year(2024))) == 4


def test_fixed() -> None:
    """三条断言改对之后的版本。"""
    # 问题 1 的修法：补上另一侧，断言写明确
    assert is_leap_year(2024) is True
    assert is_leap_year(2023) is False

    # 问题 2 的修法：去掉恒为真的 `or True`
    assert is_leap_year(2023) is False

    # 问题 3 的修法：直接断言返回值，不绕字符串
    assert is_leap_year(2024) is True


# ============================================================================
# 练习 3 · 验证你的测试真的有效
# ============================================================================

EXERCISE_3_ANSWER = """
(1) 改错之后（year % 100 != 0 → year % 100 == 0），哪一条断言失败了？

    答：第一条就失败了 —— assert is_leap_year(2024) is True。

    因为 2024 % 100 == 24，改错后 `year % 100 == 0` 为 False，
    前半个条件 `(2024 % 4 == 0 and False)` 变成 False；
    后半个 `2024 % 400 == 0` 也是 False（2024 % 400 == 24），
    所以函数返回 False，而断言预期 True。

    报错信息：
        AssertionError: 2024 能被 4 整除、不能被 100 整除，是闰年

    这就是带消息的断言的价值：一眼看出是哪个用例、预期是什么。

(2) 如果只写了 2024 和 2023 两个用例，这次改错能被发现吗？

    答：能，2024 这条就会失败。

    但换一种改错方式就发现不了。比如把 `year % 400 == 0` 改成
    `year % 400 == 1`：
        - 2024 → 仍然 True（走的是前半个条件）
        - 2023 → 仍然 False
        - 只有 2000、1600 这类「能被 400 整除」的年份才会暴露

    这正是边界值用例存在的理由：1900 和 2000 专门守着 100 和 400 这两条分界线。
    少了它们，闰年规则里最容易写错的那部分就没有任何测试覆盖。

    推论：「测试通过」的强度完全取决于用例的覆盖面。
    用例选得不对，测试通过说明不了任何事情。
"""


# ============================================================================
# 练习 4 · 把难测的函数改成好测的
# ============================================================================


def format_leap_year_message(year: int) -> str:
    """纯函数部分：只做计算，返回要显示的文字。

    拆分的依据是「计算」和「输入输出」分开：
      - 判断是不是闰年、决定显示什么文字 → 计算，放这里
      - 从键盘读、往屏幕写               → IO，放薄壳里

    这样这个函数就可以直接传参、直接断言返回值，不需要模拟任何环境。
    """
    if is_leap_year(year):
        return f"{year} 年是闰年"
    return f"{year} 年不是闰年"


def report_leap_year_v2() -> None:
    """薄壳部分：只负责 input 和 print，自己没有任何判断逻辑。

    这个函数仍然难测（它有 IO），但它已经没有值得测的东西了——
    逻辑全在 format_leap_year_message 里。
    「把难测的部分压缩到没有逻辑」是处理 IO 的通用手法。
    """
    year = int(input("请输入年份："))
    print(format_leap_year_message(year))


def test_format_leap_year_message() -> None:
    """纯函数的测试：直接传参、直接断言。"""
    assert format_leap_year_message(2024) == "2024 年是闰年"
    assert format_leap_year_message(2023) == "2023 年不是闰年"
    assert format_leap_year_message(1900) == "1900 年不是闰年"
    assert format_leap_year_message(2000) == "2000 年是闰年"


# ============================================================================
# 一个补充：为什么不直接测 report_leap_year_v2
#
# 想测它，得同时做两件事：
#   1. 伪造 input() 的返回值       → 第 8.1 章的 Mock
#   2. 捕获 print() 的输出         → pytest 的 capsys fixture（第 8.2 章）
#
# 能做，但没必要：它的逻辑已经被抽走了，测它等于测 input/print 本身。
# 这就是「可测试性来自设计」的实际含义 —— 不是想办法去测难测的代码，
# 而是把代码改成不需要那些办法。
# ============================================================================


def main() -> None:
    test_is_leap_year()
    test_fixed()
    test_format_leap_year_message()
    print("所有测试通过！")
    print()
    print(PROBLEM_1)
    print(PROBLEM_2)
    print(PROBLEM_3)
    print(EXERCISE_3_ANSWER)


if __name__ == "__main__":
    main()
