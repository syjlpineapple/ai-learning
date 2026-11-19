"""第 13 题 · 参考答案。

    python -m m05_http.server                              （另一个终端，开着）
    python -m m07_client.p13_main_solution scores
    python -m m07_client.p13_main_solution upload 张三 3
"""

from __future__ import annotations

import logging
import os
import sys
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path
from typing import Any

import requests

from m05_http.p07_classify_solution import classify
from m06_config.p10_settings_solution import ConfigError, Settings
from m06_config.p11_layers_solution import load_for
from m07_client.p12_client_solution import APIClient

CONFIG_DIR = Path(__file__).resolve().parent / "config"
USAGE = "用法：scores [玩家]  |  upload 玩家 次数"

OK, BUG, BAD_INPUT, NETWORK = 0, 1, 2, 3

logger = logging.getLogger(__name__)


def format_scores(rows: list[dict[str, Any]]) -> list[str]:
    return [f"{i:>2}. {row['player']}  {row['attempts']} 次" for i, row in enumerate(rows, 1)]


def parse_args(argv: Sequence[str]) -> tuple[str, list[Any]] | None:
    """解析命令行。不合法返回 None。"""
    if len(argv) in (1, 2) and argv[0] == "scores":
        return "scores", list(argv[1:])
    if len(argv) == 3 and argv[0] == "upload":
        try:
            return "upload", [argv[1], int(argv[2])]
        except ValueError:
            return None
    return None


def main(argv: Sequence[str], environ: Mapping[str, str] = os.environ,
         config_dir: Path = CONFIG_DIR,
         client_factory: Callable[[Settings], APIClient] = APIClient) -> int:
    # 1. 先检查输入和配置：都是在发任何请求之前就能发现的问题
    command = parse_args(argv)
    if command is None:
        print(USAGE, file=sys.stderr)         # 用法说明给人看，但它不是程序的结果，放标准错误
        return BAD_INPUT
    try:
        env, settings = load_for(config_dir, environ)
    except ConfigError as e:
        logger.error("配置有问题：%s", e)      # 预料之中的错误：说清楚原因就够了，不需要 traceback
        return BAD_INPUT
    logger.info("环境 %s，服务 %s", env, settings.base_url)

    name, args = command
    try:
        # 2. with：构造成功以后不管发生什么都会 close；构造失败的话根本不会进到这里
        with client_factory(settings) as client:
            if name == "scores":
                rows = client.get_scores(*args)
                for line in format_scores(rows) or ["（还没有成绩）"]:
                    print(line)
            else:
                row = client.upload(*args)
                print(f"已上传：第 {row['id']} 条")
    except requests.exceptions.RequestException as e:
        # 3. 网络问题：重试过了还不行。告诉用户是哪一类问题，细节留在日志里
        logger.error("请求失败（%s）：%s", classify(e), e)
        return NETWORK
    except Exception:
        # 4. 最外层，唯一该接 Exception 的地方。必须记完整的 traceback：这是程序自己的 bug
        logger.exception("程序出错了")
        return BUG
    return OK


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    sys.exit(main(sys.argv[1:]))
