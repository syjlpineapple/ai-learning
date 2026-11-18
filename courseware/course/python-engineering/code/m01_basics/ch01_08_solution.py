"""第 1.8 章 · 参考答案。"""

# ============================================================================
# 练习 1 · 先猜，再验证
# ============================================================================

PREDICTIONS: dict[str, str | None] = {
    # 用 [] 取不存在的键会报错
    '{"a": 1}["b"]': "KeyError",
    # get 取不存在的键返回 None，不报错
    '{"a": 1}.get("b")': "None",
    # 第二个参数是默认值
    '{"a": 1}.get("b", 0)': "0",
    # in 查的是键。1 是值，不是键
    '1 in {"a": 1}': "False",
    # 容易猜成两个键。True == 1 且哈希相同，是同一个键：保留第一次的键 1、最后一次的值 'y'
    "{1: 'x', True: 'y'}": "{1: 'y'}",
    # 空花括号是空字典，不是空集合
    "type({})": "<class 'dict'>",
    # 集合自动去重
    "len({1, 1, 2})": "2",
    # 括号里只有一个值，括号只是分组，不是元组
    "(1)": "1",
    # 逗号才是元组的标志
    "(1,)": "(1,)",
    # & 是交集
    "{1, 2} & {2, 3}": "{2}",
    # 列表可变、不可哈希，不能做键
    "{[1]: 2}": "TypeError",
}


# ============================================================================
# 练习 2 · 统计每种结果出现了几次
# ============================================================================


def count_results(results: list[str]) -> dict[str, int]:
    """counts.get(r, 0) + 1：没有这个键就当它是 0。

    直接写 counts[r] += 1 会在第一次遇到某个结果时报 KeyError ——
    += 要先读出旧值，而这个键还不存在。

    标准库的 collections.Counter 专门做这件事：Counter(results)。
    它是 dict 的子类，用法基本一样，还多了 most_common() 这类方法。
    能用 Counter 的地方就用 Counter；这里手写是为了看清它在做什么。
    """
    counts: dict[str, int] = {}
    for r in results:
        counts[r] = counts.get(r, 0) + 1
    return counts


# ============================================================================
# 练习 3 · 每个玩家的最好成绩
# ============================================================================


def best_scores(records: list[tuple[str, int]]) -> dict[str, int]:
    """第一次见到某人时字典里没有他 —— 用 `not in` 判断。

    另一种写法是 best.get(name)，再判断 is None。
    两种都对；`name not in best` 意图更直白，而且不怕值本身是 0 或 None。
    （值可能是 0 时，`if not best.get(name)` 就会出错 —— 又是第 1.2 章那个坑。）
    """
    best: dict[str, int] = {}
    for name, attempts in records:
        if name not in best or attempts < best[name]:
            best[name] = attempts
    return best


# ============================================================================
# 练习 4 · 去重，但保留顺序
# ============================================================================


def first_repeat(guesses: list[int]) -> int | None:
    """set 的 in 是 O(1)，所以整个函数是 O(n)。

    如果用列表记录「见过的」，每次 in 都要从头扫一遍，整个函数变成 O(n²)。
    猜数字的历史只有几个元素时看不出区别；处理十万条日志时就是秒级和小时级的区别。
    """
    seen: set[int] = set()
    for g in guesses:
        if g in seen:
            return g
        seen.add(g)
    return None


def unique_in_order(guesses: list[int]) -> list[int]:
    """dict 从 Python 3.7 起保证按插入顺序遍历，dict.fromkeys 正好利用了这一点：
    重复的键不会再插入一次，所以保留的是第一次出现的位置。

    为什么不能用 list(set(guesses))：
      集合不保证顺序。对小整数来说，CPython 的实现碰巧常常是从小到大，
      于是 list(set([3, 1, 3, 2])) 得到 [1, 2, 3] —— 看起来像「排好序了」，
      但这不是语言保证的行为，换一组数（比如 [30, 5, 100, 42, 7]）顺序就乱了。
      对字符串来说更明显：每次启动 Python，顺序都可能不同。
    """
    return list(dict.fromkeys(guesses))


# 用 set 手写的等价版本：
#
#     seen: set[int] = set()
#     result: list[int] = []
#     for g in guesses:
#         if g not in seen:
#             seen.add(g)
#             result.append(g)
#     return result
#
# 两种都只遍历一次。手写版本更啰嗦，但适用于「判断重复的依据」和「保留的值」不一样的场景，
# 比如按名字去重、保留整条记录。
