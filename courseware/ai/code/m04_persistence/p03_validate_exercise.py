"""第 3 题 · 不信任读进来的数据。

把两个函数的 raise NotImplementedError 换成你的实现，然后：

    pytest tests/test_m04.py -k p03 -v

存档格式和第 2 题一样：

    {"1": {"player": "张三", "target": 42, "history": [50, 42], "won": true}}
"""

from __future__ import annotations

from pathlib import Path

Record = dict[str, object]
FIELDS = ("player", "target", "history", "won")
LOW, HIGH = 1, 100


class SaveFormatError(ValueError):
    """存档内容不合法。继承 ValueError，老代码的 except ValueError 照样接得住。"""


def parse_games(raw: object) -> dict[int, Record]:
    """校验 json.loads 得到的对象，合法就返回 {局号: 记录}，不合法抛 SaveFormatError。

    报错消息要能定位问题：写出是第几局、哪个字段、实际的值是什么。
    """
    raise NotImplementedError("请完成要求 1-4")


def load_games(path: str | Path) -> dict[int, Record]:
    """读文件、解析 JSON、校验。文件不存在返回 {}。"""
    raise NotImplementedError("请完成要求 5")
