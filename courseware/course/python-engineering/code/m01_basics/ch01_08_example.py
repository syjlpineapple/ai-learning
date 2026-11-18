"""第 1.8 章 · 讲解里的可运行示例。

    python -m m01_basics.ch01_08_example          # 看演示输出
    python -m m01_basics.ch01_08_example play     # 玩第八版猜数字（多人排行榜）
"""

import random
import sys
from collections import Counter
from collections.abc import Callable

LOW, HIGH = 1, 100
MAX_ATTEMPTS = 7


def show(expr: str, scope: dict[str, object] | None = None) -> None:
    try:
        print(f"   {expr:<34} → {eval(expr, scope)!r}")
    except Exception as e:  # noqa: BLE001  演示用
        print(f"   {expr:<34} → {type(e).__name__}: {e}")


def demo_dict_basics() -> None:
    print("=" * 70)
    print('1. 字典基础（d = {"张三": 3, "李四": 5}）')
    scope: dict[str, object] = {"d": {"张三": 3, "李四": 5}}
    for e in ('d["张三"]', 'd["王五"]', 'd.get("王五")', 'd.get("王五", 0)',
              '"张三" in d', "3 in d", "3 in d.values()", "list(d.items())"):
        show(e, scope)
    print("   ↑ in 查的是键，不是值")


def demo_hashable_keys() -> None:
    print("=" * 70)
    print("2. 键必须可哈希；值相等的键会合并")
    for e in ("{[1, 2]: 'x'}", "{(1, 2): 'x'}", "{1: 'a', True: 'b'}",
              "{1: 'a', 1.0: 'b'}", "hash(1) == hash(True) == hash(1.0)",
              "{'a': 1, 'a': 2}"):
        show(e)
    print("   ↑ True == 1 == 1.0，而且哈希值也相同，所以它们是同一个键")


def demo_modify_while_iterating() -> None:
    print("=" * 70)
    print("3. 遍历字典时改变它的大小")
    d = {"a": 1, "b": 2, "c": 3}
    try:
        for k in d:
            if k == "a":
                del d[k]
    except RuntimeError as e:
        print(f"   边遍历边删 → RuntimeError: {e}")
    d = {"a": 1, "b": 2, "c": 3}
    for k in list(d):
        if d[k] < 2:
            del d[k]
    print(f"   for k in list(d) 先拍快照再删 → {d}")
    print("   ↑ 列表遍历时删除会悄悄漏删（第 1.7 章），字典会直接报错 —— 报错反而是好事")


def demo_counting() -> None:
    print("=" * 70)
    print("4. 计数的三种写法")
    results = ["大了", "小了", "大了", "正确"]
    try:
        naive: dict[str, int] = {}
        for r in results:
            naive[r] += 1
    except KeyError as e:
        print(f"   直接 counts[r] += 1  → KeyError: {e}")
    counts: dict[str, int] = {}
    for r in results:
        counts[r] = counts.get(r, 0) + 1
    print(f"   counts.get(r, 0) + 1 → {counts}")
    print(f"   Counter(results)     → {dict(Counter(results))}")


def demo_tuple() -> None:
    print("=" * 70)
    print("5. 元组")
    for e in ("(1)", "(1,)", "1, 2", "tuple([1, 2])"):
        show(e)
    t = ([1, 2], 3)
    try:
        t[0] += [3]
    except TypeError as e:
        print(f"   t = ([1, 2], 3); t[0] += [3] → TypeError: {e}")
    print(f"   但是 t 已经变成了 {t}   ← 报错了，修改却生效了")
    x, y = 1, 2
    x, y = y, x
    print(f"   x, y = y, x → x={x}, y={y}")
    first, *rest = [50, 30, 42]
    print(f"   first, *rest = [50, 30, 42] → first={first}, rest={rest}")


def demo_set() -> None:
    print("=" * 70)
    print("6. 集合")
    for e in ("type({})", "type(set())", "{1, 2, 2, 3}", "{1, 2} | {2, 3}",
              "{1, 2} & {2, 3}", "{1, 2} - {2, 3}", "{1, 2} ^ {2, 3}",
              "{True, 1, 1.0}", "list(set([3, 1, 3, 2]))",
              "list(dict.fromkeys([3, 1, 3, 2]))"):
        show(e)
    print("   ↑ 最后两行：set 去重不保证顺序；dict.fromkeys 去重保留首次出现的顺序")


# ============================================================================
# 第八版猜数字：多人排行榜
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
) -> list[tuple[int, str]]:
    """返回本局的每一步：(猜的数, 结果)。

    用 set 记录猜过的数：判断「猜过没有」是 O(1)。
    用 list 记录轨迹：要保留顺序。
    两者各管一件事。
    """
    steps: list[tuple[int, str]] = []
    seen: set[int] = set()
    while len(steps) < max_attempts:
        raw = ask(f"[{len(steps) + 1}/{max_attempts}] 你猜： ")
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
        result = check_num(guess, target)
        steps.append((guess, result))
        say(f"   {guess:>3} → {result}")
        if result == "正确":
            break
    return steps


def record_round(board: dict[str, int], name: str, steps: list[tuple[int, str]]) -> bool:
    """把一局的成绩记进排行榜。只记猜中的局，只保留每人最少的次数。

    原地修改 board，返回「是否刷新了这个人的纪录」。
    """
    if not steps or steps[-1][1] != "正确":
        return False
    attempts = len(steps)
    best = board.get(name)
    if best is None or attempts < best:
        board[name] = attempts
        return True
    return False


def format_board(board: dict[str, int]) -> list[str]:
    """按次数从少到多排序。sorted 对 items() 排序，key 取元组的第二个元素。"""
    ranked = sorted(board.items(), key=lambda item: item[1])
    return [f"{rank:>2}. {name}  {attempts} 次" for rank, (name, attempts) in
            enumerate(ranked, start=1)]


def main() -> None:
    if len(sys.argv) > 1 and sys.argv[1] == "play":
        board: dict[str, int] = {}
        while True:
            name = input("玩家名字（直接回车结束）： ").strip()
            if not name:
                break
            steps = play(random.Random().randint(LOW, HIGH))
            if record_round(board, name, steps):
                print(f"   {name} 刷新了个人纪录！")
        print("\n".join(format_board(board)) or "没有人猜中")
        return

    demo_dict_basics()
    demo_hashable_keys()
    demo_modify_while_iterating()
    demo_counting()
    demo_tuple()
    demo_set()
    print("=" * 70)
    print("想玩第八版：python -m m01_basics.ch01_08_example play")


if __name__ == "__main__":
    main()
