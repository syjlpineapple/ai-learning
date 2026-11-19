"""第 1.6 章 · 参考答案。"""

from collections.abc import Callable


def check_num(guess: int, target: int) -> str:
    if guess == target:
        return "正确"
    if guess < target:
        return "小了"
    return "大了"


def parse_int(raw: str) -> int | None:
    try:
        return int(raw)
    except ValueError:
        return None


# ============================================================================
# 练习 1 · 修好可变默认值
# ============================================================================


def record_guess_buggy(guess: int, history: list[int] = []) -> list[int]:  # noqa: B006
    """原题，保留作对照。"""
    history.append(guess)
    return history


def record_guess(guess: int, history: list[int] | None = None) -> list[int]:
    """默认值用 None，在函数体里再创建新列表。

    为什么原来的写法有 bug：
      默认值 [] 是在 def 这条语句**执行时**创建的，只创建一次，
      然后存在函数对象的 __defaults__ 里。之后每次不传 history 的调用，
      拿到的都是同一个列表。第一次 append 了 5，第二次再 append 7，就成了 [5, 7]。

    为什么 None 就没事：
      None 是不可变的，共享它不会出问题。真正的空列表在函数体里创建，
      函数体每次调用都会重新执行，所以每次都是新的。

    判断要用 `is None`，不要用 `if not history`：
      调用方显式传了一个空列表 []，意思是「往这个列表里加」。
      `if not history` 会把它当成「没传」，另起一个新列表，调用方手里的那个就没变。
      这和第 1.2 章 `x or 默认值` 吞掉 0 是同一个坑。
    """
    if history is None:
        history = []
    history.append(guess)
    return history


# ============================================================================
# 练习 2 · 返回多个值
# ============================================================================


def describe(guess: int, target: int) -> tuple[str, int]:
    """return a, b 实际返回的是元组 (a, b)，括号可以省略。"""
    return check_num(guess, target), abs(guess - target)


def format_hint(guess: int, target: int) -> str:
    """调用方用解包接收：左边变量的个数必须和元组的长度一致。"""
    result, gap = describe(guess, target)
    if gap == 0:
        return result
    return f"{result}（差 {gap}）"


# 猜中时的判断也可以写成 `if result == "正确"`。这里用 gap == 0，
# 是因为它判断的是一个数字，不依赖「正确」这两个字的写法 ——
# 哪天把文案改成「猜中了」，这个函数不用跟着改。
# 这个问题（业务判断依赖显示文案）在第 4.5 章会正式讨论。


# ============================================================================
# 练习 3 · 用关键字参数防止传反
# ============================================================================


def check_num_kw(*, guess: int, target: int) -> str:
    """单独的 * 表示「后面的参数只能用关键字传」。

    什么时候值得这样做：
      - 几个参数类型相同、传反了不报错（这一题正是这种）
      - 参数的含义不能从位置看出来（比如一堆 True / False）

    代价是调用时要多写几个字。对于 check_num 这种被反复调用、
    而且两个参数确实容易混的函数，这个代价是值得的。
    """
    return check_num(guess, target)


# ============================================================================
# 练习 4 · 把输入函数当参数传进来
# ============================================================================


def play(target: int, max_attempts: int = 5, ask: Callable[[str], str] = input) -> str:
    """ask 是一个函数：接收一个字符串（提示语），返回一个字符串（用户输入）。

    Callable[[str], str] 就是这个意思：「参数是一个 str、返回值是 str 的可调用对象」。
    内置的 input 正好符合，所以它可以做默认值。

    为什么这样写不需要 monkeypatch 也能测：
      play 不再直接调用全局的 input，而是调用「别人交给它的那个函数」。
      测试时交给它一个假的，它就用假的。这叫「依赖注入」：
      函数需要的外部依赖，由调用方传进来，而不是自己去拿。

      第 8.1 章的 Mock 是另一种思路（不改函数签名，运行时替换掉 input）。
      两种都常用。能改签名的时候，依赖注入通常更清楚 —— 看签名就知道函数依赖什么。
    """
    attempts = 0
    while attempts < max_attempts:
        raw = ask(f"[{attempts + 1}/{max_attempts}] 你猜： ")
        if raw.strip().lower() in ("q", "quit"):
            return "主动退出"

        guess = parse_int(raw)
        if guess is None:
            continue

        attempts += 1
        if check_num(guess, target) == "正确":
            return f"猜中了，用了 {attempts} 次"

    return "次数用完"


# 和第 1.3 章的版本比，少了「输入结束」这个结局：
# 真实的 input() 不会「用完」，它会一直等用户输入。
# 测试里的假 ask 如果被调用的次数超过预设，next() 会抛 StopIteration ——
# 这正好能暴露「循环没有按预期结束」的 bug。
