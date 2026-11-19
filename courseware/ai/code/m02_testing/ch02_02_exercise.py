"""第 2.2 章 · 练习。

    pytest tests/test_m02.py -k ch02_02 -v
"""

from collections.abc import Callable

# ============================================================================
# 练习 1（基础）· 先猜继承关系
#
# 填 "True" 或 "False"。做之前先看示例第 1 节和讲解里的异常层次图。
# ============================================================================

PREDICTIONS: dict[str, str | None] = {
    "issubclass(FileNotFoundError, OSError)": None,
    "issubclass(KeyError, LookupError)": None,
    "issubclass(IndexError, KeyError)": None,
    "issubclass(KeyboardInterrupt, Exception)": None,
    "issubclass(SystemExit, BaseException)": None,
    "issubclass(UnicodeDecodeError, ValueError)": None,
    "issubclass(ZeroDivisionError, ArithmeticError)": None,
    "issubclass(TimeoutError, OSError)": None,
    "issubclass(ModuleNotFoundError, ImportError)": None,
    "issubclass(bool, int)": None,
    "issubclass(ValueError, TypeError)": None,
}


# ============================================================================
# 练习 2（基础）· 自定义异常
#
# 1. 定义三个异常类：
#        GuessError        继承 ValueError
#        GuessFormatError  继承 GuessError
#        GuessRangeError   继承 GuessError
#    只需要 class 那一行加一个文档字符串，不用写别的。
#
# 2. 写 parse_guess(raw, low, high)：
#        raw 不是整数         → 抛 GuessFormatError，消息里包含 raw 的原文
#                               并且隐藏 int() 原来那个 ValueError（from None）
#        数字不在 [low, high] → 抛 GuessRangeError，消息里包含这个数字
#        都正常               → 返回整数
#
#    要求：try 只包住 int(raw) 这一行。范围检查放在 try 外面
#    —— 否则你自己 raise 的 GuessRangeError 会被 except ValueError 接住（讲解第 5 节）。
#
# 把下面三个占位类和占位函数整个替换掉。
# ============================================================================


class GuessError(Exception):
    """TODO 练习 2：改成继承 ValueError。"""


class GuessFormatError(Exception):
    """TODO 练习 2：改成继承 GuessError。"""


class GuessRangeError(Exception):
    """TODO 练习 2：改成继承 GuessError。"""


def parse_guess(raw: str, low: int = 1, high: int = 100) -> int:
    # TODO 练习 2
    raise NotImplementedError("请完成练习 2")


# ============================================================================
# 练习 3（基础）· 修好 except 的顺序
#
# 下面这个函数调用 action()，按异常类型返回一句描述。它有一个分支永远进不去。
#
#     describe_failure_buggy(lambda: open("不存在.txt"))   → "其他 IO 错误"   ✗
#
# 1. 先说出哪个分支是死代码、为什么
# 2. 写 describe_failure，让四种情况都返回正确的描述：
#        FileNotFoundError        → "文件不存在"
#        其他 OSError             → "其他 IO 错误"
#        ValueError               → "格式错误"
#        没有异常                 → "成功"
#    其他类型的异常不要捕获，让它抛出去。
# ============================================================================


def describe_failure_buggy(action: Callable[[], object]) -> str:
    """保留原样，不要改。"""
    try:
        action()
    except OSError:
        return "其他 IO 错误"
    except FileNotFoundError:
        return "文件不存在"
    except ValueError:
        return "格式错误"
    return "成功"


def describe_failure(action: Callable[[], object]) -> str:
    # TODO 练习 3
    raise NotImplementedError("请完成练习 3")


# ============================================================================
# 练习 4（进阶）· 手写一个 pytest.raises
#
# 写 expect_raises(exc_type, fn, *args)：调用 fn(*args)，
#     抛出了 exc_type（或它的子类）  → 返回那个异常对象
#     没有抛异常                     → 抛 AssertionError，消息里写明「预期 xxx 但没有抛出」
#     抛出了别的类型的异常           → 不要接住，让它原样抛出去
#
# 用法：
#     err = expect_raises(GuessRangeError, parse_guess, "101")
#     assert err.args ...
#
# 这就是下一章 pytest.raises 在做的事。手写一遍，下一章用它时就不是咒语了。
#
# 提示：try / except exc_type as e / else 三段结构。注意 e 在 except 块结束后会被删除。
# ============================================================================


def expect_raises(
    exc_type: type[BaseException], fn: Callable[..., object], *args: object
) -> BaseException:
    # TODO 练习 4
    raise NotImplementedError("请完成练习 4")
