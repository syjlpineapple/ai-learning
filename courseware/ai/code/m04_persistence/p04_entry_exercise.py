"""第 4 题 · 用日志代替 print（入口）。

日志「怎么输出」只在程序入口决定一次：级别、格式、输出到哪。业务模块里一行配置都不写。

    pytest tests/test_m04.py -k p04 -v
"""

from __future__ import annotations

from pathlib import Path

CONSOLE_FORMAT = "%(levelname)s %(name)s: %(message)s"
FILE_FORMAT = "%(asctime)s %(levelname)s %(name)s: %(message)s"


def setup_logging(level: str = "INFO", logfile: str | Path | None = None) -> None:
    """配置日志。

    要求 5：
        控制台：输出到标准错误，格式 CONSOLE_FORMAT
        logfile 不为 None 时，同时写进这个文件，格式 FILE_FORMAT，UTF-8 编码
        级别由 level 决定（"DEBUG"、"INFO"、"WARNING" ……）
        调用两次（比如换了个级别重新配置），每条日志也只出现一次
    """
    raise NotImplementedError("请完成要求 5")
