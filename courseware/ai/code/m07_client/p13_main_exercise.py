"""第 13 题 · 程序入口。

把 main 里的 raise NotImplementedError 换成你的实现，然后：

    pytest tests/test_m07.py -k p13 -v

做完以后可以真的跑一下（先在另一个终端里 python -m m05_http.server）：

    python -m m07_client.p13_main_exercise scores
    python -m m07_client.p13_main_exercise upload 张三 3
"""

from __future__ import annotations

import logging
import os
import sys
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path
from typing import Any

from m05_http.p07_classify_solution import classify  # noqa: F401
from m06_config.p10_settings_solution import ConfigError, Settings  # noqa: F401
from m06_config.p11_layers_solution import load_for  # noqa: F401
from m07_client.p12_client_solution import APIClient

CONFIG_DIR = Path(__file__).resolve().parent / "config"
USAGE = "用法：scores [玩家]  |  upload 玩家 次数"

# 退出码：外面的脚本、CI 靠它判断成功没有
OK, BUG, BAD_INPUT, NETWORK = 0, 1, 2, 3

logger = logging.getLogger(__name__)


def format_scores(rows: list[dict[str, Any]]) -> list[str]:
    """排行榜的每一行。已经写好了。"""
    return [f"{i:>2}. {row['player']}  {row['attempts']} 次" for i, row in enumerate(rows, 1)]


def main(argv: Sequence[str], environ: Mapping[str, str] = os.environ,
         config_dir: Path = CONFIG_DIR,
         client_factory: Callable[[Settings], APIClient] = APIClient) -> int:
    """运行一条命令，返回退出码。见题目的要求 1-5。

    environ、config_dir、client_factory 平时用默认值；测试会换掉它们。
    """
    raise NotImplementedError("请完成第 13 题")


if __name__ == "__main__":
    # 日志的配置写在这里，不写在 main 里（第 4 题：在测试里配置日志会拆掉 pytest 的 handler）
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    sys.exit(main(sys.argv[1:]))
