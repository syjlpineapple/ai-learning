"""第 3.2 章 · 讲解里的可运行示例。

    python -m m03_structure.ch03_02_example          打印讲解里的各个实验
    python -m m03_structure.ch03_02_example play     玩一局（类版本的猜数字）

文件分三部分：
    一、本章的载体：GuessGame 类和用它的 play()
    二、实验用的小类：讲解里每个「意外」都对应一个，练习 1 也在这些类上出题
    三、演示
"""

from __future__ import annotations

import random
import sys
from collections.abc import Callable
from dataclasses import dataclass, field

# ============================================================================
# 一、载体：类版本的猜数字
# ============================================================================


class GuessError(ValueError):
    """猜测输入不合法。"""


class GameOverError(Exception):
    """游戏已经结束，不能再猜。"""


def parse_guess(raw: str, low: int = 1, high: int = 100) -> int:
    """和第 2.2 章一样的解析规则，这里简化成一个异常类。"""
    try:
        n = int(raw)
    except ValueError:
        raise GuessError(f"{raw!r} 不是整数") from None
    if not low <= n <= high:
        raise GuessError(f"{n} 不在 {low}-{high} 之间")
    return n


class GuessGame:
    """一局猜数字。

    以前分散在 play() 里的局部变量 —— 答案、次数上限、猜过的数 —— 现在是这个对象的属性；
    以前写在循环里的判断 —— 大了小了、还剩几次、结束没有 —— 现在是它的方法。
    """

    def __init__(self, target: int, max_attempts: int = 7, low: int = 1, high: int = 100) -> None:
        self.target = target
        self.max_attempts = max_attempts
        self.low = low
        self.high = high
        self.history: list[int] = []      # 每个对象一个新列表（讲解第 4 节）

    @classmethod
    def with_random_target(cls, seed: int | None = None, **options: int) -> GuessGame:
        """另一种构造方式：随机出题。seed 相同，答案相同（第 1.4 章）。"""
        low, high = options.get("low", 1), options.get("high", 100)
        return cls(random.Random(seed).randint(low, high), **options)

    def guess(self, n: int) -> str:
        if self.is_over:
            raise GameOverError(f"这局已经结束了（{self!r}）")
        self.history.append(n)
        if n < self.target:
            return "小了"
        if n > self.target:
            return "大了"
        return "正确"

    @property
    def remaining(self) -> int:
        return self.max_attempts - len(self.history)

    @property
    def won(self) -> bool:
        return bool(self.history) and self.history[-1] == self.target

    @property
    def is_over(self) -> bool:
        return self.won or self.remaining <= 0

    def __repr__(self) -> str:
        # 故意不显示 target：对象会出现在日志和报错里，答案不该跟着泄露
        return (f"GuessGame(range={self.low}-{self.high}, "
                f"attempts={len(self.history)}/{self.max_attempts}, won={self.won})")


def play(game: GuessGame, ask: Callable[[str], str] = input,
         say: Callable[[str], None] = print) -> GuessGame:
    """交互流程。规则全在 game 里，这里只管问和说（依赖注入，第 1.6 章）。"""
    say(f"我想好了一个 {game.low}-{game.high} 之间的数，你有 {game.max_attempts} 次机会。")
    while not game.is_over:
        raw = ask(f"[{len(game.history) + 1}/{game.max_attempts}] 你猜（q 退出）： ")
        if raw.strip() == "q":
            say("不玩了。")
            break
        try:
            n = parse_guess(raw, game.low, game.high)
        except GuessError as e:
            say(f"   {e}，这次不算")
            continue
        say(f"   {n:>3} → {game.guess(n)}")
    if game.won:
        say(f"   用了 {len(game.history)} 次。")
    elif game.remaining == 0:
        say(f"   机会用完了，答案是 {game.target}。")
    return game


# ============================================================================
# 二、实验用的小类
# ============================================================================


class Plain:
    """普通类：没写 __eq__，== 比的是「是不是同一个对象」。"""

    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y


@dataclass
class Point:
    """dataclass：自动生成 __init__、__repr__、__eq__ —— 但 __hash__ 被设成了 None。"""

    x: int
    y: int


@dataclass(frozen=True)
class FrozenPoint:
    """frozen=True：不可修改，于是可以哈希，能放进集合、当字典键。"""

    x: int
    y: int


class Shared:
    """⚠️ 列表写在类里：所有对象共用这一个列表。"""

    history: list[int] = []

    def add(self, n: int) -> None:
        self.history.append(n)       # 读到的是类属性，append 改的就是它


def shared_after_other_add() -> list[int]:
    """a 加了一个数，然后看 b 的 history。

    第一行先把类属性清空。不清空的话，这个函数第一次调用返回 [1]，第三次返回 [1, 1, 1]：
    类属性和类活得一样久，上一次调用里那些对象早就没了，它们 append 进去的数还在。
    （写这门课的测试时真的踩到了，见讲解第 4 节。）
    """
    Shared.history = []
    a, b = Shared(), Shared()
    a.add(1)
    return b.history


class Counter:
    """整数写在类里：+= 会在对象上新建一个同名属性，所以「看起来」没有共享。"""

    count = 0

    def bump(self) -> None:
        self.count += 1              # 等价于 self.count = self.count + 1


def counter_after_one_bump() -> tuple[int, int, int]:
    """c1 调一次 bump，返回 (c1.count, c2.count, Counter.count)。"""
    c1, c2 = Counter(), Counter()
    c1.bump()
    return c1.count, c2.count, Counter.count


class Typo:
    """⚠️ 方法里把属性名拼错：Python 不报错，mypy 也不报错。"""

    def __init__(self) -> None:
        self.attempts = 0

    def bump(self) -> None:
        self.atempts = self.attempts + 1     # 少了一个 t，新建了一个属性


def typo_after_bump() -> int:
    t = Typo()
    t.bump()
    return t.attempts


@dataclass(slots=True)
class Slotted:
    """slots=True：对象只能有声明过的属性。拼错的名字在运行时就会报错。"""

    attempts: int = 0

    def bump(self) -> None:
        self.atempts = self.attempts + 1  # type: ignore[misc]  # mypy 在这里能抓到


def slotted_after_bump() -> int:
    s = Slotted()
    s.bump()
    return s.attempts


@dataclass
class Settings:
    """dataclass 里的可变默认值要用 default_factory。"""

    players: list[str] = field(default_factory=list)


class Base:
    def __init__(self, target: int) -> None:
        self.target = target
        self.history: list[int] = []

    def guess(self, n: int) -> str:
        self.history.append(n)
        return "记下了"


class NoSuper(Base):
    """⚠️ 重写了 __init__，却没调用父类的 __init__。"""

    def __init__(self, target: int, hint: bool) -> None:
        self.hint = hint


class WithSuper(Base):
    def __init__(self, target: int, hint: bool) -> None:
        super().__init__(target)
        self.hint = hint


# ============================================================================
# 三、演示
# ============================================================================


def show(label: str, fn: Callable[[], object]) -> None:
    try:
        result = repr(fn())
    except Exception as e:  # noqa: BLE001 —— 演示用，要把各种异常都打印出来
        result = f"{type(e).__name__}: {e}"
    print(f"   {label:<40} → {result}")


def section(title: str) -> None:
    print("=" * 72)
    print(title)


def main() -> None:
    game = GuessGame(42)

    section("1. self 就是第一个参数")
    show("game.guess(50)", lambda: game.guess(50))
    show("GuessGame.guess(game, 30)", lambda: GuessGame.guess(game, 30))
    show("game.history", lambda: game.history)
    show("type(game.guess).__name__", lambda: type(game.guess).__name__)
    show("type(GuessGame.guess).__name__", lambda: type(GuessGame.guess).__name__)
    show("GuessGame.guess(50)", lambda: GuessGame.guess(50))  # type: ignore[call-arg, arg-type]

    section("2. 属性与 property")
    show("game.remaining", lambda: game.remaining)
    show("game", lambda: game)
    show("vars(game)", lambda: vars(game))

    section("3. 写在类里的属性")
    show("Shared：a.add(1) 之后 b.history", shared_after_other_add)
    show("Counter：(c1.count, c2.count, 类的)", counter_after_one_bump)

    section("4. 拼错属性名")
    show("Typo：bump 之后 attempts", typo_after_bump)
    show("Slotted：bump 之后 attempts", slotted_after_bump)

    section("5. 相等、打印、哈希")
    show("Plain(1, 2) == Plain(1, 2)", lambda: Plain(1, 2) == Plain(1, 2))
    show("Point(1, 2) == Point(1, 2)", lambda: Point(1, 2) == Point(1, 2))
    show("Plain(1, 2)", lambda: Plain(1, 2))
    show("Point(1, 2)", lambda: Point(1, 2))
    show("len({Plain(1, 2), Plain(1, 2)})", lambda: len({Plain(1, 2), Plain(1, 2)}))
    show("{Point(1, 2)}", lambda: {Point(1, 2)})
    show("len({FrozenPoint(1, 2), FrozenPoint(1, 2)})",
         lambda: len({FrozenPoint(1, 2), FrozenPoint(1, 2)}))
    show("Point('1', '2')", lambda: Point("1", "2"))  # type: ignore[arg-type]

    section("6. 继承")
    show("NoSuper(42, True).hint", lambda: NoSuper(42, True).hint)
    show("NoSuper(42, True).guess(1)", lambda: NoSuper(42, True).guess(1))
    show("WithSuper(42, True).guess(1)", lambda: WithSuper(42, True).guess(1))
    show("[c.__name__ for c in WithSuper.__mro__]",
         lambda: [c.__name__ for c in WithSuper.__mro__])

    section("7. 游戏结束后再猜")
    over = GuessGame(42)
    over.guess(42)
    show("over.guess(1)", lambda: over.guess(1))


if __name__ == "__main__":
    if sys.argv[1:] == ["play"]:
        play(GuessGame.with_random_target())
    else:
        main()
