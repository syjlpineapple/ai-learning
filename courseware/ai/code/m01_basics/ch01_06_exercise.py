"""第 1.6 章 · 练习。

    pytest tests/test_m01.py -k ch01_06 -v

从这一章开始，函数的签名（def 那一行）有些要你自己写了。
"""

from collections.abc import Callable


def check_num(guess: int, target: int) -> str:
    """前几章的成果，已经写好。"""
    if guess == target:
        return "正确"
    if guess < target:
        return "小了"
    return "大了"


def parse_int(raw: str) -> int | None:
    """第 1.5 章的成果，已经写好。"""
    try:
        return int(raw)
    except ValueError:
        return None


# ============================================================================
# 练习 1（基础）· 修好可变默认值
#
# 下面这个函数想做的是：把 guess 追加进 history，返回 history。
# 不传 history 时，从一个新的空列表开始。
#
# 但它有 bug：连续调用两次 record_guess_buggy(5)、record_guess_buggy(7)，
# 第二次的结果是 [5, 7] 而不是 [7]。
#
# 写 record_guess，修好这个问题。签名里的默认值要改成 None。
# ============================================================================


def record_guess_buggy(guess: int, history: list[int] = []) -> list[int]:  # noqa: B006
    """保留原样，不要改 —— 测试会检查它确实有 bug。"""
    history.append(guess)
    return history


def record_guess(guess: int, history: list[int] | None = None) -> list[int]:
    # TODO 练习 1
    raise NotImplementedError("请完成练习 1")


# ============================================================================
# 练习 2（基础）· 返回多个值
#
# 写 describe(guess, target)，返回一个二元组 (结果, 差距)：
#   结果 是 check_num 的返回值
#   差距 是 guess 和 target 之间的距离，永远是非负数
#
#   describe(50, 42) → ("大了", 8)
#   describe(30, 42) → ("小了", 12)
#   describe(42, 42) → ("正确", 0)
#
# 再写 format_hint(guess, target)，用 describe 的两个返回值拼出提示：
#   format_hint(50, 42) → "大了（差 8）"
#   format_hint(42, 42) → "正确"            ← 猜中时不显示差距
#
# 要求：format_hint 里要用「解包」接收 describe 的结果：result, gap = describe(...)
# 提示：绝对值用内置函数 abs()
# ============================================================================


def describe(guess: int, target: int) -> tuple[str, int]:
    # TODO 练习 2
    raise NotImplementedError("请完成练习 2")


def format_hint(guess: int, target: int) -> str:
    # TODO 练习 2
    raise NotImplementedError("请完成练习 2")


# ============================================================================
# 练习 3（基础）· 用关键字参数防止传反
#
# check_num(guess, target) 的两个参数都是 int。传反了不会报错，只会给出相反的结果：
#     check_num(50, 42) → "大了"
#     check_num(42, 50) → "小了"     ← 参数传反了，但 Python 不会提醒你
#
# 写 check_num_kw，要求它**只能**用关键字调用：
#     check_num_kw(guess=50, target=42)   → "大了"
#     check_num_kw(50, 42)                → TypeError
#
# 这一题要你自己写完整的 def 那一行。
# 提示：在参数列表最前面加一个单独的 *
# ============================================================================


# TODO 练习 3：在这里写 def check_num_kw(...) -> str:
def check_num_kw(*args: object, **kwargs: object) -> str:
    """把这个占位函数整个替换掉。"""
    raise NotImplementedError("请完成练习 3")


# ============================================================================
# 练习 4（进阶）· 把输入函数当参数传进来
#
# 第 1.3 章的 play 用一个列表模拟输入。这一次换一种方式：
# 把「读一行输入」这件事本身当成参数传进来。
#
# 写 play(target, max_attempts, ask)：
#   - 每一轮调用 ask(提示语) 拿到用户输入，提示语的内容随意
#   - 规则和第 1.3 章一样：
#       q / quit（不区分大小写，可带空格） → 返回 "主动退出"
#       不是整数                         → 不计次，继续
#       猜中                             → 返回 "猜中了，用了 N 次"
#       次数用完                         → 返回 "次数用完"
#   - ask 的默认值是内置的 input，所以平时调用 play(42) 就是真实的键盘输入
#
# 测试会传一个假的 ask 进来，它按顺序返回预设的输入。
# 想一想：为什么这种写法不需要 monkeypatch 也能测？
# ============================================================================


def play(target: int, max_attempts: int = 5, ask: Callable[[str], str] = input) -> str:
    # TODO 练习 4
    raise NotImplementedError("请完成练习 4")
