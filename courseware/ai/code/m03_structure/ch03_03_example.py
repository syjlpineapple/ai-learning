"""第 3.3 章 · 检查 guess 包的分层是否成立。

    python -m m03_structure.ch03_03_example

拆分后的代码在 m03_structure/guess/ 下。这个文件不玩游戏，而是用第 3.1 章练习 3、4 的
参考答案（module_imports、find_cycle）静态检查三件事：
    1. 包内模块之间谁导入了谁
    2. 有没有反向依赖（下层导入了上层）和循环
    3. 哪些模块调用了 input() / print()
"""

from __future__ import annotations

import ast
from pathlib import Path

from m03_structure.ch03_01_solution import find_cycle, module_imports
from m03_structure.guess.rules import GuessGame

PACKAGE = "m03_structure.guess"
GUESS_DIR = Path(__file__).resolve().parent / "guess"

# 从上到下的层次。上层可以导入下层，反过来不行。
LAYERS = ["__main__", "cli", "rules", "errors"]


def internal_graph() -> dict[str, set[str]]:
    """guess 包内部的依赖图，模块名去掉包前缀，比如 {"cli": {"rules", "errors"}}。"""
    graph: dict[str, set[str]] = {}
    for path in sorted(GUESS_DIR.glob("*.py")):
        if path.stem == "__init__":
            continue
        imported = module_imports(path.read_text(encoding="utf-8"))
        graph[path.stem] = {name.removeprefix(PACKAGE + ".") for name in imported
                            if name.startswith(PACKAGE + ".")}
    return graph


def upward_imports(graph: dict[str, set[str]]) -> list[tuple[str, str]]:
    """找出「下层导入上层」的边。返回 (导入方, 被导入方)。"""
    rank = {name: i for i, name in enumerate(LAYERS)}
    return sorted((src, dst) for src, dsts in graph.items() for dst in dsts
                  if rank[dst] < rank[src])


def io_calls() -> dict[str, list[str]]:
    """每个模块里直接调用了 input / print 的位置（只看名字调用，不看 ask/say 这类参数）。"""
    found: dict[str, list[str]] = {}
    for path in sorted(GUESS_DIR.glob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        hits = [f"{node.func.id}() 第 {node.lineno} 行" for node in ast.walk(tree)
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                and node.func.id in ("input", "print")]
        if hits:
            found[path.stem] = hits
    return found


def io_defaults() -> dict[str, list[str]]:
    """把 input / print 当默认值传出去的位置 —— cli.play(ask=input, say=print) 就是这样用的。"""
    found: dict[str, list[str]] = {}
    for path in sorted(GUESS_DIR.glob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        hits = [f"{node.name}() 的默认值用了 {d.id}" for node in ast.walk(tree)
                if isinstance(node, ast.FunctionDef)
                for d in node.args.defaults
                if isinstance(d, ast.Name) and d.id in ("input", "print")]
        if hits:
            found[path.stem] = hits
    return found


def bisect_player(game: GuessGame) -> list[int]:
    """另一个「界面」：不问人，自己用二分法猜。

    它只用到 rules 层，cli 一行都没碰。分层成立的话，换一种使用方式就应该这么简单。
    """
    lo, hi = game.low, game.high
    while not game.is_over:
        mid = (lo + hi) // 2
        result = game.guess(mid)
        if result == "小了":
            lo = mid + 1
        elif result == "大了":
            hi = mid - 1
    return game.history


def main() -> None:
    graph = internal_graph()
    print("1. 包内依赖")
    for name in LAYERS:
        print(f"   {name:<10} → {', '.join(sorted(graph[name])) or '（不依赖包内任何模块）'}")
    print("2. 反向依赖：", upward_imports(graph) or "没有")
    print("   循环依赖：", find_cycle(graph) or "没有")
    print("3. 直接调用 input/print 的模块：", io_calls() or "没有")
    print("   把 input/print 当默认值的：", io_defaults())
    attempts = [len(bisect_player(GuessGame(t))) for t in range(1, 101)]
    print(f"4. 二分法玩家猜 1-100 的每一个答案：全部猜中={all(a <= 7 for a in attempts)}，"
          f"最多 {max(attempts)} 次，平均 {sum(attempts) / len(attempts):.2f} 次")


if __name__ == "__main__":
    main()
