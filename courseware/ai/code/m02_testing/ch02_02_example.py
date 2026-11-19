"""第 2.2 章 · 讲解里的可运行示例。

    python -m m02_testing.ch02_02_example          # 看演示输出
    python -m m02_testing.ch02_02_example play     # 玩第十版猜数字（自定义异常）
"""

import json
import random
import subprocess
import sys
from collections.abc import Callable

import requests

LOW, HIGH = 1, 100
MAX_ATTEMPTS = 7


def run_snippet(code: str) -> str:
    """在干净的子进程里跑一段代码，返回完整输出（含 traceback）。"""
    done = subprocess.run(
        [sys.executable, "-c", code], capture_output=True, text=True, encoding="utf-8"
    )
    return (done.stdout + done.stderr).strip()


def mro_names(cls: type) -> str:
    return " → ".join(c.__name__ for c in cls.__mro__)


def demo_hierarchy() -> None:
    print("=" * 70)
    print("1. 继承链（__mro__）")
    for cls in (FileNotFoundError, KeyError, UnicodeDecodeError, json.JSONDecodeError,
                requests.exceptions.JSONDecodeError):
        print(f"   {cls.__module__}.{cls.__qualname__}")
        print(f"      {mro_names(cls)}")
    print("   ↑ 最后一个：requests 的 JSONDecodeError 同时是 RequestException 和 ValueError")


def demo_raise_class() -> None:
    print("=" * 70)
    print("2. raise 一个类而不是实例")
    print("   " + run_snippet("import json\nraise json.JSONDecodeError").splitlines()[-1])
    print("   ↑ 想抛 JSONDecodeError，结果抛出来的是 TypeError —— 原始意图丢了")


def parse_response_buggy(text: str) -> str:
    """✗ except 顺序写反：ValueError 分支是死代码。"""
    try:
        raise requests.exceptions.JSONDecodeError("Expecting value", text, 0)
    except requests.exceptions.RequestException:
        return "请求失败"
    except ValueError:
        return "响应格式不对"


def parse_response_fixed(text: str) -> str:
    """✓ 具体的在前，宽泛的在后。"""
    try:
        raise requests.exceptions.JSONDecodeError("Expecting value", text, 0)
    except ValueError:
        return "响应格式不对"
    except requests.exceptions.RequestException:
        return "请求失败"


def demo_except_order() -> None:
    print("=" * 70)
    print("3. except 顺序写反，后面的分支永远进不去")
    print(f"   顺序写反 → {parse_response_buggy('<html>')!r}   ← 明明是响应格式不对")
    print(f"   顺序改对 → {parse_response_fixed('<html>')!r}")


def demo_chaining() -> None:
    print("=" * 70)
    print("4. 三种异常链")
    for title, form in (("不写 from", ""), ("from e", " from e"), ("from None", " from None")):
        code = ("try:\n    int('abc')\nexcept ValueError as e:\n"
                f"    raise RuntimeError('解析配置失败'){form}")
        out = run_snippet(code)
        links = [line for line in out.splitlines()
                 if line.startswith(("During handling", "The above exception"))]
        print(f"   {title:<10} 显示原始 ValueError: {'ValueError: invalid' in out!s:<5}"
              f"  连接句: {links[0] if links else '（无）'}")


def demo_reraise() -> None:
    print("=" * 70)
    print("5. 裸 raise 和 raise e 的 traceback")
    base = "def inner():\n    int('abc')\ndef outer():\n    try:\n        inner()\n"
    bare = run_snippet(base + "    except ValueError:\n        raise\nouter()")
    named = run_snippet(base + "    except ValueError as e:\n        raise e\nouter()")
    print(f"   裸 raise  的 traceback 有 {bare.count('File ')} 层，包含原始出错行: "
          f"{'line 2, in inner' in bare}")
    print(f"   raise e   的 traceback 有 {named.count('File ')} 层，包含原始出错行: "
          f"{'line 2, in inner' in named}")
    print("   ↑ raise e 多了一层「raise e 这一行」，原始信息并没有丢")


def parse_wrong(raw: str) -> int:
    """✗ 自己 raise 的异常被同一个 try 接住了。"""
    try:
        n = int(raw)
        if not LOW <= n <= HIGH:
            raise ValueError(f"数字必须在 {LOW}~{HIGH}")
        return n
    except ValueError:
        raise ValueError("输入格式错误") from None


def demo_catch_own_raise() -> None:
    print("=" * 70)
    print("6. 捕获了自己准备抛出的异常")
    for raw in ("abc", "101"):
        try:
            parse_wrong(raw)
        except ValueError as e:
            print(f"   parse_wrong({raw!r}) → {e}")
    print("   ↑ 101 的格式完全正确，提示却说「格式错误」")


def never_raises(raw: str) -> int:
    return 0


def demo_fake_test() -> None:
    print("=" * 70)
    print("7. 手写「测异常」时漏了 else")
    try:  # noqa: SIM105  故意写成 try / except / pass，演示漏了 else 的假测试
        never_raises("abc")
    except ValueError:
        pass
    print("   没写 else：上面这段静默结束了 —— 测试「通过」，但被测函数根本没抛异常")
    try:
        try:
            never_raises("abc")
        except ValueError:
            pass
        else:
            raise AssertionError("预期出现 ValueError")
    except AssertionError as e:
        print(f"   写了 else：AssertionError: {e}")


# ============================================================================
# 第十版猜数字：自定义异常
# ============================================================================


class GuessError(ValueError):
    """猜测输入不合法。继承 ValueError：老代码写的 except ValueError 照样能接住。"""


class GuessFormatError(GuessError):
    """输入不是整数。"""


class GuessRangeError(GuessError):
    """数字超出范围。"""

    def __init__(self, value: int, low: int, high: int) -> None:
        super().__init__(f"{value} 不在 {low}-{high} 之间")
        self.value = value
        self.low = low
        self.high = high


def parse_guess(raw: str, low: int = LOW, high: int = HIGH) -> int:
    """解析并校验。不打印、不处理 —— 发现问题就抛，由调用方决定怎么办。"""
    try:
        n = int(raw)
    except ValueError:
        raise GuessFormatError(f"{raw!r} 不是整数") from None

    if not low <= n <= high:
        raise GuessRangeError(n, low, high)
    return n


def check_num(guess: int, target: int) -> str:
    if guess == target:
        return "正确"
    if guess < target:
        return "小了"
    return "大了"


def play(
    target: int,
    max_attempts: int = MAX_ATTEMPTS,
    ask: Callable[[str], str] = input,
    say: Callable[[str], None] = print,
) -> list[int]:
    history: list[int] = []
    while len(history) < max_attempts:
        raw = ask(f"[{len(history) + 1}/{max_attempts}] 你猜： ")
        if raw.strip().lower() in ("q", "quit"):
            break
        try:
            guess = parse_guess(raw)
        except GuessError as e:
            say(f"   {e}，这次不算")
            continue
        history.append(guess)
        result = check_num(guess, target)
        say(f"   {guess:>3} → {result}")
        if result == "正确":
            break
    return history


def main() -> None:
    if len(sys.argv) > 1 and sys.argv[1] == "play":
        target = random.Random().randint(LOW, HIGH)
        history = play(target)
        print(f"共猜了 {len(history)} 次，答案是 {target}")
        return

    demo_hierarchy()
    demo_raise_class()
    demo_except_order()
    demo_chaining()
    demo_reraise()
    demo_catch_own_raise()
    demo_fake_test()
    print("=" * 70)
    print("想玩第十版：python -m m02_testing.ch02_02_example play")


if __name__ == "__main__":
    main()
