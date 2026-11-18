"""异常类型。放在单独的模块里，规则层和交互层都能导入，而不必互相导入。"""


class GuessError(ValueError):
    """猜测输入不合法。"""


class GuessFormatError(GuessError):
    """输入不是整数。"""


class GuessRangeError(GuessError):
    """数字超出范围。"""


class GameOverError(Exception):
    """游戏已经结束，不能再猜。"""
