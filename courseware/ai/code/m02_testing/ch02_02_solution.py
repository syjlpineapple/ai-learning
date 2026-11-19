"""第 2.2 章 · 参考答案。"""

from collections.abc import Callable

# ============================================================================
# 练习 1 · 先猜继承关系
# ============================================================================

PREDICTIONS: dict[str, str | None] = {
    "issubclass(FileNotFoundError, OSError)": "True",
    "issubclass(KeyError, LookupError)": "True",
    # 兄弟关系，都是 LookupError 的子类，但彼此不是父子
    "issubclass(IndexError, KeyError)": "False",
    # Ctrl+C 不是「错误」，所以不在 Exception 下面 —— except Exception 接不住它
    "issubclass(KeyboardInterrupt, Exception)": "False",
    "issubclass(SystemExit, BaseException)": "True",
    # 解码失败是「值不对」：字节是 bytes 没问题，内容不是合法的编码
    "issubclass(UnicodeDecodeError, ValueError)": "True",
    "issubclass(ZeroDivisionError, ArithmeticError)": "True",
    # 超时被归为操作系统层面的错误
    "issubclass(TimeoutError, OSError)": "True",
    "issubclass(ModuleNotFoundError, ImportError)": "True",
    # 不是异常，但 issubclass 对任何类都适用 —— 第 1.2 章的老朋友
    "issubclass(bool, int)": "True",
    # 两个独立的分支
    "issubclass(ValueError, TypeError)": "False",
}


# ============================================================================
# 练习 2 · 自定义异常
# ============================================================================


class GuessError(ValueError):
    """猜测输入不合法。

    继承 ValueError 是为了向后兼容：原来写 except ValueError 的调用方，
    不用改代码就能接住新的异常。
    """


class GuessFormatError(GuessError):
    """输入不是整数。"""


class GuessRangeError(GuessError):
    """数字超出范围。"""


def parse_guess(raw: str, low: int = 1, high: int = 100) -> int:
    """try 只包 int(raw)；范围检查在 try 外面。

    from None 的作用：traceback 里不再显示 int() 原来那个
    "invalid literal for int() with base 10" —— 它对用户是噪音。
    注意 from None 只改变显示方式，异常照样抛出。

    调用方现在可以按类型分别处理：
        except GuessFormatError: ...   # 提示「请输入整数」
        except GuessRangeError: ...    # 提示「请输入 1-100」
    或者用基类一起接住：
        except GuessError as e: print(e)
    而不需要去比较消息文本。
    """
    try:
        n = int(raw)
    except ValueError:
        raise GuessFormatError(f"{raw!r} 不是整数") from None

    if not low <= n <= high:
        raise GuessRangeError(f"{n} 不在 {low}-{high} 之间")
    return n


# ============================================================================
# 练习 3 · 修好 except 的顺序
# ============================================================================


def describe_failure_buggy(action: Callable[[], object]) -> str:
    """原题，保留作对照。

    死代码是 except FileNotFoundError：FileNotFoundError 是 OSError 的子类，
    写在它前面的 except OSError 会先匹配上，后面这一支永远轮不到。
    Python 不报错，ruff 和 mypy 也都不提示（讲解第 4 节有实测）。
    """
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
    """子类在前，父类在后。

    ValueError 和 OSError 之间没有继承关系，谁先谁后都行；
    只有 FileNotFoundError 必须在 OSError 前面。

    「其他类型的异常不要捕获」：比如 action 里有个 KeyError，
    那是一个这里不知道怎么处理的问题，应该让它抛出去被看见。
    """
    try:
        action()
    except FileNotFoundError:
        return "文件不存在"
    except OSError:
        return "其他 IO 错误"
    except ValueError:
        return "格式错误"
    return "成功"


# ============================================================================
# 练习 4 · 手写一个 pytest.raises
# ============================================================================


def expect_raises(
    exc_type: type[BaseException], fn: Callable[..., object], *args: object
) -> BaseException:
    """三段结构，每一段都不能省：

    except exc_type as e: return e
        抛了预期的异常 —— 把它交给调用方，方便进一步检查消息、属性。
        必须在 except 块里 return，因为 e 在块结束后会被删除（第 1.5 章）。

    else: raise AssertionError(...)
        没有抛异常 —— 这是测试失败。少了这一段，就是讲解第 8 节那个假测试。

    不写 except Exception：
        抛了别的类型的异常，说明被测函数的行为和预期完全不同，
        应该原样暴露，而不是被当成「没有抛出预期异常」。
    """
    try:
        fn(*args)
    except exc_type as e:
        return e
    else:
        raise AssertionError(f"预期 {exc_type.__name__}，但没有抛出")
