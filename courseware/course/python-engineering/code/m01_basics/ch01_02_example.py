"""第 1.2 章 · 讲解里的可运行示例。

    python -m m01_basics.ch01_02_example          # 看演示输出
    python -m m01_basics.ch01_02_example play     # 玩第二版猜数字（带输入校验）
"""

import sys

TARGET = 10


def show(expr: str) -> None:
    """计算一个表达式并打印结果。报错时打印异常类型。"""
    try:
        print(f"   {expr:<30} → {eval(expr)!r}")
    except Exception as e:  # noqa: BLE001  演示用，什么错都要打印出来
        print(f"   {expr:<30} → {type(e).__name__}: {e}")


def demo_truthiness() -> None:
    print("=" * 70)
    print("1. 真值测试：哪些值在 if 里算「假」")
    for v in ("False", "None", "0", "0.0", '""', "[]", "{}", "()", "set()"):
        show(f"bool({v})")
    print("   --- 下面这些都是「真」，最后两行最容易误判 ---")
    for v in ('" "', "[0]", "-1", '"0"', '"False"'):
        show(f"bool({v})")


def demo_and_or_return_operand() -> None:
    print("=" * 70)
    print("2. and / or 返回的是操作数本身，不一定是 True / False")
    for e in ('"" or "匿名"', '"张三" or "匿名"', '0 or "无限制"',
              '1 and "后面的值"', '0 and 1/0', 'not ""'):
        show(e)
    print("   注意 0 and 1/0 没有报错 —— and 左边为假时，右边根本不执行（短路）")


def demo_is_vs_eq() -> None:
    print("=" * 70)
    print("3. is 比较身份，== 比较值")
    a = [1, 2, 3]
    b = [1, 2, 3]
    c = a
    print(f"   a == b → {a == b}    a is b → {a is b}    a is c → {a is c}")
    show("isinstance(42, int)")
    show("isinstance('42', int)")
    show("isinstance(True, int)")
    show("type(True) is int")
    print("   ↑ bool 是 int 的子类。isinstance 认子类，type(...) is 不认")


def demo_digit_methods() -> None:
    print("=" * 70)
    print("4. isdigit() 和 int() 的判断并不一致")
    print(f"   {'输入':<8}{'isdigit':<10}{'isdecimal':<12}int()")
    for s in ("123", "-5", " 42", "3.14", "", "４２", "²"):
        try:
            converted = repr(int(s))
        except ValueError:
            converted = "ValueError"
        print(f"   {s!r:<8}{s.isdigit()!s:<10}{s.isdecimal()!s:<12}{converted}")
    print("   ↑ '-5' 和 ' 42'：isdigit 说不行，int 说行")
    print("   ↑ '²'（上标 2）：isdigit 说行，int 说不行  ← 会让程序崩溃")


def demo_chained_and_precedence() -> None:
    print("=" * 70)
    print("5. 链式比较与优先级")
    for e in ("1 <= 5 <= 100", "1 <= 150 <= 100",
              "False == False or True", "True == False or True"):
        show(e)
    print("   ↑ 后两行：== 比 or 优先级高，所以 X == False or True 永远是 True")


def check_num(guess: int, target: int) -> str:
    """上一章的成果。"""
    if guess == target:
        return "正确"
    elif guess < target:
        return "小了"
    else:
        return "大了"


def play_v2() -> None:
    """第二版：先校验再转换。

    用的是 isdigit()，所以有两个已知问题，演示部分第 4 节都展示了：
      - 输入 -5 会被当成非法（isdigit 不认负号）
      - 输入 ² 会通过校验，然后 int() 崩溃
    这两个问题在练习 3 里修。
    """
    raw = input(f"猜一个数字（答案是 {TARGET}，测试用）： ")
    if raw.isdigit():
        print(check_num(int(raw), TARGET))
    else:
        print(f"'{raw}' 不是整数")


def main() -> None:
    if len(sys.argv) > 1 and sys.argv[1] == "play":
        play_v2()
        return

    demo_truthiness()
    demo_and_or_return_operand()
    demo_is_vs_eq()
    demo_digit_methods()
    demo_chained_and_precedence()
    print("=" * 70)
    print("想玩第二版：python -m m01_basics.ch01_02_example play")
    print("试试输入 abc、-5、²（Windows 下按 Alt+0178 输入上标 2）。")


if __name__ == "__main__":
    main()
