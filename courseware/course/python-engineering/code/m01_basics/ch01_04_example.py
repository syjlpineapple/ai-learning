"""第 1.4 章 · 讲解里的可运行示例。

    python -m m01_basics.ch01_04_example          # 看演示输出
    python -m m01_basics.ch01_04_example play     # 玩第四版猜数字（随机答案）
"""

import random
import sys
import unicodedata

LOW, HIGH = 1, 100
MAX_ATTEMPTS = 7


def show(expr: str, scope: dict[str, object] | None = None) -> None:
    try:
        print(f"   {expr:<30} → {eval(expr, scope)!r}")
    except Exception as e:  # noqa: BLE001  演示用
        print(f"   {expr:<30} → {type(e).__name__}: {e}")


def demo_import_trap() -> None:
    """from random import random 导入的是函数，不是模块。"""
    print("=" * 70)
    print("1. from random import random 之后，random 是什么")
    scope: dict[str, object] = {}
    exec("from random import random", scope)
    print(f"   type(random) = {type(scope['random']).__name__}")
    show("random.randint(1, 100)", scope)
    print("   ↑ 导入的是 random 模块里那个叫 random 的函数，它没有 randint")


def demo_randint_closed() -> None:
    print("=" * 70)
    print("2. randint 两端都包含，range 不含结尾")
    rng = random.Random(0)
    counts = {1: 0, 2: 0, 3: 0}
    for _ in range(10000):
        counts[rng.randint(1, 3)] += 1
    print(f"   10000 次 randint(1, 3) 的分布：{counts}")
    print(f"   list(range(1, 3))           ：{list(range(1, 3))}")


def demo_seed() -> None:
    print("=" * 70)
    print("3. 种子相同，随机序列就相同")
    for _ in range(2):
        random.seed(42)
        print(f"   seed(42) 后连续 5 次：{[random.randint(1, 100) for _ in range(5)]}")
    a, b = random.Random(42), random.Random(42)
    print(f"   两个独立的 Random(42) 实例：{a.randint(1, 100)} 和 {b.randint(1, 100)}")


def demo_missing_f() -> None:
    print("=" * 70)
    print("4. 两种不报错的格式化错误")
    num = 56
    print("   漏掉 f      →", "随机数：{num}")
    print("   交给 print  →", end=" ")
    print("随机数：{}", num)
    print(f"   正确写法    → 随机数：{num}")


def demo_format_spec() -> None:
    print("=" * 70)
    print("5. 格式规格：冒号后面那一段")
    scope: dict[str, object] = {"name": "Tom", "x": 10, "y": 3}
    for e in ('f"{3.14159:.2f}"', 'f"{1234567:,}"', 'f"{0.85:.1%}"',
              'f"{42:>8}|"', 'f"{42:<8}|"', 'f"{42:^8}|"', 'f"{7:03}"',
              'f"{name!r}"', 'f"{x=}"', 'f"{x / y = :.2f}"', 'f"{{x}}"'):
        show(e, scope)


def demo_rounding() -> None:
    print("=" * 70)
    print("6. 四舍五入的两个意外")
    for e in ("round(2.5)", "round(3.5)", "round(0.5)", "round(2.675, 2)",
              "format(2.675, '.20f')"):
        show(e)
    print("   ↑ 前三行：round 是「四舍六入五成双」，不是四舍五入")
    print("   ↑ 后两行：2.675 在二进制里存不准，实际比 2.675 小一点点")


def display_width(text: str) -> int:
    """全角字符占两列。和第 0.2 章自检脚本里的是同一个函数。"""
    return sum(2 if unicodedata.east_asian_width(c) in ("W", "F") else 1 for c in text)


def demo_chinese_alignment() -> None:
    print("=" * 70)
    print("7. f-string 对齐按字符数算，中文会歪")
    for name in ("Tom", "张三", "欧阳修文"):
        print(f"   |{name:<8}|   len={len(name)}  显示宽度={display_width(name)}")


def make_target(seed: int | None = None) -> int:
    """生成答案。传 seed 时结果固定，方便测试。

    用 random.Random(seed) 而不是 random.seed(seed)：
    前者是一个独立的随机数生成器，不影响程序里其他地方用到的 random；
    后者改的是全局状态，谁调用都会受影响。
    """
    return random.Random(seed).randint(LOW, HIGH)


def check_num(guess: int, target: int) -> str:
    if guess == target:
        return "正确"
    elif guess < target:
        return "小了"
    else:
        return "大了"


def looks_like_int(raw: str) -> bool:
    body = raw.strip()
    if body and body[0] in "+-":
        body = body[1:]
    return body != "" and body.isdecimal()


def play_v4(seed: int | None = None) -> None:
    """第四版：答案随机，提示语用 f-string 排版。"""
    target = make_target(seed)
    print(f"我想好了一个 {LOW}-{HIGH} 之间的数，你有 {MAX_ATTEMPTS} 次机会。")

    attempts = 0
    while attempts < MAX_ATTEMPTS:
        raw = input(f"[{attempts + 1}/{MAX_ATTEMPTS}] 你猜： ")
        if raw.strip().lower() in ("q", "quit"):
            print("你选择了退出")
            break
        if not looks_like_int(raw):
            print(f"   {raw!r} 不是整数，这次不算")
            continue

        attempts += 1
        guess = int(raw)
        result = check_num(guess, target)
        print(f"   {guess:>3} → {result}")
        if result == "正确":
            print(f"   用了 {attempts} 次，机会使用率 {attempts / MAX_ATTEMPTS:.0%}")
            break
    else:
        print(f"次数用完了，答案是 {target}")

    print("本局结束")


def main() -> None:
    if len(sys.argv) > 1 and sys.argv[1] == "play":
        play_v4()
        return

    demo_import_trap()
    demo_randint_closed()
    demo_seed()
    demo_missing_f()
    demo_format_spec()
    demo_rounding()
    demo_chinese_alignment()
    print("=" * 70)
    print("想玩第四版：python -m m01_basics.ch01_04_example play")


if __name__ == "__main__":
    main()
