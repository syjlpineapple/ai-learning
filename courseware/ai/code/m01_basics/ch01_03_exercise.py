"""第 1.3 章 · 练习。

    pytest tests/test_m01.py -k ch01_03 -v

关于这一章的练习里出现的 list[str]：
真实游戏是一次次调用 input()，那样没法自动测试。所以练习里用一个列表
「模拟」用户依次输入的内容，比如 ["50", "abc", "42"] 表示用户先输入 50、
再输入 abc、最后输入 42。for raw in inputs 会把它们逐个取出来。
列表本身在第 1.7 章细讲，现在只需要会用 for 逐个取。
"""

import sys


def looks_like_int(raw: str) -> bool:
    """上一章的成果，已经写好。"""
    body = raw.strip()
    if body and body[0] in "+-":
        body = body[1:]
    return body != "" and body.isdecimal()


def check_num(guess: int, target: int) -> str:
    if guess == target:
        return "正确"
    elif guess < target:
        return "小了"
    else:
        return "大了"


# ============================================================================
# 练习 1（基础）· break 和 continue
#
# 写 sum_until_zero(numbers)：从头逐个累加，规则是
#   - 遇到负数：跳过它，继续往后（continue）
#   - 遇到 0：立刻停止，后面的数都不加（break）
#   - 返回累加结果
#
# 例：sum_until_zero([3, -1, 4, 0, 100]) → 7    （3 + 4，-1 跳过，0 之后不算）
# ============================================================================


def sum_until_zero(numbers: list[int]) -> int:
    # TODO 练习 1
    raise NotImplementedError("请完成练习 1")


# ============================================================================
# 练习 2（基础）· 完整的一局游戏
#
# 写 play(inputs, target, max_attempts)，按顺序处理 inputs 里的每一条输入，
# 返回本局的结局（字符串）：
#
#   输入是 q / Q / quit（可能带空格）  → 立即返回 "主动退出"
#   输入不是整数                       → 跳过，不计入次数
#   输入是整数                         → 次数 +1，然后判断
#       猜中                           → 返回 "猜中了，用了 N 次"
#       没猜中且次数已用完             → 返回 "次数用完"
#   inputs 全部处理完了还没结束        → 返回 "输入结束"
#
# 例：
#   play(["50", "abc", "42"], 42, 5)  → "猜中了，用了 2 次"   （abc 不算）
#   play(["1", "2"], 42, 2)           → "次数用完"
#   play(["1", " Q "], 42, 5)         → "主动退出"
#   play(["1"], 42, 5)                → "输入结束"
#
# 这里在函数里用 return 结束，而不是 break —— 想想为什么 return 在这里更合适。
# ============================================================================


def play(inputs: list[str], target: int, max_attempts: int = 5) -> str:
    # TODO 练习 2
    raise NotImplementedError("请完成练习 2")


# ============================================================================
# 练习 3（进阶）· 找出 exit() 的问题
#
# 下面这个版本在猜中时调用了 sys.exit()。它在终端里运行时「看起来」完全正常。
#
# 1. 在下面的 EXERCISE_3_ANSWER 里回答三个问题
# 2. 写一个 play_fixed，行为和 play_buggy 一样，但不调用 sys.exit()，
#    猜中时返回 "猜中了"，输入用完时返回 "输入结束"
# ============================================================================


def play_buggy(inputs: list[str], target: int) -> str:
    """保留原样，不要改这个函数 —— 测试会检查它确实会调用 sys.exit()。"""
    for raw in inputs:
        if looks_like_int(raw) and check_num(int(raw), target) == "正确":
            print("猜中了")
            sys.exit()
    return "输入结束"


def play_fixed(inputs: list[str], target: int) -> str:
    # TODO 练习 3
    raise NotImplementedError("请完成练习 3")


EXERCISE_3_ANSWER = """
TODO 练习 3：

(1) 在终端里运行 play_buggy 并猜中，程序的退出码是多少？从退出码能看出「少做了事」吗？
    答：

(2) 如果调用方是这样写的，play_buggy 猜中时 except 能接住吗？为什么？
        try:
            result = play_buggy(["42"], 42)
        except Exception:
            print("出错了")
    答：

(3) 在一个函数里想「提前结束并给出结果」，该用 break、return 还是 sys.exit()？
    答：
"""
