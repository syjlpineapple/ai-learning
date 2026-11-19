"""第 1 题 · 排行榜存盘。

把三个函数的 raise NotImplementedError 换成你的实现，然后：

    pytest tests/test_m04.py -k p01 -v

文件格式（纯文本，UTF-8，每行一条）：

    李四,3
    张三,5
"""

from __future__ import annotations

from pathlib import Path


def save_scores(path: str | Path, scores: dict[str, int]) -> None:
    """把 {名字: 次数} 写进文件，覆盖原内容，按次数从少到多排。"""
    raise NotImplementedError("请完成要求 1")


def load_scores(path: str | Path) -> dict[str, int]:
    """读文件，返回 {名字: 次数}。文件不存在返回 {}；空行跳过；同一个名字出现多次取最小值。"""
    raise NotImplementedError("请完成要求 2")


def add_score(path: str | Path, name: str, attempts: int) -> None:
    """在文件末尾追加一行。文件不存在就新建。"""
    raise NotImplementedError("请完成要求 3")
