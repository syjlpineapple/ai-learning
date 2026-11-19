"""M3 模块的测试。

两种用途：
  1. 验证讲解里的结论和参考答案本身是对的
  2. 检查你的练习做得对不对 —— 没做完的题会显示 skip

跑法：
    pytest tests/test_m03.py -v
    pytest tests/test_m03.py -k ch03_01 -v

第 3.1 章的很多测试会开子进程、在临时目录里搭项目，整个文件要跑十几秒。
"""

from __future__ import annotations

import dataclasses
import os
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

from m03_structure import ch03_01_example as example31
from m03_structure import ch03_01_exercise as ex31
from m03_structure import ch03_01_solution as sol31
from m03_structure import ch03_02_example as example32
from m03_structure import ch03_02_exercise as ex32
from m03_structure import ch03_02_solution as sol32
from m03_structure import ch03_03_example as example33
from m03_structure.guess import rules as guess_rules

CODE_DIR = Path(__file__).resolve().parents[1]


# ============================================================================
# 通用工具
# ============================================================================


def run_or_skip(fn: Callable[..., Any], *args: Any) -> Any:
    """调用练习里的函数。遇到 NotImplementedError 就跳过这条测试。"""
    try:
        return fn(*args)
    except NotImplementedError:
        pytest.skip(f"{getattr(fn, '__name__', fn)} 还没完成")


def run_python(cwd: Path, *args: str) -> subprocess.CompletedProcess[str]:
    env = {**os.environ, "PYTHONUTF8": "1"}
    env.pop("PYTHONPATH", None)
    return subprocess.run([sys.executable, *args], cwd=cwd, capture_output=True, text=True,
                          encoding="utf-8", env=env, check=False)


def output(done: subprocess.CompletedProcess[str]) -> str:
    return done.stdout + done.stderr


def assert_valid_cycle(graph: dict[str, set[str]], cycle: list[str] | None) -> None:
    assert cycle is not None, "这张图里有环，却返回了 None"
    assert len(cycle) >= 2 and cycle[0] == cycle[-1], f"环要首尾相同：{cycle}"
    for a, b in zip(cycle, cycle[1:]):
        assert b in graph.get(a, set()), f"{a} → {b} 这条边不存在：{cycle}"


# ============================================================================
# 3.1 · 示例：讲解里的每条结论
# ============================================================================


@pytest.fixture(scope="module")
def lab(tmp_path_factory: pytest.TempPathFactory) -> Path:
    root = tmp_path_factory.mktemp("lab")
    example31.build_lab(root)
    return root


@pytest.fixture(scope="module")
def scenario_truth(lab: Path) -> dict[str, str]:
    return example31.scenario_outcomes(lab)


def test_ch03_01_solution_predictions(scenario_truth: dict[str, str]) -> None:
    assert scenario_truth == sol31.PREDICTIONS


def test_ch03_01_module_runs_once(lab: Path) -> None:
    """讲解第 1 节：import 两次，模块只执行一次。"""
    out = output(run_python(lab, "-m", "app.twice"))
    assert out.count("[util.py 被执行]") == 1
    assert "sys.modules 里： True" in out


def test_ch03_01_script_vs_module_sys_path(lab: Path) -> None:
    """讲解第 2 节：脚本方式 sys.path[0] 是脚本所在目录，-m 是当前目录。"""
    script = run_python(lab, "app/main.py")
    assert f"sys.path[0] = {lab / 'app'}" in script.stdout
    assert "ModuleNotFoundError: No module named 'app'" in script.stderr
    module = run_python(lab, "-m", "app.main")
    assert module.returncode == 0
    assert f"sys.path[0] = {lab}\n" in module.stdout
    assert "__name__   = __main__" in module.stdout
    dash_c = run_python(lab, "-c", "import sys; print(repr(sys.path[0]))")
    assert dash_c.stdout.strip() == "''"


def test_ch03_01_name_three_ways(lab: Path) -> None:
    """讲解第 3 节：__name__ 和 __package__ 的三种组合。"""
    assert "__name__='__main__'  __package__=None" in output(run_python(lab, "app/who.py"))
    assert "__name__='__main__'  __package__='app'" in output(run_python(lab, "-m", "app.who"))
    assert "__name__='app.who'  __package__='app'" in output(
        run_python(lab, "-c", "import app.who"))


def test_ch03_01_dash_m_with_py_suffix_runs_module_first(lab: Path) -> None:
    """讲解第 4 节：python -m app.main.py 先把 app.main 当包导入（执行了一遍），然后才报错。"""
    done = run_python(lab, "-m", "app.main.py")
    assert done.returncode == 1
    assert "VALUE      = 42" in done.stdout, "报错之前 main.py 应该已经完整执行过"
    assert "__name__   = app.main" in done.stdout, "是被当成普通模块导入的，不是 __main__"
    assert "Try using 'app.main' instead of 'app.main.py'" in done.stderr


def test_ch03_01_relative_import_as_script(lab: Path) -> None:
    done = run_python(lab, "app/rel.py")
    assert "ImportError: attempted relative import with no known parent package" in done.stderr


def test_ch03_01_from_import_is_a_snapshot(lab: Path) -> None:
    """讲解第 6 节：from X import 名字，拿到的是导入那一刻那个名字指向的对象。"""
    out = output(run_python(lab, "-m", "snap.use"))
    assert "from 导入的 LEVEL   = INFO" in out
    assert "snap.config.LEVEL   = DEBUG" in out


def test_ch03_01_circular_import_message(lab: Path) -> None:
    out = output(run_python(lab, "-c", "import cyc.a"))
    assert ("cannot import name 'bar' from partially initialized module 'cyc.a' "
            "(most likely due to a circular import)") in out
    assert output(run_python(lab, "-c", "import cyc2.a; print(cyc2.a.call_foo())")).strip() \
        == "foo+bar"


def test_ch03_01_main_module_executed_twice(lab: Path) -> None:
    """讲解第 7 节：-m 运行的模块又被导入一次，两份 Token 类不是同一个。"""
    out = output(run_python(lab, "-m", "dual.state"))
    assert "[state.py 被执行  __name__=__main__]" in out
    assert "[state.py 被执行  __name__=dual.state]" in out
    assert "isinstance(t, other.Token) = False" in out


def test_ch03_01_runpy_warns_when_package_imports_main(lab: Path) -> None:
    """讲解第 7 节：包的 __init__.py 先导入了 tool，再用 -m 运行 tool，Python 会给一条警告。"""
    done = run_python(lab, "-m", "warn.tool")
    assert done.stdout.count("[tool.py 被执行") == 2
    assert ("RuntimeWarning: 'warn.tool' found in sys.modules after import of package 'warn', "
            "but prior to execution of 'warn.tool'") in done.stderr


def test_ch03_01_namespace_package(lab: Path) -> None:
    out = output(run_python(lab, "-c", "import ns.mod, ns; print('ns.__file__ =', ns.__file__)"))
    assert out.strip() == "ns.__file__ = None"


def test_ch03_01_dir_without_init_does_not_shadow(tmp_path: Path) -> None:
    """讲解第 8 节：没有 __init__.py 的同名目录不遮蔽标准库，有 __init__.py 的会。"""
    (tmp_path / "logging").mkdir()
    (tmp_path / "logging" / "x.py").write_text("", encoding="utf-8")
    (tmp_path / "json").mkdir()
    (tmp_path / "json" / "__init__.py").write_text("", encoding="utf-8")
    done = run_python(tmp_path, "-c",
                      "import logging, json; print(logging.__file__); print(json.__file__)")
    logging_file, json_file = done.stdout.strip().splitlines()
    assert not logging_file.startswith(str(tmp_path)), "logging 应该来自标准库"
    assert json_file.startswith(str(tmp_path)), "json 应该被同名包遮蔽"


def test_ch03_01_string_py_breaks_logging(tmp_path: Path) -> None:
    """讲解第 8 节：自己的 string.py 会让 import logging 失败 —— 出错的不是你导入的那个模块。"""
    (tmp_path / "string.py").write_text("", encoding="utf-8")
    done = run_python(tmp_path, "-c", "import logging")
    assert done.returncode == 1
    assert "ImportError: cannot import name 'Template' from 'string'" in done.stderr


def test_ch03_01_pycache_does_not_resurrect(tmp_path: Path) -> None:
    """讲解第 1 节：删掉源文件后，__pycache__ 里的 .pyc 不会让它继续可导入。"""
    (tmp_path / "gone.py").write_text("X = 1\n", encoding="utf-8")
    assert run_python(tmp_path, "-c", "import gone").returncode == 0
    (tmp_path / "gone.py").unlink()
    assert list((tmp_path / "__pycache__").glob("gone.*.pyc")), ".pyc 应该还在"
    done = run_python(tmp_path, "-c", "import gone")
    assert "ModuleNotFoundError: No module named 'gone'" in done.stderr


def test_ch03_01_pytest_inserts_test_dir(tmp_path: Path) -> None:
    """讲解第 9 节：pytest 放进 sys.path 的是测试文件所在目录（tests/ 没有 __init__.py 时）。"""
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_where.py").write_text(
        "import sys\ndef test_where():\n    print('SYSPATH0=' + sys.path[0])\n", encoding="utf-8")
    done = subprocess.run(
        [*example31.pytest_command(), "tests", "-q", "-s", "-p", "no:cacheprovider"],
        cwd=tmp_path, capture_output=True, text=True, encoding="utf-8", check=False)
    assert f"SYSPATH0={tmp_path / 'tests'}" in done.stdout


def test_ch03_01_stdlib_names_exclude_test() -> None:
    """练习 2 题面：sys.stdlib_module_names 不含 test，也不含 __main__。"""
    assert "random" in sys.stdlib_module_names
    assert "test" not in sys.stdlib_module_names
    assert "__main__" not in sys.stdlib_module_names


def test_ch03_01_example_runs() -> None:
    done = run_python(CODE_DIR, "-m", "m03_structure.ch03_01_example")
    assert done.returncode == 0, done.stderr
    assert "isinstance(t, other.Token) = False" in done.stdout


# ============================================================================
# 3.1 · 参考答案
# ============================================================================


def make_dir(root: Path, files: list[str]) -> Path:
    for rel in files:
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("", encoding="utf-8")
    return root


SHADOW_FILES = [
    "random.py", "game.py", "test.py", "requests.py", "__main__.py", "__init__.py",
    "json/__init__.py",          # 有 __init__.py 的包：算
    "logging/x.py",              # 没有 __init__.py 的目录：不算
    "notes/string.py",           # 子目录里的：不递归，不算
    "string.txt",                # 不是 .py：不算
]


def check_find_shadowing(fn: Callable[..., list[str]], tmp_path: Path) -> None:
    root = make_dir(tmp_path, SHADOW_FILES)
    assert fn(root) == ["json", "random", "test"]
    assert fn(root, ("requests", "pytest")) == ["json", "random", "requests", "test"]
    assert fn(make_dir(tmp_path / "clean", ["game.py", "main.py"])) == []


def test_ch03_01_solution_find_shadowing(tmp_path: Path) -> None:
    check_find_shadowing(sol31.find_shadowing, tmp_path)


IMPORT_SOURCE = '''
import os
import a.b as c
import x, y
from m.n import p, q
from . import sibling
from .rel import thing

if True:
    import in_if
try:
    from in_try import z
except ImportError:
    pass

class K:
    import in_class

    def method(self):
        import in_method

def f():
    import in_function

async def g():
    import in_async
'''

IMPORT_EXPECTED = {"os", "a.b", "x", "y", "m.n", "in_if", "in_try", "in_class"}


def test_ch03_01_solution_module_imports() -> None:
    assert sol31.module_imports(IMPORT_SOURCE) == IMPORT_EXPECTED
    assert sol31.module_imports("") == set()


CYCLE_GRAPHS: list[dict[str, set[str]]] = [
    {"a": {"b"}, "b": {"a"}},
    {"a": {"b"}, "b": {"c"}, "c": {"a"}},
    {"a": {"a"}},
    {"start": {"x", "os"}, "x": {"y"}, "y": {"x", "json"}},   # 环不经过起点
]
ACYCLIC_GRAPHS: list[dict[str, set[str]]] = [
    {},
    {"a": {"b"}, "b": set()},
    {"a": {"b", "c"}, "b": {"d"}, "c": {"d"}, "d": {"os"}},   # 菱形：d 被走到两次，但不是环
]


@pytest.mark.parametrize("graph", CYCLE_GRAPHS)
def test_ch03_01_solution_find_cycle(graph: dict[str, set[str]]) -> None:
    assert_valid_cycle(graph, sol31.find_cycle(graph))


@pytest.mark.parametrize("graph", ACYCLIC_GRAPHS)
def test_ch03_01_solution_find_no_cycle(graph: dict[str, set[str]]) -> None:
    assert sol31.find_cycle(graph) is None


def test_ch03_01_solution_scans_lab(lab: Path) -> None:
    """组合起来用：lab/ 里 cyc 和 cyc2 都有环 —— cyc2 能跑，但环还在。"""
    graph = sol31.import_graph(lab)
    assert_valid_cycle(graph, sol31.find_cycle({k: v for k, v in graph.items()
                                                if k.startswith("cyc.")}))
    assert_valid_cycle(graph, sol31.find_cycle({k: v for k, v in graph.items()
                                                if k.startswith("cyc2.")}))
    assert sol31.find_cycle({k: v for k, v in graph.items() if k.startswith("app")}) is None


def test_ch03_01_course_repo_has_no_cycles() -> None:
    graph = {k: v for k, v in sol31.import_graph(CODE_DIR).items() if k.startswith("m0")}
    assert len(graph) > 20
    assert sol31.find_cycle(graph) is None


# ============================================================================
# 3.1 · 练习
# ============================================================================


def test_ch03_01_exercise_1_predictions(scenario_truth: dict[str, str]) -> None:
    unanswered = [k for k, v in ex31.PREDICTIONS.items() if v is None]
    if unanswered:
        pytest.skip(f"练习 1 还有 {len(unanswered)} 条没填")
    wrong = [f"  {k:<44} 你写 {ex31.PREDICTIONS[k]!s:<20} 实际 {v}"
             for k, v in scenario_truth.items() if ex31.PREDICTIONS[k] != v]
    assert not wrong, "猜错的：\n" + "\n".join(wrong)


def test_ch03_01_exercise_2_find_shadowing(tmp_path: Path) -> None:
    run_or_skip(ex31.find_shadowing, tmp_path)
    check_find_shadowing(ex31.find_shadowing, tmp_path)


def test_ch03_01_exercise_3_module_imports() -> None:
    got = run_or_skip(ex31.module_imports, IMPORT_SOURCE)
    missing, extra = IMPORT_EXPECTED - got, got - IMPORT_EXPECTED
    assert not missing, f"漏掉了：{sorted(missing)}"
    assert not extra, f"多算了（函数体里的、相对导入的不该算）：{sorted(extra)}"


@pytest.mark.parametrize("graph", CYCLE_GRAPHS)
def test_ch03_01_exercise_4_find_cycle(graph: dict[str, set[str]]) -> None:
    assert_valid_cycle(graph, run_or_skip(ex31.find_cycle, graph))


@pytest.mark.parametrize("graph", ACYCLIC_GRAPHS)
def test_ch03_01_exercise_4_find_no_cycle(graph: dict[str, set[str]]) -> None:
    assert run_or_skip(ex31.find_cycle, graph) is None


# ============================================================================
# 3.2 · 示例
# ============================================================================


def actual_repr_in(namespace: dict[str, Any], expr: str) -> str:
    try:
        return repr(eval(expr, namespace))
    except Exception as e:  # noqa: BLE001
        return type(e).__name__


@pytest.mark.parametrize("expr", list(sol32.PREDICTIONS))
def test_ch03_02_solution_predictions(expr: str) -> None:
    assert sol32.PREDICTIONS[expr] == actual_repr_in(vars(example32), expr)


def test_ch03_02_game_rules() -> None:
    game = example32.GuessGame(42, max_attempts=3)
    assert [game.guess(50), game.guess(10)] == ["大了", "小了"]
    assert (game.remaining, game.won, game.is_over) == (1, False, False)
    assert game.guess(42) == "正确"
    assert (game.won, game.is_over) == (True, True)
    with pytest.raises(example32.GameOverError):
        game.guess(1)
    assert game.history == [50, 10, 42], "结束后再猜不该被记录"


def test_ch03_02_game_runs_out() -> None:
    game = example32.GuessGame(42, max_attempts=2)
    game.guess(1)
    game.guess(2)
    assert game.is_over and not game.won
    with pytest.raises(example32.GameOverError):
        game.guess(42)


def test_ch03_02_instances_do_not_share_history() -> None:
    a, b = example32.GuessGame(1), example32.GuessGame(2)
    a.guess(5)
    assert b.history == []


def test_ch03_02_class_attribute_outlives_objects() -> None:
    """讲解第 4 节：类属性上的数据比创建它的对象活得久，跨调用累积。"""
    example32.Shared.history = []
    for _ in range(3):
        example32.Shared().add(1)          # 每次都是一个新对象，用完就丢
    assert example32.Shared.history == [1, 1, 1]
    assert example32.shared_after_other_add() == [1]
    assert example32.shared_after_other_add() == [1], "示例函数每次先清空，结果才稳定"


def test_ch03_02_repr_hides_target() -> None:
    text = repr(example32.GuessGame(73))
    assert "73" not in text
    assert text == "GuessGame(range=1-100, attempts=0/7, won=False)"


def test_ch03_02_classmethod_constructor() -> None:
    g1 = example32.GuessGame.with_random_target(seed=42)
    g2 = example32.GuessGame.with_random_target(seed=42)
    assert isinstance(g1, example32.GuessGame)
    assert g1.target == g2.target
    small = example32.GuessGame.with_random_target(seed=1, low=1, high=3, max_attempts=2)
    assert 1 <= small.target <= 3 and small.max_attempts == 2


def run_play(answers: list[str], game: example32.GuessGame) -> list[str]:
    it = iter(answers)
    lines: list[str] = []
    example32.play(game, ask=lambda _prompt: next(it), say=lines.append)
    return lines


def test_ch03_02_play_win() -> None:
    lines = run_play(["abc", "200", "50", "42"], example32.GuessGame(42))
    assert "   'abc' 不是整数，这次不算" in lines
    assert "   200 不在 1-100 之间，这次不算" in lines
    assert "    50 → 大了" in lines
    assert lines[-1] == "   用了 2 次。"


def test_ch03_02_play_lose_and_quit() -> None:
    lost = run_play(["1", "2"], example32.GuessGame(42, max_attempts=2))
    assert lost[-1] == "   机会用完了，答案是 42。"
    quit_ = run_play(["q"], example32.GuessGame(42))
    assert quit_[-1] == "不玩了。"


def test_ch03_02_mypy_misses_typo_but_not_slots(tmp_path: Path) -> None:
    """讲解第 5 节：方法里拼错属性名，mypy 不报；用了 slots 才报。没调 super().__init__ 也不报。"""
    src = tmp_path / "typo.py"
    src.write_text(
        "from dataclasses import dataclass\n"
        "class Typo:\n"
        "    def __init__(self) -> None:\n        self.attempts = 0\n"
        "    def bump(self) -> None:\n        self.atempts = self.attempts + 1\n"   # 第 6 行
        "@dataclass(slots=True)\n"
        "class Slotted:\n"
        "    attempts: int = 0\n"
        "    def bump(self) -> None:\n        self.atempts = self.attempts + 1\n"   # 第 11 行
        "class Base:\n"
        "    def __init__(self) -> None:\n        self.history: list[int] = []\n"
        "class NoSuper(Base):\n"
        "    def __init__(self) -> None:\n        self.hint = True\n"
        "    def size(self) -> int:\n        return len(self.history)\n",
        encoding="utf-8",
    )
    done = subprocess.run(
        [sys.executable, "-m", "mypy", str(src), "--no-incremental", "--no-error-summary"],
        cwd=tmp_path, capture_output=True, text=True, check=False)
    errors = done.stdout.strip().splitlines()
    assert len(errors) == 1, done.stdout
    assert ':11: error: Trying to assign name "atempts" that is not in "__slots__"' in errors[0]


def test_ch03_02_example_runs() -> None:
    done = run_python(CODE_DIR, "-m", "m03_structure.ch03_02_example")
    assert done.returncode == 0, done.stderr
    assert "TypeError: unhashable type: 'Point'" in done.stdout


# ============================================================================
# 3.2 · 参考答案与练习共用的检查
# ============================================================================


def check_scoreboard(cls: Callable[..., Any]) -> None:
    board = cls()
    board.add("张三", 5, True)
    board.add("李四", 7, False)
    board.add("张三", 3, True)
    board.add("张三", 2, False)
    assert len(board) == 4
    assert board.best("张三") == 3, "只看赢了的局"
    assert board.best("李四") is None, "没赢过要返回 None"
    assert board.best("王五") is None, "没玩过要返回 None"
    assert board.players == sorted(["张三", "李四"])
    other = cls()
    assert len(other) == 0 and other.players == [], "两个记分板共用了数据 —— 列表是不是写成了类属性？"


def check_hint_game(cls: Callable[..., Any], base: type, game_over: type[Exception]) -> None:
    assert isinstance(cls(42), base), "要继承 GuessGame"
    game = cls(42, 7, 1, 100, 2)
    assert game.guess(50) == "大了"
    assert game.guess(10) == "小了"
    assert game.guess(30) == "小了（提示：答案在 31-49 之间）"
    assert game.guess(60) == "大了（提示：答案在 31-49 之间）", "范围只会变窄"
    assert game.guess(42) == "正确"
    assert game.history == [50, 10, 30, 60, 42], "history 要沿用父类的"
    with pytest.raises(game_over):
        game.guess(1)

    default = cls(42)
    results = [default.guess(n) for n in (1, 2, 3, 4)]
    assert results[:3] == ["小了"] * 3, "hint_after 默认是 3"
    assert results[3] == "小了（提示：答案在 5-100 之间）"

    short = cls(42, 2, 1, 100, 0)
    short.guess(1)
    short.guess(2)
    with pytest.raises(game_over):
        short.guess(3)


TOP_RECORDS = [("张三", 5, True), ("李四", 3, True), ("张三", 5, True), ("王五", 2, False),
               ("赵六", 3, True), ("钱七", 9, True)]


def check_top(record_cls: Callable[..., Any], top: Callable[..., list[Any]]) -> None:
    records = [record_cls(*r) for r in TOP_RECORDS]
    result = top(records)
    assert [(r.player, r.attempts) for r in result] == [("李四", 3), ("赵六", 3), ("张三", 5)]
    assert all(type(r) is record_cls for r in result)
    assert len(top(records, 10)) == 4, "重复的记录只算一条，输了的不算"
    assert top([]) == []
    assert repr(record_cls("张三", 5, True)) == "GameRecord(player='张三', attempts=5, won=True)"


def test_ch03_02_solution_scoreboard() -> None:
    check_scoreboard(sol32.Scoreboard)


def test_ch03_02_solution_hint_game() -> None:
    check_hint_game(sol32.HintGame, example32.GuessGame, example32.GameOverError)


def test_ch03_02_solution_top() -> None:
    check_top(sol32.GameRecord, sol32.top)


# ============================================================================
# 3.2 · 练习
# ============================================================================


def test_ch03_02_exercise_1_predictions() -> None:
    unanswered = [k for k, v in ex32.PREDICTIONS.items() if v is None]
    if unanswered:
        pytest.skip(f"练习 1 还有 {len(unanswered)} 条没填")
    ns = vars(example32)
    wrong = [f"  {k:<44} 你写 {v!s:<16} 实际 {actual_repr_in(ns, k)}"
             for k, v in ex32.PREDICTIONS.items() if v != actual_repr_in(ns, k)]
    assert not wrong, "猜错的：\n" + "\n".join(wrong)


def test_ch03_02_exercise_2_scoreboard() -> None:
    run_or_skip(ex32.Scoreboard)
    check_scoreboard(ex32.Scoreboard)


def test_ch03_02_exercise_3_hint_game() -> None:
    run_or_skip(ex32.HintGame, 42)
    check_hint_game(ex32.HintGame, example32.GuessGame, example32.GameOverError)


def test_ch03_02_exercise_4_top() -> None:
    if not dataclasses.is_dataclass(ex32.GameRecord):
        pytest.skip("练习 4 还没完成（GameRecord 还不是 dataclass）")
    run_or_skip(ex32.top, [])
    check_top(ex32.GameRecord, ex32.top)


# ============================================================================
# 3.3 · 分层（精简版章节：只有示例和验证结论的测试，没有练习）
# ============================================================================

def test_ch03_03_dependency_direction() -> None:
    """讲解第 2 节：只能上层导入下层。"""
    graph = example33.internal_graph()
    assert graph == {"__main__": {"cli", "rules"}, "cli": {"errors", "rules"},
                     "rules": {"errors"}, "errors": set()}
    assert example33.upward_imports(graph) == []
    assert sol31.find_cycle(graph) is None


def test_ch03_03_upward_import_is_detected() -> None:
    """对照：如果 rules 导入了 cli，检查能发现。"""
    graph = {**example33.internal_graph(), "rules": {"errors", "cli"}}
    assert example33.upward_imports(graph) == [("rules", "cli")]


def test_ch03_03_no_direct_io_anywhere() -> None:
    """讲解第 3 节：没有任何模块直接调用 input/print；cli 只把它们当默认值。"""
    assert example33.io_calls() == {}
    assert example33.io_defaults() == {
        "cli": ["play() 的默认值用了 input", "play() 的默认值用了 print"]}


def test_ch03_03_package_init_imports_nothing() -> None:
    init = (example33.GUESS_DIR / "__init__.py").read_text(encoding="utf-8")
    assert sol31.module_imports(init) == set()


def test_ch03_03_bisect_player_always_wins() -> None:
    """讲解第 4 节：二分法 7 次以内必中（2**7 = 128 > 100），只用到 rules 层。"""
    attempts = [len(example33.bisect_player(guess_rules.GuessGame(t))) for t in range(1, 101)]
    assert max(attempts) == 7
    assert all(guess_rules.GuessGame(t).max_attempts >= a for t, a in enumerate(attempts, 1))


def test_ch03_03_run_package_with_dash_m() -> None:
    """python -m 包名 运行的是包里的 __main__.py；__init__.py 为空，所以没有「执行两次」的警告。"""
    target = guess_rules.GuessGame.with_random_target(1).target
    done = subprocess.run(
        [sys.executable, "-m", "m03_structure.guess", "1"], cwd=CODE_DIR,
        input=f"abc\n{target}\n", capture_output=True, text=True, encoding="utf-8",
        env={**os.environ, "PYTHONUTF8": "1"}, check=False)
    assert done.returncode == 0, done.stderr
    assert "'abc' 不是整数，这次不算" in done.stdout
    assert "用了 1 次。" in done.stdout
    assert "RuntimeWarning" not in done.stderr


def test_ch03_03_example_runs() -> None:
    done = run_python(CODE_DIR, "-m", "m03_structure.ch03_03_example")
    assert done.returncode == 0, done.stderr
    assert "反向依赖： 没有" in done.stdout
