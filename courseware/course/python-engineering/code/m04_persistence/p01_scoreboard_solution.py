"""第 1 题 · 参考答案。"""

from __future__ import annotations

import os
from pathlib import Path


def save_scores(path: str | Path, scores: dict[str, int]) -> None:
    path = Path(path)
    # 先把要写的内容全部准备好。这一步出错时，文件还没被打开，原内容不受影响
    ranked = sorted(scores.items(), key=lambda item: (item[1], item[0]))
    text = "".join(f"{name},{attempts}\n" for name, attempts in ranked)
    # 写到同目录的临时文件，写完再替换。'w' 模式在打开那一刻就清空文件，
    # 直接写原文件的话，中途出错原数据就没了
    tmp = path.with_name(path.name + ".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(text)
    os.replace(tmp, path)   # 新文件完整写好之后才替换旧文件；目标已存在时直接覆盖


def load_scores(path: str | Path) -> dict[str, int]:
    path = Path(path)
    if not path.exists():
        return {}
    best: dict[str, int] = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            name, attempts = line.rsplit(",", 1)   # 名字里可能有逗号，从右边切一刀
            n = int(attempts)
            if name not in best or n < best[name]:
                best[name] = n
    return best


def add_score(path: str | Path, name: str, attempts: int) -> None:
    with open(path, "a", encoding="utf-8") as f:
        f.write(f"{name},{attempts}\n")
