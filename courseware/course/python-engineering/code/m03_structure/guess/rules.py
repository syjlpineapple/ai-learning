"""游戏规则。

这一层的约束（tests/test_m03.py 会检查）：
    不调用 input() 和 print()
    不导入 cli 和 __main__
它只回答「输入合不合法」「猜得对不对」「这局结束没有」，不关心问题是怎么问出来、答案怎么显示的。
"""

from __future__ import annotations

import random

from m03_structure.guess.errors import GameOverError, GuessFormatError, GuessRangeError


def parse_guess(raw: str, low: int = 1, high: int = 100) -> int:
    try:
        n = int(raw)
    except ValueError:
        raise GuessFormatError(f"{raw!r} 不是整数") from None
    if not low <= n <= high:
        raise GuessRangeError(f"{n} 不在 {low}-{high} 之间")
    return n


class GuessGame:
    """一局猜数字。和第 3.2 章的版本相同，只是换了个地方住。"""

    def __init__(self, target: int, max_attempts: int = 7, low: int = 1, high: int = 100) -> None:
        self.target = target
        self.max_attempts = max_attempts
        self.low = low
        self.high = high
        self.history: list[int] = []

    @classmethod
    def with_random_target(cls, seed: int | None = None, **options: int) -> GuessGame:
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
        return (f"GuessGame(range={self.low}-{self.high}, "
                f"attempts={len(self.history)}/{self.max_attempts}, won={self.won})")
