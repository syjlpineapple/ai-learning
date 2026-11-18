"""第 1.3 章 · 参考答案。"""

import sys


def looks_like_int(raw: str) -> bool:
    body = raw.strip()
    if body and body[0] in "+-":
        body = body[1:]
    return body != "" and body.isdecimal()


def check_num(guess: int, target: int) -> str:
    if guess == target:
        return "正确"
    elif guess < target:
        return "小了"
    else:
        return "大了"


# ============================================================================
# 练习 1 · break 和 continue
# ============================================================================


def sum_until_zero(numbers: list[int]) -> int:
    """continue 跳过本轮，break 结束整个循环。

    total 必须在循环外面初始化。写在循环里面的话，每一轮都会被重置成 0 ——
    这是循环里最常见的错误之一。

    判断顺序也有讲究：先判断 0（要停下），再判断负数（要跳过）。
    这道题里两个条件互斥，顺序不影响结果；但养成「先处理会结束循环的条件」
    的习惯，能避免以后条件有重叠时出错。
    """
    total = 0
    for n in numbers:
        if n == 0:
            break
        if n < 0:
            continue
        total += n
    return total


# ============================================================================
# 练习 2 · 完整的一局游戏
# ============================================================================


def play(inputs: list[str], target: int, max_attempts: int = 5) -> str:
    """每一种结局都直接 return。

    为什么用 return 而不是 break：
      这个函数的任务是「给出本局的结局」。一旦知道了结局（猜中、退出、次数用完），
      函数的任务就完成了，直接 return 结果最清楚。

      如果用 break，就得在循环外面再判断一次「刚才是因为什么 break 的」，
      还要额外维护一个变量来记录 —— 等于把同一个判断写了两遍。

    规律：在函数里，「结束循环并给出结果」用 return；
          「结束循环但还有后续工作要做」用 break。
    """
    attempts = 0
    for raw in inputs:
        if raw.strip().lower() in ("q", "quit"):
            return "主动退出"

        if not looks_like_int(raw):
            continue

        attempts += 1
        if check_num(int(raw), target) == "正确":
            return f"猜中了，用了 {attempts} 次"
        if attempts >= max_attempts:
            return "次数用完"

    return "输入结束"


# 注意「次数用完」的判断放在「猜中」之后。
# 如果顺序反过来，最后一次机会猜中时会先被判成「次数用完」——
# 这是一个典型的边界 bug：只在「正好最后一次猜中」时才会出现，平时很难测到。
# 测试里专门有一条用例覆盖它：play(["1", "42"], 42, 2) 必须是猜中。


# ============================================================================
# 练习 3 · 找出 exit() 的问题
# ============================================================================


def play_buggy(inputs: list[str], target: int) -> str:
    """原题，保留作对照。"""
    for raw in inputs:
        if looks_like_int(raw) and check_num(int(raw), target) == "正确":
            print("猜中了")
            sys.exit()
    return "输入结束"


def play_fixed(inputs: list[str], target: int) -> str:
    """把 sys.exit() 换成 return。

    函数只负责「判断结局」，要不要结束整个程序是调用方的事。
    一个库函数擅自 sys.exit()，等于替调用方做了决定，而且是最粗暴的那种。
    """
    for raw in inputs:
        if looks_like_int(raw) and check_num(int(raw), target) == "正确":
            return "猜中了"
    return "输入结束"


EXERCISE_3_ANSWER = """
(1) 在终端里运行 play_buggy 并猜中，程序的退出码是多少？从退出码能看出「少做了事」吗？

    答：退出码是 0，和正常结束完全一样。

    sys.exit() 不传参数时，SystemExit 的 code 是 None，解释器把它当成 0 处理。
    所以从外面看（比如脚本、CI、调用它的另一个程序），这次运行是「成功」的。
    循环后面那些本该执行的代码（保存成绩、打印统计）被跳过了，没有任何信号。

    这就是 exit() 最危险的地方：它不报错。

(2) 调用方用 try / except Exception 包住，猜中时能接住吗？

    答：接不住。

    sys.exit() 的本质是 raise SystemExit。而 SystemExit 继承的是 BaseException，
    不是 Exception：

        SystemExit.__mro__ == (SystemExit, BaseException, object)

    except Exception 只接 Exception 的子类，所以 SystemExit 会穿过去，
    程序照样退出，"出错了" 不会打印。

    这是 Python 故意的设计：让「我要退出」不会被一个宽泛的 except 意外拦住。
    同样继承 BaseException 的还有 KeyboardInterrupt（Ctrl+C）。

    推论：一个函数里藏着 sys.exit()，调用方几乎没有办法优雅地处理它。

(3) 在函数里想「提前结束并给出结果」，用哪个？

    答：用 return。

    break    → 只结束循环，函数还会继续往下执行
    return   → 结束函数，把结果交给调用方，由调用方决定下一步  ← 这里要的是这个
    sys.exit → 结束整个程序，调用方没有任何机会处理

    sys.exit() 只该出现在程序的入口（main 函数或 if __name__ == "__main__" 下面），
    用来把一个退出码交给操作系统。
"""


# 补充：exit() 和 sys.exit() 的区别
#
# 讲解里用的是 sys.exit()，不是直接写 exit()。原因是：
#
#   - exit 是 site 模块在启动时塞进内置命名空间的「交互环境便利工具」，
#     类型是 _sitebuiltins.Quitter。
#   - 用 python -S 启动（不加载 site）时，exit 根本不存在，会报 NameError。
#   - sys.exit 是标准库函数，任何情况下都在。
#
# 官方文档的原话大意是：exit() / quit() 用于交互式解释器，程序里应该用 sys.exit()。
