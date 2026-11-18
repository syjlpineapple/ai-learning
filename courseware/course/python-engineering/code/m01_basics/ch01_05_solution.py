"""第 1.5 章 · 参考答案。"""

# ============================================================================
# 练习 1 · 先猜会抛什么异常
# ============================================================================

PREDICTIONS: dict[str, str | None] = {
    # 类型是 str 没问题，内容不是合法整数 → 值不对
    'int("abc")': "ValueError",
    # str 和 int 根本不能相加 → 类型不对
    '"a" + 1': "TypeError",
    # 下标越界
    "[1, 2][5]": "IndexError",
    # 字典里没有这个键（字典在第 1.8 章）
    '{}["k"]': "KeyError",
    "1 / 0": "ZeroDivisionError",
    # None 没有 upper 方法
    "None.upper()": "AttributeError",
    # 容易猜成 ValueError。None 不是字符串也不是数字，int() 根本不接受这个类型
    "int(None)": "TypeError",
    # 下划线分隔符：int() 认
    'int("1_000")': "1000",
    # 首尾空白 + 负号：int() 都认
    'int(" -7 ")': "-7",
    'float("1e3")': "1000.0",
    # 用了没定义的名字
    "undefined_name": "NameError",
}


# ============================================================================
# 练习 2 · 用 EAFP 改写整数解析
# ============================================================================


def parse_int(raw: str) -> int | None:
    """判断标准就是 int() 本身，所以不可能和 int() 不一致。

    为什么只捕获 ValueError：
      raw 的类型声明是 str。如果有人传了 None 进来，int(None) 会抛 TypeError ——
      那是**调用方的 bug**，应该让它暴露出来，而不是悄悄返回 None。
      捕获 TypeError 会把「用户输错了」和「程序写错了」混成一回事。

    为什么 return 写在 try 里：
      这里 try 块只有一行 `return int(raw)`，它就是唯一可能出错的操作，
      所以不需要 else。如果成功之后还有别的事要做，那些事应该放进 else。
    """
    try:
        return int(raw)
    except ValueError:
        return None


# ============================================================================
# 练习 3 · 画出执行路径
# ============================================================================


def trace(raw: str) -> list[str]:
    """四个块的触发条件：

    try      总是执行（但一旦抛异常，剩下的部分跳过）
    except   抛出了匹配的异常
    else     try 里**没有**抛异常
    finally  无论如何都执行

    思考题的答案：不会有。int("abc") 抛异常的那一刻，try 块里剩下的代码全部跳过，
    直接跳到 except。配套示例 ch01_05_example.trace 就加了那一行，可以跑一下看。
    """
    steps: list[str] = []
    try:
        steps.append("try")
        int(raw)
    except ValueError:
        steps.append("except")
    else:
        steps.append("else")
    finally:
        steps.append("finally")
    return steps


# ============================================================================
# 练习 4 · 把 try 收窄
# ============================================================================


def bonus_wide(raw_guess: str, bonus_text: str) -> str:
    """原题，保留作对照。"""
    try:
        guess = int(raw_guess)
        bonus = int(bonus_text)
        return f"得分 {guess + bonus}"
    except ValueError:
        return "输入无效"


def bonus_narrow(raw_guess: str, bonus_text: str) -> str:
    """try 只包住「用户可能输错」的那一行。

    int(bonus_text) 放在 try 外面：它出错说明程序的配置写错了，
    这时应该让 ValueError 一路抛上去，traceback 会直接指到这一行，
    开发者一眼就知道该去改哪里。

    「try 包多大」的判断标准：**这个 except 准备处理的是哪一种失败？**
    只把会产生这种失败的代码放进 try。其他代码的失败是另一回事，
    要么有它自己的 except，要么就让它报错。
    """
    try:
        guess = int(raw_guess)
    except ValueError:
        return "输入无效"

    bonus = int(bonus_text)
    return f"得分 {guess + bonus}"


# 补充：「输入无效」这个返回值本身也值得推敲。
#
# 函数返回字符串 "输入无效" 和返回 "得分 15" 是同一种类型，调用方要区分两者，
# 只能去比较字符串内容 —— 改一个字，调用方就坏了。
# 第 4.5 章「错误语义设计」会专门讨论：什么时候返回特殊值，什么时候抛异常，
# 什么时候返回 None。现在先把 try 的范围控制好。
