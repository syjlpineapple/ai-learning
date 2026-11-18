"""第 1.9 章 · 练习。

    pytest tests/test_m01.py -k ch01_09 -v

这一章的每道题，测试都会专门喂一个「空」的输入进去。
"""

# ============================================================================
# 练习 1（基础）· 先猜，再验证
# ============================================================================

PREDICTIONS: dict[str, str | None] = {
    "sum([])": None,
    "max([])": None,
    "max([], default=0)": None,
    "6 / 2": None,
    "-7 // 2": None,
    "-7 % 2": None,
    "divmod(17, 5)": None,
    "all([])": None,
    "any([])": None,
    "''.split(',')": None,
    "' a  b '.split()": None,
}


# ============================================================================
# 练习 2（基础）· 平均值
#
# 写 average(values)：返回平均值；values 为空时返回 None。
#
#   average([30, 70, 50]) → 50.0
#   average([])           → None
#
# 要求：用守卫语句 —— 函数第一件事是判断空列表并提前 return。
# ============================================================================


def average(values: list[int]) -> float | None:
    # TODO 练习 2
    raise NotImplementedError("请完成练习 2")


# ============================================================================
# 练习 3（基础）· 统计摘要
#
# 写 summarize_stats(history)，返回一行文字：
#
#   summarize_stats([30, 70, 50]) → "共 3 次｜最大 70｜最小 30｜平均 50.00"
#   summarize_stats([])           → "共 0 次｜暂无统计数据"
#
# 平均值保留两位小数。分隔符是全角竖线「｜」。
# 要求：守卫语句写法，不要用 if / else 把两种情况包成两个大分支。
# ============================================================================


def summarize_stats(history: list[int]) -> str:
    # TODO 练习 3
    raise NotImplementedError("请完成练习 3")


# ============================================================================
# 练习 4（进阶）· 两个边界题
#
# (a) parse_guess_list(text)：把逗号分隔的文本解析成整数列表
#
#     parse_guess_list("50,30,42")        → [50, 30, 42]
#     parse_guess_list(" 50 , 30 ,, 42,") → [50, 30, 42]     空白和空段都忽略
#     parse_guess_list("")                → []               ← 注意示例第 3 节
#     parse_guess_list("   ")             → []
#     parse_guess_list("50,abc")          → 抛 ValueError，消息里要包含 'abc'
#
#     第一版很可能写成 [int(p) for p in text.split(",")]，先想想它在 "" 上会怎样。
#
# (b) closest_guess(history, target)：返回 history 里离 target 最近的那个数
#
#     closest_guess([50, 30, 45, 40], 42) → 40
#     closest_guess([44, 40], 42)         → 44     并列时返回先出现的
#     closest_guess([], 42)               → None
#
#     提示：min 的 key 参数接收一个函数，min 会用这个函数的返回值来比较。
#           lambda g: abs(g - target) 就是一个「输入 g、返回 abs(g - target)」的小函数。
# ============================================================================


def parse_guess_list(text: str) -> list[int]:
    # TODO 练习 4 (a)
    raise NotImplementedError("请完成练习 4")


def closest_guess(history: list[int], target: int) -> int | None:
    # TODO 练习 4 (b)
    raise NotImplementedError("请完成练习 4")
