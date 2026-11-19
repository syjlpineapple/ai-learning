"""第 4 题 · 用日志代替 print（业务模块）。

第 3 题的 load_games 遇到一局坏记录，整个存档就读不出来了。这里写一个「宽容」的版本：
坏的局跳过并记一条 WARNING，好的照常返回。

    pytest tests/test_m04.py -k p04 -v

这个文件只负责「记录」日志，不负责「配置」日志 —— 配置写在 p04_entry_exercise.py 里。
"""

from __future__ import annotations

from pathlib import Path

# 校验规则直接用第 3 题的参考答案：
#   is_game_id(key)           局号写法对不对
#   parse_record(key, record) 一局记录合法就返回它，不合法抛 SaveFormatError（消息里有原因）
from m04_persistence.p03_validate_solution import (  # noqa: F401
    Record,
    SaveFormatError,
    is_game_id,
    parse_record,
)

# TODO 要求 1：在这里创建这个模块的 logger


def load_games_lenient(path: str | Path) -> dict[int, Record]:
    """读存档，跳过坏的局，返回好的局。"""
    raise NotImplementedError("请完成要求 2-4")
