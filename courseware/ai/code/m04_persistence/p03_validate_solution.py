"""第 3 题 · 参考答案。"""

from __future__ import annotations

import json
from pathlib import Path

Record = dict[str, object]
FIELDS = ("player", "target", "history", "won")
LOW, HIGH = 1, 100


class SaveFormatError(ValueError):
    """存档内容不合法。继承 ValueError，老代码的 except ValueError 照样接得住。"""


def is_int(value: object) -> bool:
    """真正的整数。bool 是 int 的子类，isinstance(True, int) 是 True，必须排除。"""
    return type(value) is int


def is_game_id(key: object) -> bool:
    """局号只认 "1"、"2"、"10" 这种写法。"01"、" 1"、"１" 都能被 int() 转成 1，要拒绝。"""
    return (isinstance(key, str) and key.isascii() and key.isdecimal()
            and key == str(int(key)) and int(key) >= 1)


def parse_games(raw: object) -> dict[int, Record]:
    if not isinstance(raw, dict):
        raise SaveFormatError(f"存档最外层必须是对象，实际是 {type(raw).__name__}")
    games: dict[int, Record] = {}
    for key, record in raw.items():
        if not is_game_id(key):
            raise SaveFormatError(f"局号 {key!r} 不合法：必须是 1、2、3 这样的正整数")
        games[int(key)] = parse_record(key, record)
    return games


def parse_record(key: str, record: object) -> Record:
    where = f"第 {key} 局"
    if not isinstance(record, dict):
        raise SaveFormatError(f"{where}：记录必须是对象，实际是 {type(record).__name__}")
    missing = [name for name in FIELDS if name not in record]
    if missing:
        raise SaveFormatError(f"{where}：缺少字段 {', '.join(missing)}")
    extra = sorted(set(record) - set(FIELDS))
    if extra:
        # 多出来的字段多半是拼错了（histroy），悄悄忽略的话，真正的 history 就成了「缺失」
        raise SaveFormatError(f"{where}：有不认识的字段 {', '.join(extra)}")

    player = record["player"]
    if not isinstance(player, str) or not player.strip():
        raise SaveFormatError(f"{where} 的 player：必须是非空字符串，实际是 {player!r}")

    target = record["target"]
    if not (is_int(target) and LOW <= target <= HIGH):
        raise SaveFormatError(f"{where} 的 target：必须是 {LOW}-{HIGH} 的整数，实际是 {target!r}")

    history = record["history"]
    if not isinstance(history, list):
        raise SaveFormatError(f"{where} 的 history：必须是列表，实际是 {history!r}")
    for i, n in enumerate(history):
        if not (is_int(n) and LOW <= n <= HIGH):
            raise SaveFormatError(
                f"{where} 的 history[{i}]：必须是 {LOW}-{HIGH} 的整数，实际是 {n!r}")

    won = record["won"]
    if type(won) is not bool:
        raise SaveFormatError(f"{where} 的 won：必须是 true 或 false，实际是 {won!r}")
    # 类型都对了，还要看几个字段之间对不对得上
    if won != (bool(history) and history[-1] == target):
        raise SaveFormatError(f"{where} 的 won：写的是 {won}，但 history 和 target 说明不是这样")

    return {"player": player, "target": target, "history": list(history), "won": won}


def load_games(path: str | Path) -> dict[int, Record]:
    path = Path(path)
    if not path.exists():
        return {}
    with open(path, encoding="utf-8-sig") as f:
        text = f.read()
    try:                                   # try 只包住会抛 JSONDecodeError 的这一行
        raw = json.loads(text)
    except json.JSONDecodeError as e:
        raise SaveFormatError(f"{path.name} 不是合法的 JSON：{e}") from e
    return parse_games(raw)
