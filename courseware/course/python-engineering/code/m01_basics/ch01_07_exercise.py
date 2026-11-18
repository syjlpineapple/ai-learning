"""第 1.7 章 · 练习。

    pytest tests/test_m01.py -k ch01_07 -v
"""


def parse_int(raw: str) -> int | None:
    """第 1.5 章的成果，已经写好。"""
    try:
        return int(raw)
    except ValueError:
        return None


# ============================================================================
# 练习 1（基础）· 先猜，再验证
# ============================================================================

PREDICTIONS: dict[str, str | None] = {
    "[10, 20, 30][-1]": None,
    "[10, 20, 30][3]": None,
    "[10, 20, 30][1:10]": None,
    "[10, 20, 30][::-1]": None,
    "[3, 1, 2].sort()": None,
    "sorted([3, 1, 2])": None,
    "[1, 2] + [3]": None,
    "[1, 2] * 2": None,
    'list("abc")': None,
    "len([[1, 2], [3]])": None,
    "[x * 2 for x in range(4) if x != 2]": None,
}


# ============================================================================
# 练习 2（基础）· 从原始输入里挑出有效的猜测
#
# 写 valid_guesses(raw_inputs, low, high)：
#   - raw_inputs 是一组字符串（用户输入的原样）
#   - 返回一个新列表：能转成整数、且在 [low, high] 范围内的那些，转成 int 之后的值
#   - 顺序保持不变
#   - **不能修改 raw_inputs**
#
#   valid_guesses(["50", "abc", "0", " 7 ", "101", "42"], 1, 100) → [50, 7, 42]
#
# 要求：用列表推导式，或者一个普通 for 循环 + append，都可以。
# ============================================================================


def valid_guesses(raw_inputs: list[str], low: int = 1, high: int = 100) -> list[int]:
    # TODO 练习 2
    raise NotImplementedError("请完成练习 2")


# ============================================================================
# 练习 3（基础）· 建一个二维表格
#
# 写 make_grid(rows, cols, fill)，返回 rows 行、cols 列的二维列表，每个格子都是 fill。
#
#   make_grid(2, 3, 0) → [[0, 0, 0], [0, 0, 0]]
#
# 测试会改其中一个格子，检查其他行有没有跟着变。
# 先想想 [[fill] * cols] * rows 为什么不行（示例第 4 节）。
# ============================================================================


def make_grid(rows: int, cols: int, fill: int = 0) -> list[list[int]]:
    # TODO 练习 3
    raise NotImplementedError("请完成练习 3")


# ============================================================================
# 练习 4（进阶）· 原地删除超范围的猜测
#
# 下面这个函数想从 guesses 里删掉所有不在 [low, high] 里的数，**原地修改**，不返回值。
# 它有 bug：
#
#     guesses = [0, -1, 50, 200, 300, 42]
#     drop_out_of_range_buggy(guesses, 1, 100)
#     guesses  →  [-1, 50, 300, 42]        ← -1 和 300 没删掉
#
# 写 drop_out_of_range，要求：
#   1. 结果正确
#   2. **仍然是原地修改** —— 调用方手里的那个列表对象要变，而不是你新建一个列表 return 出去
#   3. 返回 None
#
# 测试会检查第 2 条：调用前后，guesses 必须还是同一个对象（id 不变），而且内容变了。
#
# 提示：示例第 6 节最后两行，对比 items[:] = ... 和 items = ... 的区别。
# ============================================================================


def drop_out_of_range_buggy(guesses: list[int], low: int, high: int) -> None:
    """保留原样，不要改 —— 测试会检查它确实有 bug。"""
    for g in guesses:
        if not low <= g <= high:
            guesses.remove(g)


def drop_out_of_range(guesses: list[int], low: int = 1, high: int = 100) -> None:
    # TODO 练习 4
    raise NotImplementedError("请完成练习 4")
