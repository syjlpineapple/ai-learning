"""第 1.1 章 · 讲解里的可运行示例。

两种跑法：

    python -m m01_basics.ch01_01_example          # 看演示输出
    python -m m01_basics.ch01_01_example play     # 玩第一版猜数字

演示部分不需要键盘输入，玩游戏那部分需要。
"""

import sys

TARGET = 10


def demo_input_is_always_str() -> None:
    """input() 的返回值永远是 str。这里用一个写死的字符串模拟用户输入了 18。"""
    print("=" * 70)
    print("1. input() 拿到的永远是字符串")
    age = "18"  # 相当于 age = input("年龄：") 且用户输入了 18
    print(f"   type(age) = {type(age)}")

    for expr, run in (
        ('age > 10', lambda: age > 10),  # type: ignore[operator]
        ('age + 1', lambda: age + 1),  # type: ignore[operator]
        ('age * 3', lambda: age * 3),
        ('int(age) > 10', lambda: int(age) > 10),
    ):
        try:
            print(f"   {expr:<16} → {run()!r}")
        except TypeError as e:
            print(f"   {expr:<16} → TypeError: {e}")


def demo_string_comparison() -> None:
    """字符串之间也能比较大小，但比的是字典序，不是数值。"""
    print("=" * 70)
    print("2. 字符串比较是按字符逐个比，不是按数值")
    print(f"   '9' > '10'   → {'9' > '10'}      ← 比的是第一个字符 '9' 和 '1'")
    print(f"   9 > 10       → {9 > 10}")


def demo_conversion_edges() -> None:
    """int() / float() 的转换边界。这张表值得背下来。"""
    print("=" * 70)
    print("3. int() / float() 的转换边界")
    cases = [
        'int("42")', 'int("abc")', 'int("")', 'int("3.14")',
        "int(3.99)", "int(-3.99)",
        'int(" 42 ")', 'int("+7")', 'int("-7")', 'int("1_000")', 'int("４２")',
        'float("3.14")', 'float("1e3")', 'float("abc")',
    ]
    for expr in cases:
        try:
            print(f"   {expr:<16} → {eval(expr)!r}")
        except ValueError as e:
            print(f"   {expr:<16} → ValueError: {e}")


def check_num(guess: int, target: int) -> str:
    """比较猜测值和目标值。

    这是整门课的第一个函数。def 的完整语法在第 1.6 章讲，
    现在只需知道：调用 check_num(3, 10) 会得到 "小了"。
    """
    if guess == target:
        return "正确"
    elif guess < target:
        return "小了"
    else:
        return "大了"


def play_v1() -> None:
    """第一版猜数字：只猜一次，输入不是整数会直接崩。

    这一版故意保留了「输入 abc 会崩」的问题，1.2 和 1.5 会逐步修掉它。
    """
    guess = int(input(f"猜一个数字（答案是 {TARGET}，测试用）： "))
    print(check_num(guess, TARGET))


def main() -> None:
    if len(sys.argv) > 1 and sys.argv[1] == "play":
        play_v1()
        return

    demo_input_is_always_str()
    demo_string_comparison()
    demo_conversion_edges()
    print("=" * 70)
    print("想玩第一版猜数字：python -m m01_basics.ch01_01_example play")
    print("试试输入 abc，看看会发生什么。")


if __name__ == "__main__":
    main()
