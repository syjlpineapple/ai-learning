"""第 1.5 章 · 讲解里的可运行示例。

    python -m m01_basics.ch01_05_example          # 看演示输出
    python -m m01_basics.ch01_05_example play     # 玩第五版猜数字（EAFP + 范围检查）
"""

import random
import sys

LOW, HIGH = 1, 100
MAX_ATTEMPTS = 7


def kind(expr: str) -> None:
    """计算表达式，打印结果或异常的类型和消息。"""
    try:
        value = eval(expr)
        print(f"   {expr:<20} → 不报错: {value!r}")
    except Exception as e:  # noqa: BLE001  演示用
        print(f"   {expr:<20} → {type(e).__name__}: {e}")


def demo_builtin_exceptions() -> None:
    print("=" * 70)
    print("1. 常见内置异常的原文")
    for e in ('int("abc")', '"a" + 1', "[1, 2][5]", '{}["k"]', "1 / 0",
              "None.upper()", "int(None)", "undefined_name"):
        kind(e)
    print("   ↑ int(\"abc\") 是 ValueError，int(None) 是 TypeError：")
    print("     类型对但值不行 → ValueError；类型本身就不对 → TypeError")


def trace(raw: str) -> list[str]:
    """记录 try / except / else / finally 四个块哪些执行了、按什么顺序。"""
    steps = []
    try:
        steps.append("try")
        int(raw)
        steps.append("try 的后半段")
    except ValueError:
        steps.append("except")
    else:
        steps.append("else")
    finally:
        steps.append("finally")
    return steps


def demo_flow() -> None:
    print("=" * 70)
    print("2. 四个块的执行顺序")
    print(f"   trace('42')  = {trace('42')}")
    print(f"   trace('abc') = {trace('abc')}")
    print("   ↑ 出错时「try 的后半段」没有执行 —— 异常一抛出，try 里剩下的代码全部跳过")


def returns_from_try() -> str:
    try:
        return "try 里的 return"
    finally:
        print("   finally 执行了（在 return 真正返回之前）")


def finally_overrides() -> int:
    try:
        return 1
    finally:
        return 2  # noqa: SIM107  故意的错误示范，ruff 会拦住它


def finally_swallows() -> str:
    try:
        raise ValueError("这个异常会消失")
    finally:
        return "finally 的 return"  # 故意的错误示范


def demo_finally() -> None:
    print("=" * 70)
    print("3. finally 一定执行，包括 return 的时候")
    print(f"   返回值：{returns_from_try()}")
    print()
    print("   ⚠️ finally 里写 return 的后果：")
    print(f"   finally_overrides() = {finally_overrides()}      ← try 里明明 return 1")
    print(f"   finally_swallows()  = {finally_swallows()!r}  ← ValueError 消失了")


def demo_bare_except() -> None:
    print("=" * 70)
    print("4. 裸 except 会接住 SystemExit 和 KeyboardInterrupt")
    try:
        sys.exit(3)
    except:  # noqa: E722  故意的错误示范
        print("   裸 except 接住了 sys.exit(3) —— 程序没有退出")
    try:
        raise KeyboardInterrupt
    except:  # noqa: E722  故意的错误示范
        print("   裸 except 接住了 KeyboardInterrupt —— Ctrl+C 失效")
    try:
        raise KeyboardInterrupt
    except Exception:
        print("   不会到这里")
    except BaseException as e:
        print(f"   except Exception 放过了 {type(e).__name__} —— 这才是想要的")


def demo_as_e_scope() -> None:
    print("=" * 70)
    print("5. except ... as e 结束后，e 会被删除")
    try:
        int("x")
    except ValueError as e:
        print(f"   块内：type={type(e).__name__}  str={str(e)!r}")
        print(f"         args={e.args!r}")
    try:
        # mypy 会直接报 "Trying to read deleted variable e" —— 它知道 e 已被删除
        print(e)  # type: ignore[misc]  # noqa: F821
    except NameError as err:
        print(f"   块外：NameError: {err}")


def looks_like_int(raw: str) -> bool:
    """第 1.2 章练习 3 的成果：LBYL 写法。"""
    body = raw.strip()
    if body and body[0] in "+-":
        body = body[1:]
    return body != "" and body.isdecimal()


def parse_int(raw: str) -> int | None:
    """EAFP 写法：直接交给 int()，失败了返回 None。"""
    try:
        return int(raw)
    except ValueError:
        return None


def demo_lbyl_vs_eafp() -> None:
    print("=" * 70)
    print("6. LBYL 和 EAFP 在哪里分歧")
    for raw in ("42", "-5", " 7 ", "²", "abc", "1_000", "1__000", "_1"):
        lbyl = looks_like_int(raw)
        eafp = parse_int(raw)
        mark = "" if lbyl == (eafp is not None) else "   ← 不一致"
        print(f"   {raw!r:<10} LBYL={lbyl!s:<6} EAFP={eafp!r:<6}{mark}")


def bonus_wide(raw_guess: str, bonus_text: str) -> str:
    """✗ try 包得太大：配置写错了，也被说成是用户输入无效。"""
    try:
        guess = int(raw_guess)
        bonus = int(bonus_text)  # 这一行的错误不是用户的错
        return f"得分 {guess + bonus}"
    except ValueError:
        return "输入无效"


def demo_wide_try() -> None:
    print("=" * 70)
    print("7. try 包得太大，会把程序自己的 bug 伪装成用户的错")
    print(f"   bonus_wide('5', '10')    = {bonus_wide('5', '10')!r}")
    print(f"   bonus_wide('abc', '10')  = {bonus_wide('abc', '10')!r}   ← 正确：用户输错了")
    print(f"   bonus_wide('5', '10分')  = {bonus_wide('5', '10分')!r}   ← 错误：是配置写错了")


def check_num(guess: int, target: int) -> str:
    if guess == target:
        return "正确"
    elif guess < target:
        return "小了"
    else:
        return "大了"


def play_v5(seed: int | None = None) -> None:
    """第五版：EAFP 解析 + 范围检查。

    try 只包住 int(raw) 这一行，后面的比较、计数都在 try 外面。
    """
    target = random.Random(seed).randint(LOW, HIGH)
    print(f"我想好了一个 {LOW}-{HIGH} 之间的数，你有 {MAX_ATTEMPTS} 次机会。")

    attempts = 0
    while attempts < MAX_ATTEMPTS:
        raw = input(f"[{attempts + 1}/{MAX_ATTEMPTS}] 你猜： ")
        if raw.strip().lower() in ("q", "quit"):
            print("你选择了退出")
            break

        guess = parse_int(raw)
        if guess is None:
            print(f"   {raw!r} 不是整数，这次不算")
            continue
        if not LOW <= guess <= HIGH:
            print(f"   {guess} 超出了 {LOW}-{HIGH}，这次不算")
            continue

        attempts += 1
        result = check_num(guess, target)
        print(f"   {guess:>3} → {result}")
        if result == "正确":
            print(f"   用了 {attempts} 次")
            break
    else:
        print(f"次数用完了，答案是 {target}")

    print("本局结束")


def main() -> None:
    if len(sys.argv) > 1 and sys.argv[1] == "play":
        play_v5()
        return

    demo_builtin_exceptions()
    demo_flow()
    demo_finally()
    demo_bare_except()
    demo_as_e_scope()
    demo_lbyl_vs_eafp()
    demo_wide_try()
    print("=" * 70)
    print("想玩第五版：python -m m01_basics.ch01_05_example play")
    print("试试输入 abc、²、1_000、0、101。")


if __name__ == "__main__":
    main()
