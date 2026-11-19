"""第 5 题 · 该返回空值还是抛异常。

把四个函数的 raise NotImplementedError 换成你的实现，然后：

    pytest tests/test_m04.py -k p05 -v
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from m04_persistence.p03_validate_solution import (  # noqa: F401
    Record,
    SaveFormatError,
    is_game_id,
    parse_record,
)


@dataclass(frozen=True)
class LoadResult:
    """一次读存档的完整结果。调用方靠它区分「没有存档」「存档完好」「有几局坏了」。"""

    games: dict[int, Record] = field(default_factory=dict)
    skipped: dict[str, str] = field(default_factory=dict)   # 局号 → 为什么跳过
    found: bool = False                                     # 存档文件是否存在


def load_save(path: str | Path) -> LoadResult:
    """读存档。

    文件不存在          → LoadResult(found=False)
    整个文件坏了        → 抛 SaveFormatError（JSON 语法错误、最外层不是对象）
    有几局坏了          → 跳过，原因记进 skipped
    其他读不了的情况    → 不要处理，让异常原样抛出
    """
    raise NotImplementedError("请完成要求 1")


def describe(result: LoadResult) -> str:
    """给玩家看的一句话。五种情况各不相同，见题目。"""
    raise NotImplementedError("请完成要求 2")


def best_attempts(result: LoadResult, player: str) -> int | None:
    """这个玩家赢的那些局里，最少用了几次。没赢过（包括没玩过）返回 None。"""
    raise NotImplementedError("请完成要求 3")


def leaderboard(result: LoadResult) -> list[tuple[str, int | None]]:
    """每个玩家一行 (名字, 最好成绩)。成绩好的在前；没赢过的排在最后；成绩相同按名字排。"""
    raise NotImplementedError("请完成要求 4")
