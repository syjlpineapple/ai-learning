"""第 1.4 章 · 练习。

    pytest tests/test_m01.py -k ch01_04 -v
"""

import random  # noqa: F401  练习 2 要用
import unicodedata

# ============================================================================
# 练习 1（基础）· 先猜，再验证
#
# 填法和前几章一样：按 repr 格式写结果，报错写异常名。
# 注意：f-string 的结果是字符串，所以要带引号。比如结果是 3.14 这个字符串，写 "'3.14'"
# ============================================================================

PREDICTIONS: dict[str, str | None] = {
    'f"{3.14159:.2f}"': None,
    'f"{1234567:,}"': None,
    'f"{0.85:.1%}"': None,
    'f"{7:03}"': None,
    'f"{42:>5}"': None,
    'f"{{x}}"': None,
    '"随机数：{x}"': None,
    'f"{10 / 4 = }"': None,
    "round(2.5)": None,
    "round(3.5)": None,
    "round(2.675, 2)": None,
}


# ============================================================================
# 练习 2（基础）· 可重现的随机答案
#
# 写 pick_target(low, high, seed)：
#   - 返回 [low, high] 之间的随机整数，两端都要能取到
#   - seed 相同时，返回值必须相同（方便测试和复现 bug）
#   - seed 为 None 时，每次可以不同
#
# 要求：不要调用 random.seed() —— 它会改全局状态，影响程序里其他用到 random 的地方。
# 提示：random.Random(seed) 会创建一个独立的随机数生成器，它也有 randint 方法。
# ============================================================================


def pick_target(low: int = 1, high: int = 100, seed: int | None = None) -> int:
    # TODO 练习 2
    raise NotImplementedError("请完成练习 2")


# ============================================================================
# 练习 3（基础）· 用 f-string 排版提示语
#
# format_feedback(attempt, max_attempts, guess, result) 要返回：
#
#     "[2/7]  50 → 大了"
#
#   - 方括号里是「第几次/总次数」
#   - 一个空格，然后是猜的数，**右对齐、占 3 格**
#     （所以 50 看起来前面有两个空格，100 只有一个，5 有三个）
#   - 然后是 " → " 和结果
#
# format_summary(attempts, max_attempts) 要返回：
#
#     "用了 2 次，机会使用率 29%"
#
#   - 使用率 = attempts / max_attempts，用百分号格式，**不要小数**
# ============================================================================


def format_feedback(attempt: int, max_attempts: int, guess: int, result: str) -> str:
    # TODO 练习 3
    raise NotImplementedError("请完成练习 3")


def format_summary(attempts: int, max_attempts: int) -> str:
    # TODO 练习 3
    raise NotImplementedError("请完成练习 3")


# ============================================================================
# 练习 4（进阶）· 让中文表格对齐
#
# 示例第 7 节展示了：f"{name:<8}" 按「字符数」补齐，而中文字符在终端里占两列，
# 所以中英混排的表格会歪。
#
# 1. 写 pad(text, width)：在右边补空格，让 text 的「显示宽度」等于 width。
#    text 本来就比 width 宽时，原样返回，不要截断。
#
# 2. 写 format_row(rank, name, attempts)，返回一行排行榜：
#
#        " 1  张三       3 次"
#
#    （张三占 4 列，补 6 个空格到 10 列；attempts 的 >2 又在 3 前面补了 1 个空格）
#
#    - rank 右对齐占 2 格
#    - 两个空格
#    - name 按「显示宽度」左对齐占 10 列（用你的 pad）
#    - attempts 右对齐占 2 格，后面跟 " 次"
#
#    不管 name 是 "Tom" 还是 "欧阳修文"，format_row 返回的字符串显示宽度都应该相同。
#
# 提示：unicodedata.east_asian_width(c) 对中文返回 "W"（宽），对全角符号返回 "F"。
#       这两种都算两列。
# ============================================================================


def display_width(text: str) -> int:
    """已经写好：返回 text 在终端里占几列。"""
    return sum(2 if unicodedata.east_asian_width(c) in ("W", "F") else 1 for c in text)


def pad(text: str, width: int) -> str:
    # TODO 练习 4
    raise NotImplementedError("请完成练习 4")


def format_row(rank: int, name: str, attempts: int) -> str:
    # TODO 练习 4
    raise NotImplementedError("请完成练习 4")
