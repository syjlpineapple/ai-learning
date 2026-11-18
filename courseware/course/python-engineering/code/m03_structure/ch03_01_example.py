"""第 3.1 章 · 讲解里的可运行示例。

    python -m m03_structure.ch03_01_example

在临时目录里搭一个小项目 lab/，用子进程跑各种 import 场景，把真实输出打印出来。
每个场景都是一个新的 Python 进程 —— import 的行为和「当前进程已经导入过什么」有关，
在同一个进程里做实验，结果会被缓存污染。

讲解里引用的输出都来自这个文件。练习 1 的标准答案也是用这里的 SCENARIOS 现场跑出来的。
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
import tempfile
import textwrap
from pathlib import Path

# ============================================================================
# 实验项目 lab/ 的全部文件
# ============================================================================

LAB_FILES = {
    # ---- app：一个普通的包 ------------------------------------------------
    "app/__init__.py": 'print("[app/__init__.py 被执行]")\n',
    "app/util.py": 'print("[util.py 被执行]")\nVALUE = 42\n',
    "app/main.py": """
        import sys
        print("sys.path[0] =", sys.path[0] or "''（空字符串，代表当前目录）")
        print("__name__   =", __name__)
        from app import util
        print("VALUE      =", util.VALUE)
    """,
    "app/who.py": """
        print(f"__name__={__name__!r}  __package__={__package__!r}")
    """,
    "app/rel.py": """
        from .util import VALUE
        print("rel VALUE =", VALUE)
    """,
    # 裸导入：只写模块名，不写包名（学习记录 Day10 最初的写法）
    "app/bare.py": """
        from util import VALUE
        print("bare VALUE =", VALUE)
    """,
    "app/twice.py": """
        import sys
        import app.util
        import app.util
        print("第二次 import 没有再执行 util.py；它在 sys.modules 里：", "app.util" in sys.modules)
    """,
    # ---- cyc：from 形式的循环导入 → 报错 -----------------------------------
    "cyc/__init__.py": "",
    "cyc/a.py": """
        from cyc.b import foo

        def bar():
            return "bar"
    """,
    "cyc/b.py": """
        from cyc.a import bar

        def foo():
            return "foo"
    """,
    # ---- cyc2：import 形式的循环导入 → 能跑，但循环还在 ---------------------
    "cyc2/__init__.py": "",
    "cyc2/a.py": """
        import cyc2.b

        def bar():
            return "bar"

        def call_foo():
            return cyc2.b.foo()
    """,
    "cyc2/b.py": """
        import cyc2.a

        def foo():
            return "foo+" + cyc2.a.bar()
    """,
    # ---- snap：from X import 名字，拿到的是那一刻的值 ------------------------
    "snap/__init__.py": "",
    "snap/config.py": """
        LEVEL = "INFO"

        def set_level(value):
            global LEVEL
            LEVEL = value
    """,
    "snap/use.py": """
        import snap.config
        from snap.config import LEVEL, set_level

        set_level("DEBUG")
        print("from 导入的 LEVEL   =", LEVEL)
        print("snap.config.LEVEL   =", snap.config.LEVEL)
    """,
    # ---- dual：用 -m 运行的模块又被别人导入 → 执行两次 ----------------------
    "dual/__init__.py": "",
    "dual/state.py": """
        print(f"[state.py 被执行  __name__={__name__}]")

        class Token:
            pass

        if __name__ == "__main__":
            from dual import other
            t = Token()
            print("isinstance(t, other.Token) =", isinstance(t, other.Token))
    """,
    "dual/other.py": "from dual.state import Token\n",
    # ---- warn：包的 __init__.py 导入了要用 -m 运行的那个模块 ----------------
    "warn/__init__.py": "from warn import tool\n",
    "warn/tool.py": 'print(f"[tool.py 被执行  __name__={__name__}]")\n',
    # ---- ns：没有 __init__.py 的目录 ----------------------------------------
    "ns/mod.py": "X = 1\n",
    # ---- tests：测试目录，没有 __init__.py ---------------------------------
    "tests/test_lab.py": """
        from app import util

        def test_value():
            assert util.VALUE == 42
    """,
    # ---- shadow：一个和标准库同名的文件 -------------------------------------
    "shadow/random.py": "",
}


def build_lab(root: Path) -> None:
    for rel, content in LAB_FILES.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(textwrap.dedent(content).lstrip(), encoding="utf-8")


# ============================================================================
# 运行工具
# ============================================================================


def pytest_command() -> list[str]:
    """「直接敲 pytest」对应的命令。

    pip 装 pytest 时会在 Scripts/（或 bin/）下生成一个 pytest 可执行文件。
    它和 python -m pytest 的区别正是讲解第 7 节的内容，所以这里要用它本身。
    """
    script = Path(sys.executable).with_name("pytest.exe" if os.name == "nt" else "pytest")
    if script.exists():
        return [str(script)]
    # 找不到时用等价的写法：-c 会把 '' 放进 sys.path[0]，删掉它就和入口脚本一样了
    return [sys.executable, "-c",
            "import sys; sys.path.pop(0); import pytest; raise SystemExit(pytest.main())"]


def run_in(root: Path, cwd: str, args: list[str]) -> subprocess.CompletedProcess[str]:
    """在 root/cwd 下开一个新进程。args 以 'python' 或 'pytest' 开头。"""
    head, *rest = args
    cmd = [sys.executable, *rest] if head == "python" else [*pytest_command(), *rest]
    env = {**os.environ, "PYTHONUTF8": "1"}
    env.pop("PYTHONPATH", None)   # 外面设过 PYTHONPATH 的话，实验结果会不一样
    return subprocess.run(cmd, cwd=root / cwd, capture_output=True, text=True,
                          encoding="utf-8", env=env, check=False)


def outcome(done: subprocess.CompletedProcess[str]) -> str:
    """把一次运行的结果归纳成一个词：成功是 "OK"，失败是最后出现的那个异常名。"""
    if done.returncode == 0:
        return "OK"
    names = re.findall(r"\b([A-Z]\w*Error)\b", done.stdout + done.stderr)
    return names[-1] if names else f"exit {done.returncode}"


# 练习 1 的场景。键是题面，值是（在 lab 下的哪个目录运行，命令）。
SCENARIOS: dict[str, tuple[str, list[str]]] = {
    "lab/ 下：python app/main.py": (".", ["python", "app/main.py"]),
    "lab/ 下：python -m app.main": (".", ["python", "-m", "app.main"]),
    "lab/ 下：python -m app.main.py": (".", ["python", "-m", "app.main.py"]),
    "lab/ 下：python app/rel.py": (".", ["python", "app/rel.py"]),
    "lab/ 下：python -m app.rel": (".", ["python", "-m", "app.rel"]),
    "lab/ 下：python -m app.bare": (".", ["python", "-m", "app.bare"]),
    "lab/app/ 下：python bare.py": ("app", ["python", "bare.py"]),
    "lab/ 下：python -c 'import cyc.a'": (".", ["python", "-c", "import cyc.a"]),
    "lab/ 下：python -c 'import cyc2.a'": (".", ["python", "-c", "import cyc2.a"]),
    "lab/ 下：pytest tests": (".", ["pytest", "tests", "-q", "-p", "no:cacheprovider"]),
    "lab/ 下：python -m pytest tests": (
        ".", ["python", "-m", "pytest", "tests", "-q", "-p", "no:cacheprovider"]),
    "lab/shadow/ 下：python -m pytest --version": (
        "shadow", ["python", "-m", "pytest", "--version"]),
}


def scenario_outcomes(root: Path) -> dict[str, str]:
    """在 root（已经 build_lab 过）里把所有场景跑一遍，得到真实结果。"""
    return {key: outcome(run_in(root, cwd, args)) for key, (cwd, args) in SCENARIOS.items()}


# ============================================================================
# 演示
# ============================================================================


def section(title: str) -> None:
    print("=" * 72)
    print(title)


def show(root: Path, cwd: str, args: list[str], last: int | None = None,
         keep: tuple[str, ...] = ()) -> None:
    """运行并打印输出。last 只看最后几行；keep 只看包含这些片段的行。"""
    where = "lab/" if cwd == "." else f"lab/{cwd}/"
    print(f"  $ ({where}) {' '.join(args)}")
    done = run_in(root, cwd, args)
    lines = (done.stdout + done.stderr).strip().splitlines()
    if keep:
        lines = [line for line in lines if any(k in line for k in keep)]
    if last is not None:
        lines = lines[-last:]
    for line in lines:
        # 临时目录的路径又长又随机，换成 <lab>。报错里的路径有时是 repr 形式（反斜杠成对）
        line = line.replace(str(root).replace("\\", "\\\\"), "<lab>").replace(str(root), "<lab>")
        print(f"      {line}")
    print(f"      → 退出码 {done.returncode}")


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp) / "lab"
        build_lab(root)

        section("1. import 做的三件事：找到、执行一次、绑定名字")
        show(root, ".", ["python", "-m", "app.twice"])

        section("2. 同一个文件，两种运行方式，sys.path[0] 不同")
        show(root, ".", ["python", "app/main.py"])
        show(root, ".", ["python", "-m", "app.main"])
        show(root, ".", ["python", "-c", "import sys; print(repr(sys.path[0]))"])

        section("3. __name__ 的三种取值")
        show(root, ".", ["python", "app/who.py"])
        show(root, ".", ["python", "-m", "app.who"])
        show(root, ".", ["python", "-c", "import app.who"])

        section("4. -m 后面写成文件路径")
        show(root, ".", ["python", "-m", "app/main.py"])
        show(root, ".", ["python", "-m", "app.main.py"])

        section("5. 相对导入与裸导入")
        show(root, ".", ["python", "app/rel.py"], last=1)
        show(root, ".", ["python", "-m", "app.rel"])
        show(root, ".", ["python", "-m", "app.bare"], last=1)
        show(root, "app", ["python", "bare.py"])

        section("6. from X import 名字：拿到的是导入那一刻的值")
        show(root, ".", ["python", "-m", "snap.use"])

        section("7. 循环导入")
        show(root, ".", ["python", "-c", "import cyc.a"], last=1)
        show(root, ".", ["python", "-c", "import cyc2.a; print(cyc2.a.call_foo())"])

        section("8. 用 -m 运行的模块又被别人导入：同一个文件执行了两次")
        show(root, ".", ["python", "-m", "dual.state"])
        show(root, ".", ["python", "-m", "warn.tool"])

        section("9. 没有 __init__.py 的目录也能导入（命名空间包）")
        show(root, ".", ["python", "-c",
                         "import ns.mod, ns; print('ns.__file__ =', ns.__file__)"])

        section("10. pytest 和 python -m pytest")
        show(root, ".", ["pytest", "tests", "-q", "-p", "no:cacheprovider"],
             keep=("E   ", "error in"))
        show(root, ".", ["python", "-m", "pytest", "tests", "-q", "-p", "no:cacheprovider"],
             last=1)

        section("11. 当前目录有 random.py：python -m pytest 直接启动不了")
        show(root, "shadow", ["python", "-m", "pytest", "--version"], last=1)


if __name__ == "__main__":
    main()
