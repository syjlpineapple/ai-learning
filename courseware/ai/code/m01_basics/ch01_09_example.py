"""第 1.9 章 · 讲解里的可运行示例，也是 M1 猜数字的最终版。

    python -m m01_basics.ch01_09_example          # 看演示输出
    python -m m01_basics.ch01_09_example play     # 玩 M1 最终版
"""

import math
import random
import sys
from collections.abc import Callable

LOW, HIGH = 1, 100
MAX_ATTEMPTS = 7


def show(expr: str) -> None:
    try:
        print(f"   {expr:<26} → {eval(expr, {'math': math})!r}")
    except Exception as e:  # noqa: BLE001  演示用
        print(f"   {expr:<26} → {type(e).__name__}: {e}")


def demo_empty_containers() -> None:
    print("=" * 70)
    print("1. 空容器：哪些会报错，哪些不会")
    for e in ("len([])", "sum([])", "max([])", "min([])", "max([], default=0)",
              "[][-1]", "sum([]) / len([])", "sorted([])"):
        show(e)


def demo_vacuous_truth() -> None:
    print("=" * 70)
    print("2. all / any 对空容器")
    for e in ("all([])", "any([])", "all([True, False])", "any([False, True])"):
        show(e)
    print("   ↑ all([]) 是 True：「所有元素都满足」在没有元素时成立")


def demo_split() -> None:
    print("=" * 70)
    print("3. split() 的空字符串边界")
    for e in ("''.split(',')", "''.split()", "' a  b '.split()",
              "' a  b '.split(' ')", "'a,,b'.split(',')", "'50,'.split(',')"):
        show(e)
    print("   ↑ 带参数时：空字符串切出 ['']（一个空串），不是 []")


def demo_division() -> None:
    print("=" * 70)
    print("4. 除法的三个运算符")
    for e in ("7 / 2", "6 / 2", "7 // 2", "-7 // 2", "7 % 2", "-7 % 2",
              "divmod(17, 5)", "int(-3.5)", "math.floor(-3.5)", "1 % 0"):
        show(e)
    print("   ↑ // 向下取整（朝负无穷）；int() 向零截断。正数时一样，负数时不同")


def demo_float_sum() -> None:
    print("=" * 70)
    print("5. 浮点数求和")
    for e in ("0.1 + 0.2", "sum([0.1] * 10)", "math.fsum([0.1] * 10)"):
        show(e)
    print(f"   当前 Python {sys.version.split()[0]}；3.11 及更早的 sum([0.1] * 10) "
          "是 0.9999999999999999")


def demo_key_function() -> None:
    print("=" * 70)
    print("6. max / min / sorted 的 key 参数")
    history = [50, 30, 45, 40]
    print(f"   history = {history}，target = 42")
    print(f"   min(history, key=lambda g: abs(g - 42)) → "
          f"{min(history, key=lambda g: abs(g - 42))}   离 42 最近的")
    print(f"   min([44, 40], key=lambda g: abs(g - 42)) → "
          f"{min([44, 40], key=lambda g: abs(g - 42))}   并列时取先出现的")
    print(f"   sorted(history, reverse=True) → {sorted(history, reverse=True)}")


def in_range_wrong(x: int) -> bool:
    """✗ 枚举非法情况：漏掉了 0。"""
    return not (x < 0 or x > 100)


def in_range_right(x: int) -> bool:
    """✓ 描述合法区间。"""
    return 1 <= x <= 100


def demo_range_check() -> None:
    print("=" * 70)
    print("7. 范围判断：枚举非法 vs 描述合法")
    for x in (-1, 0, 1, 100, 101):
        print(f"   x={x:>3}  x<0 or x>100 判为合法: {in_range_wrong(x)!s:<5}"
              f"  1<=x<=100: {in_range_right(x)}")
    print("   ↑ 0 被第一种写法放过了")


# ============================================================================
# M1 最终版猜数字
# ============================================================================


def parse_int(raw: str) -> int | None:
    try:
        return int(raw)
    except ValueError:
        return None


def check_num(guess: int, target: int) -> str:
    if guess == target:
        return "正确"
    if guess < target:
        return "小了"
    return "大了"


def play(
    target: int,
    max_attempts: int = MAX_ATTEMPTS,
    ask: Callable[[str], str] = input,
    say: Callable[[str], None] = print,
) -> list[int]:
    history: list[int] = []
    seen: set[int] = set()
    while len(history) < max_attempts:
        raw = ask(f"[{len(history) + 1}/{max_attempts}] 你猜： ")
        if raw.strip().lower() in ("q", "quit"):
            break
        guess = parse_int(raw)
        if guess is None or not LOW <= guess <= HIGH:
            say(f"   {raw!r} 不是 {LOW}-{HIGH} 之间的整数，这次不算")
            continue
        if guess in seen:
            say(f"   {guess} 已经猜过了，这次不算")
            continue
        seen.add(guess)
        history.append(guess)
        result = check_num(guess, target)
        say(f"   {guess:>3} → {result}")
        if result == "正确":
            break
    return history


def statistics(history: list[int], target: int) -> list[str]:
    """守卫语句：先把空列表挡在外面，后面的代码就不用再担心它。"""
    lines = [f"有效猜测 {len(history)} 次"]
    if not history:
        lines.append("一次都没猜，暂无统计")
        return lines

    avg = sum(history) / len(history)
    lines.append(f"最大 {max(history)}，最小 {min(history)}，平均 {avg:.2f}")
    if history[-1] == target:
        lines.append(f"猜中了，答案是 {target}")
    else:
        closest = min(history, key=lambda g: abs(g - target))
        lines.append(f"没猜中，答案是 {target}，离它最近的一次是 {closest}")
    return lines


def main() -> None:
    if len(sys.argv) > 1 and sys.argv[1] == "play":
        target = random.Random().randint(LOW, HIGH)
        print(f"我想好了一个 {LOW}-{HIGH} 之间的数，你有 {MAX_ATTEMPTS} 次机会。")
        history = play(target)
        print("\n".join(statistics(history, target)))
        return

    demo_empty_containers()
    demo_vacuous_truth()
    demo_split()
    demo_division()
    demo_float_sum()
    demo_key_function()
    demo_range_check()
    print("=" * 70)
    print("想玩 M1 最终版：python -m m01_basics.ch01_09_example play")
    print("试试一次都不猜直接输入 q —— 统计部分不应该崩。")


if __name__ == "__main__":
    main()
