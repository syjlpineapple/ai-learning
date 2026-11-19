"""第 4 题 · 参考答案（入口）。

    python -m m04_persistence.p04_entry_solution 存档.json [DEBUG|INFO|WARNING]

日志的配置只在这里做一次。
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

CONSOLE_FORMAT = "%(levelname)s %(name)s: %(message)s"
FILE_FORMAT = "%(asctime)s %(levelname)s %(name)s: %(message)s"


def setup_logging(level: str = "INFO", logfile: str | Path | None = None) -> None:
    console = logging.StreamHandler(sys.stderr)
    console.setFormatter(logging.Formatter(CONSOLE_FORMAT))
    handlers: list[logging.Handler] = [console]
    if logfile is not None:
        # FileHandler 也有 encoding 参数，不写的话用系统编码（中文 Windows 上是 GBK）
        file_handler = logging.FileHandler(logfile, encoding="utf-8")
        file_handler.setFormatter(logging.Formatter(FILE_FORMAT))
        handlers.append(file_handler)
    # basicConfig 默认只在第一次调用时生效，之后静默什么都不做；
    # force=True 先把根 logger 上已有的 handler 关掉、移除，再按这次的参数重新配置
    logging.basicConfig(level=level, handlers=handlers, force=True)


def main(argv: list[str]) -> int:
    from m04_persistence.p03_validate_solution import SaveFormatError
    from m04_persistence.p04_load_solution import load_games_lenient

    setup_logging(argv[1] if len(argv) > 1 else "INFO", "games.log")
    log = logging.getLogger(__name__)
    try:
        games = load_games_lenient(argv[0])
    except SaveFormatError:
        log.exception("存档读不了")        # 在 except 里用 exception，会带上完整的 traceback
        return 1
    print(f"读到 {len(games)} 局")        # 给人看的结果用 print；排查用的过程信息用日志
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
