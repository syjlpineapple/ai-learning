"""第 3.2 章 · 练习。

    pytest tests/test_m03.py -k ch03_02 -v
"""

from __future__ import annotations

from collections.abc import Iterable

from m03_structure.ch03_02_example import GuessGame

# ============================================================================
# 练习 1（基础）· 先猜，再验证
#
# 下面每个表达式都在示例文件 ch03_02_example.py 的命名空间里求值，
# 用到的 Plain、Point、Shared、NoSuper …… 都定义在那个文件的第二部分。
#
# 填 repr 形式的结果（字符串要带引号），报错就填异常名。和第 1 章的规则一样：
#     结果是 True            → "True"
#     结果是字符串 大了       → "'大了'"
#     抛 TypeError           → "TypeError"
# ============================================================================

PREDICTIONS: dict[str, str | None] = {
    "GuessGame.guess(GuessGame(42), 50)": None,
    "GuessGame(42).remaining": None,
    "Plain(1, 2) == Plain(1, 2)": None,
    "Point(1, 2) == Point(1, 2)": None,
    "repr(Point(1, 2))": None,
    "len({Plain(1, 2), Plain(1, 2)})": None,
    "{Point(1, 2)}": None,
    "len({FrozenPoint(1, 2), FrozenPoint(1, 2)})": None,
    "Point('1', '2').x": None,
    "shared_after_other_add()": None,
    "counter_after_one_bump()": None,
    "typo_after_bump()": None,
    "slotted_after_bump()": None,
    "NoSuper(42, True).hint": None,
    "NoSuper(42, True).guess(1)": None,
    "isinstance(WithSuper(42, True), Base)": None,
}


# ============================================================================
# 练习 2（基础）· 记分板
#
# 写一个 Scoreboard 类，记录很多局游戏的结果：
#
#     board = Scoreboard()
#     board.add("张三", 5, won=True)
#     board.add("李四", 7, won=False)
#     board.add("张三", 3, won=True)
#
#     len(board)            → 3                    记录了几局（实现 __len__）
#     board.best("张三")     → 3                    赢的那些局里最少的次数
#     board.best("李四")     → None                 没赢过
#     board.best("王五")     → None                 没玩过
#     board.players         → ["张三", "李四"]       property；去重，按名字排序（sorted 的默认顺序）
#
# 要求：两个 Scoreboard 对象互不影响。测试会专门检查这一点（讲解第 4 节）。
# 把下面的占位类整个替换掉。
# ============================================================================


class Scoreboard:
    def __init__(self) -> None:
        # TODO 练习 2
        raise NotImplementedError("请完成练习 2")


# ============================================================================
# 练习 3（进阶）· 继承：带提示的猜数字
#
# 写 HintGame，继承示例里的 GuessGame：
#
#     game = HintGame(42, hint_after=2)
#     game.guess(50)   → "大了"
#     game.guess(10)   → "小了"
#     game.guess(30)   → "小了（提示：答案在 31-49 之间）"     ← 之前已经错了 2 次，这次开始带提示
#     game.guess(42)   → "正确"                               ← 猜对了不加提示
#
#     什么时候带提示：这次猜之前，已经猜错的次数 >= hint_after
#     提示里的范围：从 low-high 开始，每猜错一次就收窄，只会变窄、不会变宽
#         猜小了 → 下限 = max(原下限, 这个数 + 1)
#         猜大了 → 上限 = min(原上限, 这个数 - 1)
#     hint_after 默认是 3；其他参数（target、max_attempts、low、high）和 GuessGame 一样
#
# 要求：
#     history、次数上限、GameOverError 这些行为全部沿用父类，不要重写一遍
#         —— 在 guess 里调用 super().guess(n) 拿到「大了/小了/正确」，再决定加不加提示
#     __init__ 里记得调用 super().__init__(...)（讲解第 8 节）
# ============================================================================


class HintGame(GuessGame):
    def __init__(self, target: int, max_attempts: int = 7, low: int = 1, high: int = 100,
                 hint_after: int = 3) -> None:
        # TODO 练习 3
        raise NotImplementedError("请完成练习 3")


# ============================================================================
# 练习 4（进阶）· 用 dataclass 做排行榜
#
# 1. 把 GameRecord 改成 dataclass，三个字段依次是：
#        player: str
#        attempts: int
#        won: bool
#    并且让它能放进集合（提示：讲解第 7 节，默认的 dataclass 不行）
#
# 2. 写 top(records, n=3)：
#        只要赢了的局
#        完全相同的记录只算一条（同一局被重复提交了）
#        按次数从少到多排；次数相同按玩家名排
#        返回前 n 条，类型是 list[GameRecord]
#
#    top([GameRecord("张三", 5, True), GameRecord("李四", 3, True),
#         GameRecord("张三", 5, True), GameRecord("王五", 2, False)])
#    → [GameRecord(player='李四', attempts=3, won=True),
#       GameRecord(player='张三', attempts=5, won=True)]
# ============================================================================


class GameRecord:
    """TODO 练习 4：改成 dataclass。"""


def top(records: Iterable[GameRecord], n: int = 3) -> list[GameRecord]:
    # TODO 练习 4
    raise NotImplementedError("请完成练习 4")
