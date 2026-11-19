"""第 1.8 章 · 练习。

    pytest tests/test_m01.py -k ch01_08 -v
"""

# ============================================================================
# 练习 1（基础）· 先猜，再验证
# ============================================================================

PREDICTIONS: dict[str, str | None] = {
    '{"a": 1}["b"]': None,
    '{"a": 1}.get("b")': None,
    '{"a": 1}.get("b", 0)': None,
    '1 in {"a": 1}': None,
    "{1: 'x', True: 'y'}": None,
    "type({})": None,
    "len({1, 1, 2})": None,
    "(1)": None,
    "(1,)": None,
    "{1, 2} & {2, 3}": None,
    "{[1]: 2}": None,
}


# ============================================================================
# 练习 2（基础）· 统计每种结果出现了几次
#
# 写 count_results(results)，返回一个字典：键是结果，值是出现次数。
#
#   count_results(["大了", "小了", "大了", "正确"]) → {"大了": 2, "小了": 1, "正确": 1}
#   count_results([])                              → {}
#
# 要求：用 dict.get 的写法，不要用 collections.Counter（做完可以对比一下）。
# ============================================================================


def count_results(results: list[str]) -> dict[str, int]:
    # TODO 练习 2
    raise NotImplementedError("请完成练习 2")


# ============================================================================
# 练习 3（基础）· 每个玩家的最好成绩
#
# records 是一串 (玩家名, 次数) 元组，同一个人可能出现多次。
# 写 best_scores(records)，返回每个人用的**最少**次数。
#
#   best_scores([("张三", 5), ("李四", 3), ("张三", 2), ("李四", 4)])
#   → {"张三": 2, "李四": 3}
#
# 要求：用 for name, attempts in records 解包元组。
# 想一想：第一次见到某个人时，字典里还没有他，该怎么判断？
# ============================================================================


def best_scores(records: list[tuple[str, int]]) -> dict[str, int]:
    # TODO 练习 3
    raise NotImplementedError("请完成练习 3")


# ============================================================================
# 练习 4（进阶）· 去重，但保留顺序
#
# 写两个函数：
#
# (a) first_repeat(guesses)：返回第一个「之前已经出现过」的数；没有重复就返回 None
#
#     first_repeat([50, 30, 50, 30]) → 50      （第 3 个元素 50 之前出现过）
#     first_repeat([1, 2, 3])        → None
#
# (b) unique_in_order(guesses)：去掉重复，保留每个数**第一次出现**的顺序
#
#     unique_in_order([3, 1, 3, 2, 1]) → [3, 1, 2]
#
# 要求：
#   - 两个函数都只能遍历一次列表
#   - (b) 不能用 list(set(guesses)) —— 测试会抓住它（示例第 6 节说明了为什么）
#
# 提示：(a) 用一个 set 记录「已经见过的」。(b) 可以同样用 set，也可以用 dict.fromkeys。
# ============================================================================


def first_repeat(guesses: list[int]) -> int | None:
    # TODO 练习 4 (a)
    raise NotImplementedError("请完成练习 4")


def unique_in_order(guesses: list[int]) -> list[int]:
    # TODO 练习 4 (b)
    raise NotImplementedError("请完成练习 4")
