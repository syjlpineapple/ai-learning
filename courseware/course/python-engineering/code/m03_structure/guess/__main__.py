"""入口。`python -m m03_structure.guess` 运行的就是这个文件。

入口只做组装：决定用什么参数创建对象、把它交给谁。不写规则，也不写交互细节。
它只被运行，不被任何模块导入（第 3.1 章第 7 节）。
"""

import sys

from m03_structure.guess.cli import play
from m03_structure.guess.rules import GuessGame


def main(argv: list[str]) -> None:
    seed = int(argv[0]) if argv else None      # 传一个数字当种子，方便复现某一局
    play(GuessGame.with_random_target(seed))


if __name__ == "__main__":
    main(sys.argv[1:])
