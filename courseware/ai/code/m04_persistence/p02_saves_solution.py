"""第 2 题 · 参考答案。"""

from __future__ import annotations

import json
import os
from pathlib import Path

from m03_structure.guess.rules import GuessGame

Record = dict[str, object]


def save_games(path: str | Path, games: dict[int, Record]) -> None:
    path = Path(path)
    # 先在内存里变成字符串。里面有存不了的东西（比如 set）时，在这一步就报错，文件还没动
    text = json.dumps(games, ensure_ascii=False, indent=2)
    tmp = path.with_name(path.name + ".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(text)
    os.replace(tmp, path)


def load_games(path: str | Path) -> dict[int, Record]:
    path = Path(path)
    if not path.exists():
        return {}
    # utf-8-sig：文件开头有 BOM 就跳过它，没有也照常读
    with open(path, encoding="utf-8-sig") as f:
        raw = json.load(f)
    # JSON 对象的键只能是字符串，存进去的 1 读回来是 "1"
    return {int(key): record for key, record in raw.items()}


def add_game(path: str | Path, player: str, game: GuessGame) -> int:
    games = load_games(path)
    game_id = max(games, default=0) + 1
    games[game_id] = {
        "player": player,
        "target": game.target,
        "history": list(game.history),
        "won": game.won,
    }
    save_games(path, games)
    return game_id
