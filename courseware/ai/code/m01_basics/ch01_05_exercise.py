"""第 1.5 章 · 练习。

    pytest tests/test_m01.py -k ch01_05 -v
"""

# ============================================================================
# 练习 1（基础）· 先猜会抛什么异常
#
# 填法：不报错就写结果（repr 格式），报错就写异常名。
# 这一题的重点是分清 ValueError 和 TypeError。
# ============================================================================

PREDICTIONS: dict[str, str | None] = {
    'int("abc")': None,
    '"a" + 1': None,
    "[1, 2][5]": None,
    '{}["k"]': None,
    "1 / 0": None,
    "None.upper()": None,
    "int(None)": None,
    'int("1_000")': None,
    'int(" -7 ")': None,
    'float("1e3")': None,
    "undefined_name": None,
}


# ============================================================================
# 练习 2（基础）· 用 EAFP 改写整数解析
#
# 第 1.2 章的 looks_like_int 是 LBYL（先检查再转换）。它有一处和 int() 对不上：
#     int("1_000") → 1000，但 looks_like_int("1_000") → False
#
# 写 parse_int(raw)：
#   - int(raw) 能成功 → 返回转换后的整数
#   - int(raw) 抛 ValueError → 返回 None
#
# 要求：
#   - 用 try / except
#   - 只捕获 ValueError，不要写 except Exception，也不要写裸 except
#   - try 块里只放 int(raw) 这一件事
# ============================================================================


def parse_int(raw: str) -> int | None:
    # TODO 练习 2
    raise NotImplementedError("请完成练习 2")


# ============================================================================
# 练习 3（基础）· 画出执行路径
#
# 写 trace(raw)，返回一个列表，按顺序记录执行了哪些块：
#
#   trace("42")  → ["try", "else", "finally"]
#   trace("abc") → ["try", "except", "finally"]
#
# 结构是 try / except ValueError / else / finally 四个块，
# 每个块的第一行把自己的名字 append 到列表里。try 块里在 append 之后调用 int(raw)。
#
# 做完之后想一想：如果在 try 块里 int(raw) 的「后面」再 append 一个 "try 的后半段"，
# trace("abc") 的结果会有它吗？
# ============================================================================


def trace(raw: str) -> list[str]:
    # TODO 练习 3
    raise NotImplementedError("请完成练习 3")


# ============================================================================
# 练习 4（进阶）· 把 try 收窄
#
# 下面这个函数的 try 包得太大：
#
#   bonus_wide("abc", "10")   → "输入无效"     ✓ 用户输错了，这个提示是对的
#   bonus_wide("5", "10分")   → "输入无效"     ✗ 是程序的配置写错了，不是用户的错
#
# 第二种情况本该是一个响亮的报错（让开发者赶紧去修配置），
# 却被伪装成了「用户输入无效」，用户怎么改输入都没用。
#
# 写 bonus_narrow(raw_guess, bonus_text)：
#   - raw_guess 不是整数 → 返回 "输入无效"
#   - bonus_text 不是整数 → **让 ValueError 正常抛出**，不要接住
#   - 都正常 → 返回 "得分 N"
# ============================================================================


def bonus_wide(raw_guess: str, bonus_text: str) -> str:
    """保留原样，不要改 —— 测试会检查它确实会把配置错误伪装成输入无效。"""
    try:
        guess = int(raw_guess)
        bonus = int(bonus_text)
        return f"得分 {guess + bonus}"
    except ValueError:
        return "输入无效"


def bonus_narrow(raw_guess: str, bonus_text: str) -> str:
    # TODO 练习 4
    raise NotImplementedError("请完成练习 4")
