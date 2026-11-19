"""第 3.2 章 · 参考答案。"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from m03_structure.ch03_02_example import GuessGame

# ============================================================================
# 练习 1
# ============================================================================

PREDICTIONS: dict[str, str | None] = {
    # 类.方法(对象, 参数) 和 对象.方法(参数) 是同一回事
    "GuessGame.guess(GuessGame(42), 50)": "'大了'",
    # property 像属性一样读，不加括号
    "GuessGame(42).remaining": "7",
    # 没写 __eq__：== 退回到 is，两个新对象当然不是同一个
    "Plain(1, 2) == Plain(1, 2)": "False",
    # dataclass 生成的 __eq__ 按字段比较
    "Point(1, 2) == Point(1, 2)": "True",
    "repr(Point(1, 2))": "'Point(x=1, y=2)'",
    # 普通类按 id 哈希：两个对象，两个元素
    "len({Plain(1, 2), Plain(1, 2)})": "2",
    # dataclass 定义了 __eq__ 又不是 frozen，__hash__ 被设成 None
    "{Point(1, 2)}": "TypeError",
    "len({FrozenPoint(1, 2), FrozenPoint(1, 2)})": "1",
    # 类型注解不做运行时检查（第 1.6 章）
    "Point('1', '2').x": "'1'",
    # history 是类属性，a 和 b 读到的是同一个列表
    "shared_after_other_add()": "[1]",
    # += 在 c1 上新建了 count；c2 和类本身都还是 0
    "counter_after_one_bump()": "(1, 0, 0)",
    # 拼错的 atempts 是一个新属性，attempts 没变
    "typo_after_bump()": "0",
    # slots 不允许新建属性
    "slotted_after_bump()": "AttributeError",
    "NoSuper(42, True).hint": "True",
    # 父类的 __init__ 没执行，history 从来没被创建
    "NoSuper(42, True).guess(1)": "AttributeError",
    "isinstance(WithSuper(42, True), Base)": "True",
}


# ============================================================================
# 练习 2
# ============================================================================


class Scoreboard:
    def __init__(self) -> None:
        # 列表必须在 __init__ 里创建。写成类属性 _rounds = [] 的话，所有记分板共用一个
        self._rounds: list[tuple[str, int, bool]] = []

    def add(self, player: str, attempts: int, won: bool) -> None:
        self._rounds.append((player, attempts, won))

    def best(self, player: str) -> int | None:
        wins = [attempts for name, attempts, won in self._rounds if name == player and won]
        return min(wins) if wins else None      # min([]) 会抛 ValueError（第 1.9 章）

    @property
    def players(self) -> list[str]:
        return sorted({name for name, _, _ in self._rounds})

    def __len__(self) -> int:
        return len(self._rounds)


# ============================================================================
# 练习 3
# ============================================================================


class HintGame(GuessGame):
    def __init__(self, target: int, max_attempts: int = 7, low: int = 1, high: int = 100,
                 hint_after: int = 3) -> None:
        super().__init__(target, max_attempts, low, high)
        self.hint_after = hint_after
        self.hint_low = low
        self.hint_high = high

    def guess(self, n: int) -> str:
        # 猜对就结束了，所以能走到这里时，之前猜过的每一次都是猜错
        wrong_before = len(self.history)
        result = super().guess(n)        # 记录、次数、GameOverError 都在这里
        if result == "小了":
            self.hint_low = max(self.hint_low, n + 1)
        elif result == "大了":
            self.hint_high = min(self.hint_high, n - 1)
        if result != "正确" and wrong_before >= self.hint_after:
            return f"{result}（提示：答案在 {self.hint_low}-{self.hint_high} 之间）"
        return result


# ============================================================================
# 练习 4
# ============================================================================


@dataclass(frozen=True)
class GameRecord:
    player: str
    attempts: int
    won: bool


def top(records: Iterable[GameRecord], n: int = 3) -> list[GameRecord]:
    winners = {r for r in records if r.won}            # frozen 才能放进集合
    return sorted(winners, key=lambda r: (r.attempts, r.player))[:n]
