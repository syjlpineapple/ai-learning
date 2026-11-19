"""第 2.1 章 · 讲解里的可运行示例。

这个文件最重要的用途是演示 `-O` 模式对 assert 的影响。
**请务必用两种方式各跑一次，对比输出：**

    python -m m02_testing.ch02_01_example
    python -O -m m02_testing.ch02_01_example

第 1 节和第 5 节的输出会完全不同。
"""

import dis
import sys


def check_num(input_num: int, target_num: int) -> str:
    """比较猜测值和目标值，返回提示文字。

    这是一个纯函数：相同输入永远得到相同输出，不做任何 IO。
    所以它可以直接传参、直接断言返回值。
    """
    if input_num == target_num:
        return "正确"
    elif input_num < target_num:
        return "小了"
    else:
        return "大了"


def parse_age_wrong(s: str) -> int:
    """✗ 错误示范：用 assert 校验外部输入。

    -O 模式下 assert 被删除，这个校验会静默失效。
    """
    age = int(s)
    assert 0 <= age <= 150, "年龄不合法"
    return age


def parse_age_right(s: str) -> int:
    """✓ 正确示范：外部输入用 raise 校验。

    raise 不受 -O 影响，任何模式下都生效。
    """
    age = int(s)
    if not 0 <= age <= 150:
        raise ValueError(f"年龄不合法：{age}")
    return age


def demo_1_assert_message() -> None:
    """断言失败时，带消息和不带消息的区别。"""
    print("=" * 70)
    print("1. assert 失败时的报错")

    try:
        assert check_num(30, 50) == "大了"
    except AssertionError as e:
        print(f"   不带消息: AssertionError, args={e.args!r}")

    try:
        result = check_num(30, 50)
        expected = "大了"
        assert result == expected, f"预期 {expected}，实际得到 {result}"
    except AssertionError as e:
        print(f"   带消息  : AssertionError: {e}")

    # -O 模式下上面两个 assert 都被删除，异常不会抛出，
    # except 分支不执行，这一节什么都不会打印。


def demo_2_optimize_flag() -> None:
    """用字节码证明 -O 删掉了 assert。"""
    print("=" * 70)
    print("2. -O 模式对 assert 的影响：看字节码")
    print(f"   当前 __debug__ = {__debug__}")
    print(f"   当前优化级别 sys.flags.optimize = {sys.flags.optimize}")
    print()
    print("   parse_age_wrong 的字节码里和 assert 有关的指令：")

    found = False
    for ins in dis.get_instructions(parse_age_wrong):
        if ins.opname in ("LOAD_ASSERTION_ERROR", "RAISE_VARARGS"):
            print(f"     {ins.offset:>4} {ins.opname}")
            found = True
    if not found:
        print("     （没有任何 assert 相关指令 —— assert 已被编译器移除）")

    print()
    print("   对比 parse_age_right（用 raise）的字节码：")
    for ins in dis.get_instructions(parse_age_right):
        if ins.opname == "RAISE_VARARGS":
            print(f"     {ins.offset:>4} {ins.opname}   ← raise 不受 -O 影响，始终存在")


def demo_3_always_true() -> None:
    """恒为真的断言：为什么它永远不失败。"""
    print("=" * 70)
    print("3. 恒为真的断言")
    for v in ("小了", "正确", "大了"):
        print(f"   bool({v!r}) = {bool(v)}")
    print("   → assert check_num(...) 只要返回非空字符串就通过，和内容无关")


def test_check_num() -> None:
    """三个场景的断言。本章先写在一个函数里，第 8.2 章会拆开。"""
    assert check_num(30, 50) == "小了"
    assert check_num(50, 50) == "正确"
    assert check_num(70, 50) == "大了"


def demo_4_silence_is_pass() -> None:
    """全部断言通过时的输出。"""
    print("=" * 70)
    print("4. 全部断言通过时的输出")
    test_check_num()
    print("   （上面这行调用没有产生任何输出 —— 这就是通过的样子）")


def test_never_called() -> None:
    """这个测试一定失败，但它永远不会被调用。"""
    assert 1 == 2, "这条断言一定失败"


def demo_5_forgot_to_call() -> None:
    """定义了测试函数但忘记调用。"""
    print("=" * 70)
    print("5. 定义了测试函数但忘记调用")
    print("   test_never_called 里写着 assert 1 == 2，但没有调用它。")
    print("   程序继续运行，没有任何提示。")
    print(f"   函数对象存在吗：{callable(test_never_called)}")
    print()
    print("   取消下面一行的注释，才会看到它失败：")
    print("   # test_never_called()")


def demo_6_raise_still_works() -> None:
    """raise 版本的校验在 -O 下依然生效。"""
    print("=" * 70)
    print("6. 两种校验在当前模式下的表现")

    for name, fn in (("parse_age_wrong (assert)", parse_age_wrong),
                     ("parse_age_right (raise) ", parse_age_right)):
        try:
            value = fn("200")
            print(f"   {name}: 没有拦住，返回了 {value}  ← 校验失效")
        except (AssertionError, ValueError) as e:
            print(f"   {name}: 拦住了，{type(e).__name__}: {e}")


def main() -> None:
    demo_1_assert_message()
    demo_2_optimize_flag()
    demo_3_always_true()
    demo_4_silence_is_pass()
    demo_5_forgot_to_call()
    demo_6_raise_still_works()
    print("=" * 70)
    if __debug__:
        print("现在用 python -O 再跑一次，对比第 1、2、6 节的输出。")
    else:
        print("这是 -O 模式的输出。第 1 节整节消失，第 2 节没有 assert 指令，")
        print("第 6 节里 assert 版本的校验已经失效。")


if __name__ == "__main__":
    main()
