"""第 3.1 章 · 参考答案。

    python -m m03_structure.ch03_01_solution
        用练习 3、4 的两个函数，扫描示例里的 lab/ 和这门课自己的代码仓，找循环导入。
"""

from __future__ import annotations

import ast
import sys
import tempfile
from collections.abc import Iterable
from pathlib import Path

# ============================================================================
# 练习 1
# ============================================================================

PREDICTIONS: dict[str, str | None] = {
    # 脚本方式运行：sys.path[0] 是 lab/app/，那里面没有叫 app 的东西
    "lab/ 下：python app/main.py": "ModuleNotFoundError",
    # -m：sys.path[0] 是当前目录 lab/，app 包找得到
    "lab/ 下：python -m app.main": "OK",
    # 把 main 当成包、去找它下面的 py 子模块。注意：报错之前 main.py 已经被完整执行了一遍
    "lab/ 下：python -m app.main.py": "ModuleNotFoundError",
    # 脚本方式运行时没有「所在的包」，相对导入无从谈起
    "lab/ 下：python app/rel.py": "ImportError",
    "lab/ 下：python -m app.rel": "OK",
    # 裸导入 util：sys.path 里只有 lab/，没有 lab/app/
    "lab/ 下：python -m app.bare": "ModuleNotFoundError",
    # 反过来，在 app/ 里直接运行，sys.path[0] 正好是 app/
    "lab/app/ 下：python bare.py": "OK",
    # from 形式的循环导入：b 要拿 a.bar 时，a 才执行到第一行
    "lab/ 下：python -c 'import cyc.a'": "ImportError",
    # import 形式：只要求 cyc2.b 这个模块对象存在，不要求里面已经有 foo
    "lab/ 下：python -c 'import cyc2.a'": "OK",
    # pytest 命令不会把当前目录放进 sys.path；它放的是 tests/
    "lab/ 下：pytest tests": "ModuleNotFoundError",
    # python -m pytest 会，所以 from app import util 找得到
    "lab/ 下：python -m pytest tests": "OK",
    # -m 把 shadow/ 放进 sys.path[0]，pytest 启动时间接用到的 tempfile 要导入 random
    "lab/shadow/ 下：python -m pytest --version": "ImportError",
}


# ============================================================================
# 练习 2
# ============================================================================


def find_shadowing(directory: Path, extra: Iterable[str] = ()) -> list[str]:
    banned = set(sys.stdlib_module_names) | {"test"} | set(extra)
    found: set[str] = set()
    for entry in directory.iterdir():
        if entry.is_file() and entry.suffix == ".py":
            name = entry.stem
        elif entry.is_dir() and (entry / "__init__.py").is_file():
            name = entry.name
        else:
            continue
        if name.startswith("__"):
            continue
        if name in banned:
            found.add(name)
    return sorted(found)


# ============================================================================
# 练习 3
# ============================================================================


def module_imports(source: str) -> set[str]:
    found: set[str] = set()

    def visit(node: ast.AST) -> None:
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue  # 函数体在调用时才执行
            if isinstance(child, ast.Import):
                found.update(alias.name for alias in child.names)
            elif isinstance(child, ast.ImportFrom):
                if child.level == 0 and child.module is not None:
                    found.add(child.module)
            else:
                visit(child)

    visit(ast.parse(source))
    return found


# ============================================================================
# 练习 4
# ============================================================================


def find_cycle(graph: dict[str, set[str]]) -> list[str] | None:
    done: set[str] = set()          # 已经确认「从它出发找不到环」的点

    def dfs(node: str, path: list[str]) -> list[str] | None:
        if node in path:
            return path[path.index(node):] + [node]
        if node in done or node not in graph:
            return None
        path.append(node)
        for nxt in sorted(graph[node]):          # 排序只是为了结果稳定
            cycle = dfs(nxt, path)
            if cycle is not None:
                return cycle
        path.pop()
        done.add(node)
        return None

    for start in sorted(graph):
        cycle = dfs(start, [])
        if cycle is not None:
            return cycle
    return None


# ============================================================================
# 把两个函数组合起来：扫描一个目录，得到导入关系图
# ============================================================================


def import_graph(root: Path) -> dict[str, set[str]]:
    """root 下所有 .py 文件 → 模块名 → 它导入的模块集合。

    简化处理：import a.b 实际上还会先导入包 a 的 __init__.py，这里没有把这条边加进去。
    """
    graph: dict[str, set[str]] = {}
    for path in sorted(root.rglob("*.py")):
        parts = list(path.relative_to(root).with_suffix("").parts)
        if parts[-1] == "__init__":
            parts.pop()
        if not parts:
            continue
        graph[".".join(parts)] = module_imports(path.read_text(encoding="utf-8"))
    return graph


def main() -> None:
    from m03_structure.ch03_01_example import build_lab

    with tempfile.TemporaryDirectory() as tmp:
        lab = Path(tmp)
        build_lab(lab)
        graph = import_graph(lab)
        print("lab/ 里的循环：", find_cycle(graph))
        without_cyc = {k: v for k, v in graph.items() if not k.startswith("cyc.")}
        print("去掉 cyc 包以后：", find_cycle(without_cyc))
        print("lab/ 里会遮蔽标准库的名字：", find_shadowing(lab), find_shadowing(lab / "shadow"))

    code_dir = Path(__file__).resolve().parents[1]
    course = {k: v for k, v in import_graph(code_dir).items() if k.startswith("m0")}
    print(f"课程代码仓（{len(course)} 个模块）里的循环：", find_cycle(course))


if __name__ == "__main__":
    main()
