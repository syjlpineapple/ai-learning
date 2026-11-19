"""第 2 题 · JSON 存档。

把三个函数的 raise NotImplementedError 换成你的实现，然后：

    pytest tests/test_m04.py -k p02 -v

存档文件长这样（人要能直接打开看）：

    {
      "1": {
        "player": "张三",
        "target": 42,
        "history": [50, 25, 42],
        "won": true
      }
    }
"""

from __future__ import annotations

from pathlib import Path

from m03_structure.guess.rules import GuessGame

# 一局的记录：{"player": str, "target": int, "history": list[int], "won": bool}
Record = dict[str, object]


def save_games(path: str | Path, games: dict[int, Record]) -> None:
    """把 {局号: 记录} 写成 JSON，覆盖原文件。"""
    raise NotImplementedError("请完成要求 1")


def load_games(path: str | Path) -> dict[int, Record]:
    """读回 {局号: 记录}。局号必须是 int。文件不存在返回 {}。"""
    raise NotImplementedError("请完成要求 2")


def add_game(path: str | Path, player: str, game: GuessGame) -> int:
    """把一局游戏追加进存档，返回分配给它的局号：已有最大局号 + 1，存档为空时是 1。"""
    raise NotImplementedError("请完成要求 3")
