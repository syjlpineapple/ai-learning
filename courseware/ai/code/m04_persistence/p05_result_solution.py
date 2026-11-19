"""第 5 题 · 参考答案。"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from m04_persistence.p03_validate_solution import (
    Record,
    SaveFormatError,
    is_game_id,
    parse_record,
)


@dataclass(frozen=True)
class LoadResult:
    games: dict[int, Record] = field(default_factory=dict)
    skipped: dict[str, str] = field(default_factory=dict)
    found: bool = False


def load_save(path: str | Path) -> LoadResult:
    path = Path(path)
    # 直接打开，只把「文件不存在」当成正常情况。
    # 不先用 exists() 判断：路径是一个目录时 exists() 也是 True，接着 open 照样失败；
    # 也不写 except OSError：权限不够、路径是目录这些情况，不该被说成「还没有存档」
    try:
        with open(path, encoding="utf-8-sig") as f:
            text = f.read()
    except FileNotFoundError:
        return LoadResult(found=False)

    try:
        raw = json.loads(text)
    except json.JSONDecodeError as e:
        raise SaveFormatError(f"{path.name} 不是合法的 JSON：{e}") from e
    if not isinstance(raw, dict):
        raise SaveFormatError(f"存档最外层必须是对象，实际是 {type(raw).__name__}")

    games: dict[int, Record] = {}
    skipped: dict[str, str] = {}
    for key, record in raw.items():
        if not is_game_id(key):
            skipped[key] = "局号必须是 1、2、3 这样的正整数"
            continue
        try:
            games[int(key)] = parse_record(key, record)
        except SaveFormatError as e:
            skipped[key] = str(e)
    return LoadResult(games=games, skipped=skipped, found=True)


def describe(result: LoadResult) -> str:
    if not result.found:
        return "还没有存档，从第 1 局开始"
    bad = "、".join(result.skipped)
    if not result.games and not result.skipped:
        return "存档是空的"
    if not result.games:
        return f"存档里的 {len(result.skipped)} 局全都坏了（{bad}），没有读到任何一局"
    if not result.skipped:
        return f"读到 {len(result.games)} 局"
    return f"读到 {len(result.games)} 局，跳过 {len(result.skipped)} 局（{bad}）"


def best_attempts(result: LoadResult, player: str) -> int | None:
    wins: list[int] = []
    for game in result.games.values():
        history = game["history"]
        # parse_record 已经保证 history 是列表；这里的 isinstance 是写给 mypy 看的
        if game["player"] == player and game["won"] and isinstance(history, list):
            wins.append(len(history))
    return min(wins, default=None)    # 没赢过是 None，不是 0：0 次赢下来是不可能的成绩


def leaderboard(result: LoadResult) -> list[tuple[str, int | None]]:
    players = {str(g["player"]) for g in result.games.values()}
    board = [(p, best_attempts(result, p)) for p in players]
    # None 不能和 int 比大小，排序键里先按「是不是 None」分开，没赢过的排最后
    return sorted(board, key=lambda row: (row[1] is None, row[1] or 0, row[0]))
