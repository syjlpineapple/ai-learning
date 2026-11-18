"""第 1.6 章 · 讲解里的可运行示例。

    python -m m01_basics.ch01_06_example          # 看演示输出
    python -m m01_basics.ch01_06_example play     # 玩第六版猜数字（拆成函数）
"""

import random
import subprocess
import sys
from collections.abc import Callable

LOW, HIGH = 1, 100
MAX_ATTEMPTS = 7


def last_error(code: str) -> str:
    """在子进程里跑一段代码，返回报错的最后一行。

    有些错误（NameError、UnboundLocalError）必须在一个干净的环境里才能复现，
    所以放到子进程里跑。
    """
    done = subprocess.run(
        [sys.executable, "-c", code], capture_output=True, text=True, encoding="utf-8"
    )
    lines = (done.stdout + done.stderr).strip().splitlines()
    return lines[-1] if lines else "（没有输出）"


def demo_def_is_a_statement() -> None:
    print("=" * 70)
    print("1. def 是一条要执行的语句：调用在 def 之前会报错")
    print("  ", last_error("f()\ndef f():\n    print('hi')"))


def show(x: int) -> None:
    print(f"   show 打印了 {x}")


def demo_return_vs_print() -> None:
    print("=" * 70)
    print("2. 没有 return 的函数返回 None")
    r = show(5)  # type: ignore[func-returns-value]
    print(f"   返回值 r = {r!r}   ← 屏幕上看到了 5，程序拿到的是 None")


def add_item(item: str, items: list[str] = []) -> list[str]:  # noqa: B006
    """✗ 错误示范：可变对象做默认值。"""
    items.append(item)
    return items


def demo_mutable_default() -> None:
    print("=" * 70)
    print("3. 可变默认值：所有调用共享同一个列表")
    print(f"   add_item('a') = {add_item('a')}")
    print(f"   add_item('b') = {add_item('b')}   ← 第二次调用，没传 items")
    print(f"   add_item.__defaults__ = {add_item.__defaults__}")
    print("   ↑ 默认值在 def 执行时创建一次，存在函数对象上，之后每次调用都复用它")


def check(guess: int, target: int) -> int:
    return guess - target


def check_kw(*, guess: int, target: int) -> int:
    """* 之后的参数只能用关键字传。"""
    return guess - target


def demo_arguments() -> None:
    print("=" * 70)
    print("4. 参数传错时的报错原文")
    for call in ("check(1)", "check(1, 2, 3)", "check(1, 2, goal=3)",
                 "check(1, guess=2)", "check_kw(50, 42)"):
        try:
            eval(call)
        except TypeError as e:
            print(f"   {call:<20} → TypeError: {e}")
    print()
    print(f"   参数传反不报错：check(50, 42) = {check(50, 42)}，"
          f"check(42, 50) = {check(42, 50)}")
    print(f"   强制关键字参数：check_kw(guess=50, target=42) = "
          f"{check_kw(guess=50, target=42)}")


def demo_scope() -> None:
    print("=" * 70)
    print("5. 作用域与遮蔽")
    print("   函数里给全局变量赋值：")
    print("  ", last_error("count = 0\ndef inc():\n    count = count + 1\ninc()"))
    print("   在函数外访问局部变量：")
    print("  ", last_error("def f():\n    y = 1\nf()\nprint(y)"))
    print("   变量名遮蔽了内置函数 sum：")
    print("  ", last_error("sum = 0\nprint(sum([1, 2, 3]))"))
    print("   结果覆盖了函数名：")
    print("  ", last_error("import random\ndef random_num():\n"
                           "    return random.randint(1, 9)\n"
                           "random_num = random_num()\nrandom_num()"))


def greet() -> str:
    return "hi"


def demo_first_class() -> None:
    print("=" * 70)
    print("6. 函数本身也是一个值")
    print(f"   greet   → {greet.__name__} 这个函数对象（不加括号 = 函数本身）")
    print(f"   greet() → {greet()!r}（加括号 = 调用它，得到返回值）")
    f = greet
    print(f"   f = greet; f() → {f()!r}")


def add(a: int, b: int) -> int:
    return "hello"  # type: ignore[return-value]  # 故意的错误示范


def demo_annotations() -> None:
    print("=" * 70)
    print("7. 类型注解不做运行时检查")
    print(f"   add(1, 2) = {add(1, 2)!r}   ← 注解写的是 -> int，实际返回了字符串")
    print("   但 mypy 会在运行之前拦住它（去掉那行的 type: ignore 再跑 mypy 试试）")


def divide(a: int, b: int) -> tuple[int, int]:
    return a // b, a % b


def demo_multiple_return() -> None:
    print("=" * 70)
    print("8. 返回多个值，其实是返回一个元组")
    res = divide(17, 5)
    print(f"   divide(17, 5) = {res!r}   type = {type(res).__name__}")
    q, r = divide(17, 5)
    print(f"   q, r = divide(17, 5) → q={q}, r={r}")
    print("  ", last_error("def d(a, b):\n    return a // b, a % b\nq, r, x = d(17, 5)"))


# ============================================================================
# 第六版猜数字：拆成一组各管一件事的函数
# ============================================================================


def make_target(seed: int | None = None) -> int:
    return random.Random(seed).randint(LOW, HIGH)


def parse_int(raw: str) -> int | None:
    try:
        return int(raw)
    except ValueError:
        return None


def is_quit(raw: str) -> bool:
    return raw.strip().lower() in ("q", "quit")


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
) -> str:
    """一局游戏。返回结局，不自己决定程序要不要退出。

    ask 和 say 默认就是 input 和 print。测试时可以换成假的：
        play(42, ask=假的输入函数, say=收集输出的函数)
    这样不需要 monkeypatch 也能测。能这样做，是因为函数本身也是一个值（第 6 节）。
    """
    attempts = 0
    while attempts < max_attempts:
        raw = ask(f"[{attempts + 1}/{max_attempts}] 你猜： ")
        if is_quit(raw):
            return "主动退出"

        guess = parse_int(raw)
        if guess is None or not LOW <= guess <= HIGH:
            say(f"   {raw!r} 不是 {LOW}-{HIGH} 之间的整数，这次不算")
            continue

        attempts += 1
        result = check_num(guess, target)
        say(f"   {guess:>3} → {result}")
        if result == "正确":
            return f"猜中了，用了 {attempts} 次"

    return f"次数用完了，答案是 {target}"


def main() -> None:
    if len(sys.argv) > 1 and sys.argv[1] == "play":
        print(f"我想好了一个 {LOW}-{HIGH} 之间的数，你有 {MAX_ATTEMPTS} 次机会。")
        print(play(make_target()))
        print("本局结束")
        return

    demo_def_is_a_statement()
    demo_return_vs_print()
    demo_mutable_default()
    demo_arguments()
    demo_scope()
    demo_first_class()
    demo_annotations()
    demo_multiple_return()
    print("=" * 70)
    print("想玩第六版：python -m m01_basics.ch01_06_example play")


if __name__ == "__main__":
    main()
