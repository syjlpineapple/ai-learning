"""第 1.2 章 · 练习。

    pytest tests/test_m01.py -k ch01_02 -v
"""


def check_num(guess: int, target: int) -> str:
    """上一章的成果，已经写好。"""
    if guess == target:
        return "正确"
    elif guess < target:
        return "小了"
    else:
        return "大了"


# ============================================================================
# 练习 1（基础）· 先猜，再验证
#
# 填法和 1.1 一样：按 repr 格式写结果，报错写异常名。
# ============================================================================

PREDICTIONS: dict[str, str | None] = {
    "bool(0.0)": None,
    'bool(" ")': None,
    'bool("0")': None,
    "bool([0])": None,
    '"" or "匿名"': None,
    '0 or "无限制"': None,
    '"张三" and "李四"': None,
    "0 and 1/0": None,
    "isinstance(True, int)": None,
    "1 <= 150 <= 100": None,
    "True == False or True": None,
}


# ============================================================================
# 练习 2（基础）· 加上范围检查
#
# 猜数字的范围是 low 到 high（含两端）。写 classify(guess, target, low, high)：
#
#   guess 不在 [low, high] 里  →  "超出范围"
#   否则                        →  交给 check_num 判断
#
# 要求：范围判断用链式比较，一个表达式写完，不要写成两个条件用 and 连起来。
# ============================================================================


def classify(guess: int, target: int, low: int = 1, high: int = 100) -> str:
    # TODO 练习 2
    raise NotImplementedError("请完成练习 2")


# ============================================================================
# 练习 3（进阶）· 修好 isdigit 的两个漏洞
#
# 示例第 4 节展示了：isdigit() 和 int() 的判断不一致。
#
#   "-5"、"+7"、" 42 "  →  int() 能转，isdigit() 说不行     （误杀）
#   "²"                  →  int() 会崩，isdigit() 说可以     （漏放）
#
# 写一个 looks_like_int(raw)，要求它的判断和 int() 一致：
# int(raw) 能成功时返回 True，int(raw) 会报 ValueError 时返回 False。
#
# 限制：不许调用 int()，也不许用 try（那是第 1.5 章的写法，到时候会对比）。
#
# 提示：
#   - 先 strip() 去掉首尾空白
#   - 开头可能有一个 + 或 -，去掉它再判断剩下的部分
#   - 用 isdecimal() 代替 isdigit()，看示例第 4 节的表格想想为什么
#   - 别忘了只有一个 "-" 的情况
# ============================================================================


def looks_like_int(raw: str) -> bool:
    # TODO 练习 3
    raise NotImplementedError("请完成练习 3")


# ============================================================================
# 练习 4（进阶）· 0 是一个合法的值
#
# 游戏可以设置「剩余次数」。None 表示不限次数，整数表示还剩几次。
# 下面这个实现有 bug：
#
#     def format_remaining(remaining):
#         if not remaining:
#             return "不限次数"
#         return f"剩余 {remaining} 次"
#
# 1. 先想清楚：format_remaining(0) 会返回什么？对不对？
# 2. 修好它，让 None 返回 "不限次数"，0 返回 "剩余 0 次"
# ============================================================================


def format_remaining(remaining: int | None) -> str:
    # TODO 练习 4
    raise NotImplementedError("请完成练习 4")
