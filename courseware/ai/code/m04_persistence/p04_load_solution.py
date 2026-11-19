"""第 4 题 · 参考答案（业务模块）。只记录日志，不配置日志。"""

from __future__ import annotations

import json
import logging
from pathlib import Path

from m04_persistence.p03_validate_solution import (
    Record,
    SaveFormatError,
    is_game_id,
    parse_record,
)

# 名字就是模块的完整路径 m04_persistence.p04_load_solution。
# 入口可以按这个层级单独调某个包、某个模块的级别（Day13）
logger = logging.getLogger(__name__)


def load_games_lenient(path: str | Path) -> dict[int, Record]:
    path = Path(path)
    if not path.exists():
        logger.info("存档 %s 不存在，从空存档开始", path.name)
        return {}

    with open(path, encoding="utf-8-sig") as f:
        text = f.read()
    try:
        raw = json.loads(text)
    except json.JSONDecodeError as e:
        # 整个文件都读不了，没法「跳过一部分」，只能交给调用方。
        # 这里不记日志：调用方接住以后会记，这里再记一遍就成了两条
        raise SaveFormatError(f"{path.name} 不是合法的 JSON：{e}") from e
    if not isinstance(raw, dict):
        raise SaveFormatError(f"存档最外层必须是对象，实际是 {type(raw).__name__}")

    games: dict[int, Record] = {}
    skipped = 0
    for key, record in raw.items():
        if not is_game_id(key):
            logger.warning("跳过局号 %r：必须是 1、2、3 这样的正整数", key)
            skipped += 1
            continue
        try:
            games[int(key)] = parse_record(key, record)
        except SaveFormatError as e:
            # 参数交给 logging，不要先用 f-string 拼好：
            # 级别被过滤掉时它不会去格式化；参数个数写错也只会报一条 Logging error，不会让程序崩
            logger.warning("跳过第 %s 局：%s", key, e)
            skipped += 1

    logger.info("读取 %s：%d 局，跳过 %d 局", path.name, len(games), skipped)
    return games
