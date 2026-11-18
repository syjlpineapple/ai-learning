"""第 1.3 章 · 讲解里的可运行示例。

    python -m m01_basics.ch01_03_example                  # 看演示输出
    python -m m01_basics.ch01_03_example play             # 玩第三版猜数字（循环）
    python -m m01_basics.ch01_03_example ending break     # 单独看 break 的效果
    python -m m01_basics.ch01_03_example ending continue
    python -m m01_basics.ch01_03_example ending exit      # 注意看最后一行有没有打印

ending 那三条命令是这一章最重要的实验，务必各跑一次。
"""

import sys

TARGET = 42
MAX_ATTEMPTS = 5


def demo_ending(mode: str) -> None:
    """同一个循环，第 2 次时分别用 break / continue / exit() 打断。

    循环结束后有一行「保存成绩」—— 看它在哪种模式下被跳过。
    """
    for attempt in range(1, 4):
        print(f"第 {attempt} 次尝试")
        if attempt == 2:
            if mode == "break":
                break
            elif mode == "continue":
                continue
            elif mode == "exit":
                sys.exit()
        print(f"   第 {attempt} 次的循环体后半段")

    print("循环结束后：保存成绩、打印统计")


def demo_exit_is_an_exception() -> None:
    """exit() 的本质是抛出 SystemExit 异常。"""
    print("=" * 70)
    print("1. exit() 的本质")
    try:
        sys.exit()
    except SystemExit as e:
        print(f"   sys.exit() 抛出了 {type(e).__name__}，code={e.code!r}")

    print(f"   SystemExit 的继承链：{[c.__name__ for c in SystemExit.__mro__]}")
    print("   ↑ 它继承的是 BaseException，不是 Exception")
    print("     所以 except Exception 接不住它 —— 这是故意设计的")


def demo_range() -> None:
    print("=" * 70)
    print("2. range() 的三种写法")
    print(f"   list(range(5))        → {list(range(5))}")
    print(f"   list(range(1, 6))     → {list(range(1, 6))}      ← 不含结束值")
    print(f"   list(range(0, 10, 3)) → {list(range(0, 10, 3))}")
    print(f"   list(range(5, 0, -1)) → {list(range(5, 0, -1))}")


def demo_nested_break() -> None:
    print("=" * 70)
    print("3. 嵌套循环里的 break 只跳出最内层")
    for outer in range(1, 4):
        for inner in range(1, 4):
            if inner == 2:
                break
            print(f"   outer={outer} inner={inner}")
    print("   ↑ 外层循环跑满了 3 次，break 只结束了内层")


def demo_while_vs_for() -> None:
    print("=" * 70)
    print("4. 什么时候用 while，什么时候用 for")
    print("   次数已知（猜 5 次）       → for attempt in range(5)")
    print("   次数未知（直到猜中为止）  → while True + break")
    count = 0
    n = 27
    while n != 1:
        n = n // 2 if n % 2 == 0 else 3 * n + 1
        count += 1
    print(f"   例：从 27 开始做 3n+1 变换，{count} 步后到达 1 —— 事先不知道要几步")


def looks_like_int(raw: str) -> bool:
    """上一章练习 3 的成果。"""
    body = raw.strip()
    if body and body[0] in "+-":
        body = body[1:]
    return body != "" and body.isdecimal()


def check_num(guess: int, target: int) -> str:
    if guess == target:
        return "正确"
    elif guess < target:
        return "小了"
    else:
        return "大了"


def play_v3() -> None:
    """第三版：循环 + 次数上限 + 主动退出。

    三种结束方式都用 break 或自然结束，没有一处用 exit()。
    所以循环后面那行「本局结束」在任何情况下都会执行。
    """
    attempts = 0
    while attempts < MAX_ATTEMPTS:
        raw = input(f"第 {attempts + 1}/{MAX_ATTEMPTS} 次，猜 1-100（q 退出）： ")

        if raw.strip().lower() in ("q", "quit"):
            print("你选择了退出")
            break

        if not looks_like_int(raw):
            print(f"   '{raw}' 不是整数，这次不算")
            continue

        attempts += 1
        result = check_num(int(raw), TARGET)
        print(f"   {result}")
        if result == "正确":
            print(f"   用了 {attempts} 次")
            break
    else:
        # while 的条件变成假（次数用完）时才进这里；被 break 打断时不进
        print(f"次数用完了，答案是 {TARGET}")

    print("本局结束")


def main() -> None:
    args = sys.argv[1:]
    if args[:1] == ["play"]:
        play_v3()
        return
    if args[:1] == ["ending"] and len(args) == 2:
        demo_ending(args[1])
        return

    demo_exit_is_an_exception()
    demo_range()
    demo_nested_break()
    demo_while_vs_for()
    print("=" * 70)
    print("接下来务必跑这三条，对比最后一行：")
    print("   python -m m01_basics.ch01_03_example ending break")
    print("   python -m m01_basics.ch01_03_example ending continue")
    print("   python -m m01_basics.ch01_03_example ending exit")


if __name__ == "__main__":
    main()
