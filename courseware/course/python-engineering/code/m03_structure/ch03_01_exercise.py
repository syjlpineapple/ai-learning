"""第 3.1 章 · 练习。

    pytest tests/test_m03.py -k ch03_01 -v
"""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

# ============================================================================
# 练习 1（基础）· 先猜，再验证
#
# 示例文件 ch03_01_example.py 里的 LAB_FILES 是一个小项目 lab/。
# 先读懂里面每个文件写了什么，再判断下面每条命令的结果：
#     成功（退出码 0）     → 填 "OK"
#     失败                 → 填最后报出的那个异常名，比如 "ModuleNotFoundError"
#
# 不要先跑示例。猜完再跑测试，测试会现场搭一遍 lab/、把每条命令真的跑一遍来判分。
# ============================================================================

PREDICTIONS: dict[str, str | None] = {
    "lab/ 下：python app/main.py": None,
    "lab/ 下：python -m app.main": None,
    "lab/ 下：python -m app.main.py": None,
    "lab/ 下：python app/rel.py": None,
    "lab/ 下：python -m app.rel": None,
    "lab/ 下：python -m app.bare": None,
    "lab/app/ 下：python bare.py": None,
    "lab/ 下：python -c 'import cyc.a'": None,
    "lab/ 下：python -c 'import cyc2.a'": None,
    "lab/ 下：pytest tests": None,
    "lab/ 下：python -m pytest tests": None,
    "lab/shadow/ 下：python -m pytest --version": None,
}


# ============================================================================
# 练习 2（基础）· 遮蔽检查器
#
# 写 find_shadowing(directory, extra)，找出 directory 里会遮蔽标准库的名字。
#
#     只看 directory 这一层，不递归
#     检查两类东西：
#         *.py 文件                  名字取去掉 .py 的部分
#         含 __init__.py 的子目录     名字取目录名
#     名字以 __ 开头的跳过（__init__.py、__main__.py 是正常文件）
#     名字满足下面任意一条就算遮蔽：
#         在 sys.stdlib_module_names 里
#         是 "test"  —— 标准库确实有 test 包，但 stdlib_module_names 不列测试模块
#         在 extra 里  —— 用来传入你装的第三方库名，比如 ("requests", "pytest")
#     返回排好序、不重复的列表；没有就返回 []
#
# 为什么没有 __init__.py 的目录不算：讲解第 8 节。
# ============================================================================


def find_shadowing(directory: Path, extra: Iterable[str] = ()) -> list[str]:
    # TODO 练习 2
    raise NotImplementedError("请完成练习 2")


# ============================================================================
# 练习 3（进阶）· 一个模块在导入时会导入谁
#
# 写 module_imports(source)：source 是一个 .py 文件的源码，返回它导入的模块名集合。
#
#     import a                → "a"
#     import a.b as c         → "a.b"
#     import a, b             → "a" 和 "b"
#     from a.b import c, d    → "a.b"
#     from . import x         → 忽略（相对导入，level > 0）
#     from .m import y        → 忽略
#
#     函数体（def 和 async def）里的 import 不算：它们在函数被调用时才执行，
#         不会在导入阶段引发循环导入（讲解第 7 节的解法 2）
#     类体、if、try、with 里的 import 都算：它们在导入阶段就会执行
#
# 用标准库 ast 解析源码：ast.parse(source) 得到语法树，
# ast.Import / ast.ImportFrom 是两种 import 语句，
# ast.FunctionDef / ast.AsyncFunctionDef 是函数定义，
# ast.iter_child_nodes(node) 可以遍历一个节点的直接子节点。
# ============================================================================


def module_imports(source: str) -> set[str]:
    # TODO 练习 3
    raise NotImplementedError("请完成练习 3")


# ============================================================================
# 练习 4（进阶）· 找出循环依赖
#
# 写 find_cycle(graph)：graph 是「模块 → 它导入的模块集合」，返回其中一个环。
#
#     find_cycle({"a": {"b"}, "b": {"a"}})          → ["a", "b", "a"]
#     find_cycle({"a": {"b"}, "b": {"c"}, "c": {"a"}}) → ["a", "b", "c", "a"]（从哪个点开始都行）
#     find_cycle({"a": {"a"}})                      → ["a", "a"]
#     find_cycle({"a": {"b"}, "b": set()})          → None
#
#     返回的列表首尾相同，相邻两个之间必须真的有一条边
#     graph 里只出现在值里、没作为键出现的模块（比如标准库），当作没有依赖
#
# 提示：深度优先搜索。记住「当前这条路径上有哪些点」，走到路径上已有的点就是环。
# ============================================================================


def find_cycle(graph: dict[str, set[str]]) -> list[str] | None:
    # TODO 练习 4
    raise NotImplementedError("请完成练习 4")
