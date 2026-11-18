"""第 1.7 章 · 讲解里的可运行示例。

    python -m m01_basics.ch01_07_example          # 看演示输出
    python -m m01_basics.ch01_07_example play     # 玩第七版猜数字（带历史记录）
"""

import copy
import random
import sys
import timeit
from collections.abc import Callable

LOW, HIGH = 1, 100
MAX_ATTEMPTS = 7


def show(expr: str, scope: dict[str, object] | None = None) -> None:
    try:
        print(f"   {expr:<26} → {eval(expr, scope)!r}")
    except Exception as e:  # noqa: BLE001  演示用
        print(f"   {expr:<26} → {type(e).__name__}: {e}")


def demo_index_and_slice() -> None:
    print("=" * 70)
    print("1. 索引与切片（items = [10, 20, 30, 40, 50]）")
    scope: dict[str, object] = {"items": [10, 20, 30, 40, 50]}
    for e in ("items[0]", "items[-1]", "items[5]", "items[1:3]", "items[:3]",
              "items[3:]", "items[::2]", "items[::-1]", "items[10:20]"):
        show(e, scope)
    print("   ↑ 索引越界会报错，切片越界不会 —— 它只返回能取到的部分")


def demo_in_place_returns_none() -> None:
    print("=" * 70)
    print("2. 原地修改的方法返回 None")
    items = [3, 1, 2]
    r = items.sort()
    print(f"   r = items.sort()      → r={r!r}，items 被原地排好了：{items}")
    items2: list[int] | None = [3, 1, 2]
    items2 = items2.sort()  # type: ignore[union-attr]
    print(f"   items = items.sort()  → items={items2!r}   ← 列表没了")
    print(f"   sorted([3, 1, 2])     → {sorted([3, 1, 2])}   ← 返回新列表，原列表不变")
    a: list[object] = [1, 2]
    a.append([3, 4])
    b = [1, 2]
    b.extend([3, 4])
    c: list[object] = [1, 2]
    c.extend("ab")
    print(f"   append([3, 4]) → {a}")
    print(f"   extend([3, 4]) → {b}")
    print(f"   extend('ab')   → {c}   ← 字符串被拆成了单个字符")


def demo_reference() -> None:
    print("=" * 70)
    print("3. 赋值是引用，不是拷贝")
    a = [1, 2, 3]
    b = a
    b.append(4)
    print(f"   b = a; b.append(4)       → a = {a}    a is b: {a is b}")
    c = a.copy()
    c.append(5)
    print(f"   c = a.copy(); c.append(5) → a = {a}    a is c: {a is c}")

    nested = [[1, 2], [3, 4]]
    shallow = nested.copy()
    shallow[0].append(99)
    print(f"   浅拷贝后改内层            → 原列表 = {nested}")
    print(f"                                nested[0] is shallow[0]: {nested[0] is shallow[0]}")
    nested = [[1, 2], [3, 4]]
    deep = copy.deepcopy(nested)
    deep[0].append(99)
    print(f"   深拷贝后改内层            → 原列表 = {nested}")


def demo_grid_trap() -> None:
    print("=" * 70)
    print("4. [[0] * 3] * 3 陷阱")
    g = [[0] * 3] * 3
    g[0][0] = 1
    print(f"   g = [[0] * 3] * 3; g[0][0] = 1 → {g}")
    print(f"   g[0] is g[1] is g[2]: {g[0] is g[1] is g[2]}")
    h = [[0] * 3 for _ in range(3)]
    h[0][0] = 1
    print(f"   推导式版本                     → {h}")


def add_bonus(scores: list[int]) -> None:
    scores.append(100)


def rebind(scores: list[int]) -> None:
    scores = [0]  # noqa: F841  故意的：演示重新绑定不影响调用方


def demo_function_argument() -> None:
    print("=" * 70)
    print("5. 把列表传给函数")
    mine = [60, 70]
    add_bonus(mine)
    print(f"   add_bonus(mine) 之后 mine = {mine}   ← 函数改到了调用方的列表")
    mine2 = [60, 70]
    rebind(mine2)
    print(f"   rebind(mine2) 之后 mine2 = {mine2}        ← 重新绑定不影响调用方")


def demo_remove_while_iterating() -> None:
    print("=" * 70)
    print("6. 遍历时删除元素")
    items = [-1, -2, 3, -4, 5]
    for x in items:
        if x < 0:
            items.remove(x)
    print(f"   从 [-1, -2, 3, -4, 5] 删负数 → {items}   ← -2 没删掉")
    items = [-1, -2, 3, -4, 5]
    print(f"   推导式建新列表             → {[x for x in items if x >= 0]}")
    items = [-1, -2, 3, -4, 5]
    alias = items
    items[:] = [x for x in items if x >= 0]
    print(f"   items[:] = ...  → items = {items}  alias = {alias}   （原地替换）")
    items = [-1, -2, 3, -4, 5]
    alias = items
    items = [x for x in items if x >= 0]
    print(f"   items = ...     → items = {items}  alias = {alias}   （重新绑定）")


def demo_in_speed() -> None:
    print("=" * 70)
    print("7. in 的速度：list 逐个比较，set 直接定位")
    big_list = list(range(100_000))
    big_set = set(big_list)
    t_list = timeit.timeit(lambda: 99_999 in big_list, number=1000)
    t_set = timeit.timeit(lambda: 99_999 in big_set, number=1000)
    print("   10 万个元素，查最后一个，各 1000 次：")
    print(f"   list: {t_list * 1000:8.2f} ms")
    print(f"   set : {t_set * 1000:8.3f} ms   （约快 {t_list / t_set:,.0f} 倍，具体数字因机器而异）")


# ============================================================================
# 第七版猜数字：记录历史
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
    """返回本局所有有效猜测。

    注意没有单独的 attempts 计数器：次数就是 len(history)。
    两个变量表达同一件事，迟早会有一个分支只改了其中一个。
    """
    history: list[int] = []
    while len(history) < max_attempts:
        raw = ask(f"[{len(history) + 1}/{max_attempts}] 你猜： ")
        if raw.strip().lower() in ("q", "quit"):
            say("你选择了退出")
            break
        guess = parse_int(raw)
        if guess is None or not LOW <= guess <= HIGH:
            say(f"   {raw!r} 不是 {LOW}-{HIGH} 之间的整数，这次不算")
            continue
        if guess in history:
            say(f"   {guess} 已经猜过了，这次不算")
            continue

        history.append(guess)
        result = check_num(guess, target)
        say(f"   {guess:>3} → {result}")
        if result == "正确":
            break
    return history


def summarize(history: list[int], target: int) -> str:
    if not history:
        return "一次都没猜"
    won = history[-1] == target
    trail = " → ".join(str(g) for g in history)
    status = f"猜中了，用了 {len(history)} 次" if won else f"没猜中，答案是 {target}"
    return f"{status}。轨迹：{trail}"


def main() -> None:
    if len(sys.argv) > 1 and sys.argv[1] == "play":
        target = random.Random().randint(LOW, HIGH)
        print(f"我想好了一个 {LOW}-{HIGH} 之间的数，你有 {MAX_ATTEMPTS} 次机会。")
        history = play(target)
        print(summarize(history, target))
        return

    demo_index_and_slice()
    demo_in_place_returns_none()
    demo_reference()
    demo_grid_trap()
    demo_function_argument()
    demo_remove_while_iterating()
    demo_in_speed()
    print("=" * 70)
    print("想玩第七版：python -m m01_basics.ch01_07_example play")


if __name__ == "__main__":
    main()
