"""M4 每日一题的测试。

    pytest tests/test_m04.py -k p01 -v

每道题的测试同时跑在你的练习（exercise）和参考答案（solution）上。
练习还没做时显示 skip。
"""

from __future__ import annotations

import ast
import contextlib
import json
import logging
import os
import re
import subprocess
import sys
from collections.abc import Callable, Iterator
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest

from m03_structure.guess.rules import GuessGame
from m04_persistence import (
    p01_scoreboard_exercise,
    p01_scoreboard_solution,
    p02_saves_exercise,
    p02_saves_solution,
    p03_validate_exercise,
    p03_validate_solution,
    p04_entry_exercise,
    p04_entry_solution,
    p04_load_exercise,
    p04_load_solution,
    p05_result_exercise,
    p05_result_solution,
)

CODE_DIR = Path(__file__).resolve().parents[1]


def run_or_skip(fn: Callable[..., Any], *args: Any) -> Any:
    try:
        return fn(*args)
    except NotImplementedError:
        pytest.skip(f"{fn.__name__} 还没完成")


# ============================================================================
# 第 1 题 · 排行榜存盘
# ============================================================================

P01 = {"exercise": p01_scoreboard_exercise, "solution": p01_scoreboard_solution}


@pytest.fixture(params=list(P01))
def p01(request: pytest.FixtureRequest) -> ModuleType:
    return P01[request.param]


def test_p01_round_trip(p01: ModuleType, tmp_path: Path) -> None:
    path = tmp_path / "scores.txt"
    run_or_skip(p01.save_scores, path, {"张三": 5, "李四": 3, "欧阳修文": 7})
    assert path.read_text(encoding="utf-8") == "李四,3\n张三,5\n欧阳修文,7\n", "按次数从少到多排"
    assert p01.load_scores(path) == {"张三": 5, "李四": 3, "欧阳修文": 7}


def test_p01_accepts_str_path(p01: ModuleType, tmp_path: Path) -> None:
    path = str(tmp_path / "scores.txt")
    run_or_skip(p01.save_scores, path, {"张三": 5})
    assert p01.load_scores(path) == {"张三": 5}


def test_p01_missing_file(p01: ModuleType, tmp_path: Path) -> None:
    assert run_or_skip(p01.load_scores, tmp_path / "没有这个文件.txt") == {}


def test_p01_blank_lines_and_duplicates(p01: ModuleType, tmp_path: Path) -> None:
    path = tmp_path / "scores.txt"
    path.write_text("张三,5\n\n李四,3\n张三,2\n\n", encoding="utf-8")
    assert run_or_skip(p01.load_scores, path) == {"张三": 2, "李四": 3}


def test_p01_comma_in_name(p01: ModuleType, tmp_path: Path) -> None:
    path = tmp_path / "scores.txt"
    run_or_skip(p01.save_scores, path, {"张,三": 4})
    assert p01.load_scores(path) == {"张,三": 4}, "名字里有逗号：试试 rsplit(',', 1)"


def test_p01_add_score(p01: ModuleType, tmp_path: Path) -> None:
    path = tmp_path / "new.txt"
    run_or_skip(p01.add_score, path, "张三", 6)
    p01.add_score(path, "李四", 4)
    p01.add_score(path, "张三", 3)
    assert path.read_text(encoding="utf-8") == "张三,6\n李四,4\n张三,3\n"
    assert p01.load_scores(path) == {"张三": 3, "李四": 4}


class _BrokenScores(dict[str, int]):
    """遍历到第二条就出错的字典，模拟「写到一半程序崩了」。不管用哪种方式遍历都会出错。"""

    def __init__(self) -> None:
        super().__init__({"李四": 3, "王五": 4})

    def items(self) -> Iterator[tuple[str, int]]:  # type: ignore[override]
        yield "李四", 3
        raise RuntimeError("写到一半出错")

    def __iter__(self) -> Iterator[str]:
        yield "李四"
        raise RuntimeError("写到一半出错")

    def keys(self) -> Iterator[str]:  # type: ignore[override]
        return iter(self)


def test_p01_save_failure_keeps_old_file(p01: ModuleType, tmp_path: Path) -> None:
    """要求 4：保存中途出错时，原来的文件内容不能丢。"""
    path = tmp_path / "scores.txt"
    path.write_text("张三,5\n", encoding="utf-8")
    with contextlib.suppress(RuntimeError):
        run_or_skip(p01.save_scores, path, _BrokenScores())
    assert path.read_text(encoding="utf-8") == "张三,5\n", (
        "保存失败后原文件被清空了。'w' 模式在打开文件的那一刻就清空了它 —— "
        "先把内容准备好再打开，或者写临时文件再替换")


def test_p01_encoding_is_explicit(p01: ModuleType, tmp_path: Path) -> None:
    """要求 5：每一处打开文件都写了 encoding。

    开一个子进程，关掉 UTF-8 模式（-X utf8=0），并把「没写 encoding」的警告变成错误。
    这样不管你的终端有没有设 PYTHONUTF8，漏写的地方都会暴露出来。
    """
    run_or_skip(p01.load_scores, tmp_path / "探测.txt")
    code = (
        f"from {p01.__name__} import save_scores, load_scores, add_score\n"
        "save_scores('s.txt', {'欧阳修文': 5})\n"
        "add_score('s.txt', '张三', 3)\n"
        "print(sorted(load_scores('s.txt').items()))\n"
    )
    out = run_strict_encoding(code, tmp_path)
    assert out == "[('张三', 3), ('欧阳修文', 5)]"
    (tmp_path / "s.txt").read_bytes().decode("utf-8")   # 文件本身必须是 UTF-8


def run_strict_encoding(code: str, cwd: Path) -> str:
    """关掉 UTF-8 模式、把「没写 encoding」的警告变成错误，跑一段代码，返回标准输出。"""
    env = {**os.environ, "PYTHONPATH": str(CODE_DIR), "PYTHONIOENCODING": "utf-8"}
    done = subprocess.run(
        [sys.executable, "-X", "utf8=0", "-X", "warn_default_encoding",
         "-W", "error::EncodingWarning", "-c", code],
        cwd=cwd, capture_output=True, text=True, encoding="utf-8", env=env, check=False)
    assert "EncodingWarning" not in done.stderr, (
        "有一处 open() 没写 encoding：\n" + done.stderr.strip().splitlines()[-1])
    assert done.returncode == 0, done.stderr
    return done.stdout.strip()


# --- 讲评里的实测结论 --------------------------------------------------------


def run_no_utf8(code: str, cwd: Path) -> subprocess.CompletedProcess[str]:
    """关掉 UTF-8 模式跑一段代码，复现 Windows 中文系统的默认行为。"""
    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    return subprocess.run([sys.executable, "-X", "utf8=0", "-c", code], cwd=cwd,
                          capture_output=True, text=True, encoding="utf-8", env=env, check=False)


needs_gbk = pytest.mark.skipif(
    run_no_utf8("import locale; print(locale.getpreferredencoding(False))", Path.cwd())
    .stdout.strip() != "cp936",
    reason="只在默认编码是 cp936（中文 Windows）的机器上复现")


@needs_gbk
def test_p01_review_gbk_mojibake_and_error(tmp_path: Path) -> None:
    """讲评坑 1：UTF-8 文件不写 encoding 读 —— 有时乱码不报错，有时报错。"""
    (tmp_path / "a.txt").write_text("张三,3\n", encoding="utf-8")
    (tmp_path / "b.txt").write_text("欧阳修文,5\n", encoding="utf-8")
    quiet = run_no_utf8("print(repr(open('a.txt').read()))", tmp_path)
    assert quiet.returncode == 0 and quiet.stdout.strip() == "'寮犱笁,3\\n'"
    loud = run_no_utf8("open('b.txt').read()", tmp_path)
    assert "UnicodeDecodeError: 'gbk' codec can't decode byte 0xae" in loud.stderr


def test_p01_review_w_mode_truncates(tmp_path: Path) -> None:
    """讲评坑 2：'w' 模式打开那一刻文件就清空了。"""
    path = tmp_path / "d.txt"
    path.write_text("张三,3\n", encoding="utf-8")
    with pytest.raises(ValueError), open(path, "w", encoding="utf-8"):
        raise ValueError("写到一半出错")
    assert path.read_text(encoding="utf-8") == ""


@pytest.mark.skipif(os.name != "nt", reason="文件占用导致删不掉是 Windows 的行为")
def test_p01_review_unclosed_file(tmp_path: Path) -> None:
    """讲评坑 3：没关闭的文件，内容还在缓冲区里，而且 Windows 上删不掉。"""
    path = tmp_path / "e.txt"
    f = open(path, "w", encoding="utf-8")  # noqa: SIM115 —— 故意不用 with
    f.write("张三,3\n")
    assert path.stat().st_size == 0
    with pytest.raises(PermissionError):
        path.unlink()
    f.close()
    # Windows 的文本模式会把 \n 写成 \r\n，所以是 10 字节而不是 9 字节
    assert path.stat().st_size == len("张三,3\r\n".encode())
    assert path.read_bytes().endswith(b"\r\n")
    assert path.read_text(encoding="utf-8") == "张三,3\n", "读回来时 \\r\\n 又被换回了 \\n"


# ============================================================================
# 第 2 题 · JSON 存档
# ============================================================================

P02 = {"exercise": p02_saves_exercise, "solution": p02_saves_solution}


@pytest.fixture(params=list(P02))
def p02(request: pytest.FixtureRequest) -> ModuleType:
    return P02[request.param]


def record(player: str, target: int, history: list[int]) -> dict[str, object]:
    return {"player": player, "target": target, "history": history,
            "won": bool(history) and history[-1] == target}


def finished_game(target: int, guesses: list[int]) -> GuessGame:
    game = GuessGame(target)
    for n in guesses:
        game.guess(n)
    return game


def test_p02_round_trip_keeps_int_keys(p02: ModuleType, tmp_path: Path) -> None:
    path = tmp_path / "games.json"
    games = {1: record("张三", 42, [50, 42]), 2: record("李四", 7, [1, 2])}
    run_or_skip(p02.save_games, path, games)
    loaded = p02.load_games(path)
    assert list(loaded) == [1, 2], f"局号要是 int，读回来的是 {list(loaded)!r}"
    assert loaded == games


def test_p02_file_is_readable(p02: ModuleType, tmp_path: Path) -> None:
    """要求 1：打开文件能直接看懂 —— 中文原样写，有缩进。"""
    path = tmp_path / "games.json"
    run_or_skip(p02.save_games, path, {1: record("张三", 42, [42])})
    text = path.read_text(encoding="utf-8")
    assert "张三" in text, "文件里是 \\u5f20\\u4e09 这样的转义 —— 看看 json.dumps 的 ensure_ascii"
    assert "\n  " in text, "整个文件挤在一行 —— 看看 json.dumps 的 indent"
    assert json.loads(text) == {"1": record("张三", 42, [42])}


def test_p02_missing_file(p02: ModuleType, tmp_path: Path) -> None:
    assert run_or_skip(p02.load_games, tmp_path / "没有这个文件.json") == {}


def test_p02_add_game(p02: ModuleType, tmp_path: Path) -> None:
    path = tmp_path / "games.json"
    first = run_or_skip(p02.add_game, path, "张三", finished_game(42, [50, 42]))
    second = p02.add_game(path, "李四", finished_game(7, [1, 2]))
    assert (first, second) == (1, 2)
    assert p02.load_games(path) == {1: record("张三", 42, [50, 42]), 2: record("李四", 7, [1, 2])}


def test_p02_add_game_after_nine(p02: ModuleType, tmp_path: Path) -> None:
    """要求 3：存档里已经有 1-9 局，新的一局必须是 10，再下一局是 11。"""
    path = tmp_path / "games.json"
    path.write_text(json.dumps({str(i): record("张三", 1, [1]) for i in range(1, 10)}),
                    encoding="utf-8")
    first = run_or_skip(p02.add_game, path, "李四", finished_game(5, [5]))
    second = p02.add_game(path, "王五", finished_game(6, [6]))
    assert (first, second) == (10, 11), (
        f"拿到的局号是 {first} 和 {second}。如果第二局覆盖了第一局，"
        "检查一下你是不是在字符串局号上取了 max —— max(['9', '10']) 是 '9'")
    assert len(p02.load_games(path)) == 11


def test_p02_save_failure_keeps_old_file(p02: ModuleType, tmp_path: Path) -> None:
    """要求 4：记录里有存不进 JSON 的东西时，原存档不能被写坏。"""
    path = tmp_path / "games.json"
    old = json.dumps({"1": record("张三", 42, [42])}, ensure_ascii=False, indent=2)
    path.write_text(old, encoding="utf-8")
    bad = {1: record("张三", 42, [42]), 2: {"player": "李四", "tags": {"新手"}}}
    with pytest.raises(TypeError):
        run_or_skip(p02.save_games, path, bad)
    assert path.read_text(encoding="utf-8") == old, (
        "存档被写坏了。json.dump 是边转换边写文件的，转换到一半出错时文件里已经是半截 JSON")


def test_p02_load_file_with_bom(p02: ModuleType, tmp_path: Path) -> None:
    """要求 5：Windows 记事本、PowerShell 5.1 写出的 UTF-8 文件开头可能带 BOM。"""
    path = tmp_path / "games.json"
    path.write_bytes(b"\xef\xbb\xbf" + json.dumps({"1": record("张三", 42, [42])},
                                                  ensure_ascii=False).encode("utf-8"))
    assert run_or_skip(p02.load_games, path) == {1: record("张三", 42, [42])}


def test_p02_encoding_is_explicit(p02: ModuleType, tmp_path: Path) -> None:
    run_or_skip(p02.load_games, tmp_path / "探测.json")
    code = (
        f"from {p02.__name__} import save_games, load_games, add_game\n"
        "from m03_structure.guess.rules import GuessGame\n"
        "g = GuessGame(42)\ng.guess(42)\n"
        "add_game('g.json', '欧阳修文', g)\n"
        "print(load_games('g.json')[1]['player'])\n"
    )
    assert run_strict_encoding(code, tmp_path) == "欧阳修文"


# --- 讲评里的实测结论 --------------------------------------------------------


def test_p02_review_json_facts() -> None:
    assert json.loads(json.dumps({1: "a"})) == {"1": "a"}
    assert json.dumps({1: "a", "1": "b"}) == '{"1": "a", "1": "b"}', "两个键都写进去了"
    assert json.loads('{"1": "a", "1": "b"}') == {"1": "b"}, "读回来后一个覆盖前一个"
    assert json.loads(json.dumps({"h": (50, 25)})) == {"h": [50, 25]}
    assert json.dumps({True: 1, None: 2}) == '{"true": 1, "null": 2}'
    assert json.dumps({"p": "张三"}) == '{"p": "\\u5f20\\u4e09"}'
    assert max(["9", "10", "2"]) == "9"
    with pytest.raises(TypeError, match="Object of type set is not JSON serializable"):
        json.dumps({1, 2})
    with pytest.raises(json.JSONDecodeError, match="Unexpected UTF-8 BOM"):
        json.loads("\ufeff{}")
    assert issubclass(json.JSONDecodeError, ValueError)


def test_p02_review_dump_writes_half_file(tmp_path: Path) -> None:
    """讲评坑 2：json.dump 边转换边写，中途出错留下半截 JSON。"""
    path = tmp_path / "games.json"
    with pytest.raises(TypeError), open(path, "w", encoding="utf-8") as f:
        json.dump({"1": {"player": "李四"}, "2": {"tags": {1}}}, f, ensure_ascii=False)
    assert path.read_text(encoding="utf-8") == '{"1": {"player": "李四"}, "2": {"tags": '
    with pytest.raises(json.JSONDecodeError):
        json.loads(path.read_text(encoding="utf-8"))


# ============================================================================
# 第 3 题 · 不信任读进来的数据
# ============================================================================

P03 = {"exercise": p03_validate_exercise, "solution": p03_validate_solution}


@pytest.fixture(params=list(P03))
def p03(request: pytest.FixtureRequest) -> ModuleType:
    return P03[request.param]


GOOD = '{"player": "张三", "target": 42, "history": [50, 42], "won": true}'


def with_field(field: str, value: str) -> str:
    """把 GOOD 里某个字段的值换成一段 JSON 文本。"""
    data = json.loads(GOOD)
    data[field] = "__X__"
    return json.dumps(data, ensure_ascii=False).replace('"__X__"', value)


# (用例名, 整个存档的 JSON 文本, 报错消息里必须出现的片段)
BAD_SAVES = [
    ("top_is_list", "[]", ["list"]),
    ("key_leading_zero", '{"01": ' + GOOD + "}", ["'01'"]),
    ("key_zero", '{"0": ' + GOOD + "}", ["'0'"]),
    ("key_fullwidth", '{"１": ' + GOOD + "}", ["'１'"]),
    ("key_word", '{"abc": ' + GOOD + "}", ["'abc'"]),
    ("record_is_list", '{"1": [1, 2]}', ["第 1 局"]),
    ("missing_won", '{"1": {"player": "张三", "target": 42, "history": [42]}}', ["第 1 局", "won"]),
    ("typo_field", '{"1": {"player": "张三", "target": 42, "histroy": [42], "history": [42], '
                   '"won": true}}', ["第 1 局", "histroy"]),
    ("player_empty", '{"1": ' + with_field("player", '""') + "}", ["player"]),
    ("target_true", '{"1": ' + with_field("target", "true") + "}", ["target", "True"]),
    ("target_float", '{"1": ' + with_field("target", "42.0") + "}", ["target", "42.0"]),
    ("target_101", '{"1": ' + with_field("target", "101") + "}", ["target", "101"]),
    ("target_nan", '{"1": ' + with_field("target", "NaN") + "}", ["target", "nan"]),
    ("history_str", '{"1": ' + with_field("history", '"50, 42"') + "}", ["history"]),
    ("history_bool", '{"1": ' + with_field("history", "[50, true]") + "}", ["history[1]"]),
    ("won_one", '{"1": ' + with_field("won", "1") + "}", ["won", "1"]),
    ("won_wrong", '{"1": ' + with_field("won", "false") + "}", ["won"]),
    ("second_bad", '{"1": ' + GOOD + ', "2": ' + with_field("target", "0") + "}",
     ["第 2 局", "target"]),
]


def test_p03_valid_save(p03: ModuleType) -> None:
    raw = json.loads('{"1": ' + GOOD + ', "10": {"player": "李四", "target": 7, '
                     '"history": [1, 2], "won": false}, "11": {"player": "王五", "target": 9, '
                     '"history": [], "won": false}}')
    games = run_or_skip(p03.parse_games, raw)
    assert list(games) == [1, 10, 11]
    assert games[1] == json.loads(GOOD)
    assert games[11]["history"] == [], "一次都没猜的局也是合法的"


def test_p03_empty_save(p03: ModuleType) -> None:
    assert run_or_skip(p03.parse_games, {}) == {}


@pytest.mark.parametrize(("text", "fragments"), [c[1:] for c in BAD_SAVES],
                         ids=[c[0] for c in BAD_SAVES])
def test_p03_rejects_bad_save(p03: ModuleType, text: str, fragments: list[str]) -> None:
    raw = json.loads(text)
    run_or_skip(p03.parse_games, {})
    with pytest.raises(p03.SaveFormatError) as excinfo:
        p03.parse_games(raw)
    message = str(excinfo.value)
    missing = [f for f in fragments if f not in message]
    assert not missing, f"报错消息里应该提到 {missing}，实际消息：{message!r}"


def test_p03_error_is_value_error(p03: ModuleType) -> None:
    assert issubclass(p03.SaveFormatError, ValueError)


def test_p03_load_bad_json(p03: ModuleType, tmp_path: Path) -> None:
    """要求 5：JSON 语法错误也要变成 SaveFormatError，并保留原来的 JSONDecodeError。"""
    path = tmp_path / "games.json"
    path.write_text('{"1": {"player": "李四"}, "2": {"tags": ', encoding="utf-8")
    run_or_skip(p03.load_games, tmp_path / "没有.json")
    with pytest.raises(p03.SaveFormatError) as excinfo:
        p03.load_games(path)
    assert "games.json" in str(excinfo.value), "消息里要写出是哪个文件"
    assert isinstance(excinfo.value.__cause__, json.JSONDecodeError), (
        "原来的 JSONDecodeError 丢了 —— raise ... from e")


def test_p03_load_missing_and_bom(p03: ModuleType, tmp_path: Path) -> None:
    assert run_or_skip(p03.load_games, tmp_path / "没有.json") == {}
    path = tmp_path / "games.json"
    path.write_bytes(b"\xef\xbb\xbf" + ('{"1": ' + GOOD + "}").encode("utf-8"))
    assert p03.load_games(path) == {1: json.loads(GOOD)}


def test_p03_load_validates(p03: ModuleType, tmp_path: Path) -> None:
    path = tmp_path / "games.json"
    path.write_text('{"1": ' + with_field("won", "1") + "}", encoding="utf-8")
    run_or_skip(p03.load_games, tmp_path / "没有.json")
    with pytest.raises(p03.SaveFormatError, match="won"):
        p03.load_games(path)


def test_p03_encoding_is_explicit(p03: ModuleType, tmp_path: Path) -> None:
    run_or_skip(p03.load_games, tmp_path / "探测.json")
    (tmp_path / "g.json").write_text('{"1": ' + GOOD.replace("张三", "欧阳修文") + "}",
                                     encoding="utf-8")
    code = (f"from {p03.__name__} import load_games\n"
            "print(load_games('g.json')[1]['player'])\n")
    assert run_strict_encoding(code, tmp_path) == "欧阳修文"


# --- 讲评里的实测结论 --------------------------------------------------------


def test_p03_review_bool_is_int() -> None:
    value: object = True
    assert isinstance(value, int) and type(value) is not int
    assert (1 <= True <= 100) is True
    assert 1 in (True, False), "won in (True, False) 会放过 1"
    assert isinstance(1, bool) is False
    # 答案存成 true，猜 1 就算猜中。GuessGame 的参数注解是 int，bool 是它的子类，mypy 也不拦
    game = GuessGame(True)
    assert game.guess(1) == "正确"


def test_p03_review_or_precedence() -> None:
    """讲评坑 5：Day14 的 `100 < item | item < 1` 永远不成立；`| bool` 的变体永远成立。"""
    for item in (0, 1, 50, 100, 101, 10000):
        assert (100 < item | item < 1) is False
    assert [not 1 <= n <= 100 for n in (0, 101, 10000)] == [True, True, True]
    for value in (1, True, "x", None):
        assert (type(value) is not int | bool) is True


def test_p03_review_keys_collapse() -> None:
    assert {int(k): v for k, v in {"1": "a", "01": "b"}.items()} == {1: "b"}
    assert (int("01"), int(" 1"), int("１")) == (1, 1, 1)
    assert "１".isdecimal() and not "１".isascii()


def test_p03_review_nan_passes_json() -> None:
    target = json.loads('{"t": NaN}')["t"]
    assert target != target, "NaN 不等于它自己"
    assert not (1 <= target <= 100), "范围检查能拦住 NaN"
    assert not isinstance(target, int)


# ============================================================================
# 第 4 题 · 用日志代替 print
# ============================================================================

P04_LOAD = {"exercise": p04_load_exercise, "solution": p04_load_solution}
P04_ENTRY = {"exercise": p04_entry_exercise, "solution": p04_entry_solution}


@pytest.fixture(params=list(P04_LOAD))
def p04(request: pytest.FixtureRequest) -> ModuleType:
    return P04_LOAD[request.param]


@pytest.fixture(params=list(P04_ENTRY))
def p04_entry(request: pytest.FixtureRequest) -> ModuleType:
    return P04_ENTRY[request.param]


MIXED_SAVE = ('{"1": ' + GOOD + ', "01": ' + GOOD + ', "2": ' + with_field("won", "1")
              + ', "3": ' + GOOD.replace("张三", "李四") + "}")


def load_with_log(p04: ModuleType, path: Path, caplog: pytest.LogCaptureFixture) -> Any:
    caplog.set_level(logging.DEBUG, logger=p04.__name__)
    return run_or_skip(p04.load_games_lenient, path)


def test_p04_module_logger(p04: ModuleType) -> None:
    """要求 1：模块级的 logger，名字是模块的完整路径。"""
    logger = getattr(p04, "logger", None)
    if logger is None:
        pytest.skip("还没有创建 logger")
    assert isinstance(logger, logging.Logger)
    assert logger.name == p04.__name__, f"用 getLogger(__name__)，现在的名字是 {logger.name!r}"


def test_p04_module_does_not_configure_or_print(p04: ModuleType) -> None:
    """要求 1：业务模块里不 print、不 basicConfig、不加 handler。"""
    assert p04.__file__ is not None
    tree = ast.parse(Path(p04.__file__).read_text(encoding="utf-8"))
    calls = {node.func.attr if isinstance(node.func, ast.Attribute) else getattr(node.func, "id", "")
             for node in ast.walk(tree) if isinstance(node, ast.Call)}
    banned = calls & {"print", "basicConfig", "addHandler", "setLevel"}
    assert not banned, f"业务模块里出现了 {sorted(banned)} —— 配置日志是入口的事"


def test_p04_skips_bad_games(p04: ModuleType, tmp_path: Path,
                             caplog: pytest.LogCaptureFixture) -> None:
    """要求 2：坏的局跳过，每局一条 WARNING，写出局号和原因。"""
    path = tmp_path / "games.json"
    path.write_text(MIXED_SAVE, encoding="utf-8")
    games = load_with_log(p04, path, caplog)
    assert sorted(games) == [1, 3]
    warnings = [r for r in caplog.records if r.levelno == logging.WARNING]
    assert len(warnings) == 2, f"跳过了 2 局，应该有 2 条 WARNING，实际 {len(warnings)} 条"
    text = "\n".join(r.getMessage() for r in warnings)
    assert "01" in text, "局号不对的那一局，消息里要写出局号"
    assert "won" in text, "记录不合法的那一局，消息里要写出原因（parse_record 抛的异常消息）"


def test_p04_uses_lazy_args(p04: ModuleType, tmp_path: Path,
                            caplog: pytest.LogCaptureFixture) -> None:
    """要求 3：参数交给 logging，而不是先用 f-string 拼好。"""
    path = tmp_path / "games.json"
    path.write_text(MIXED_SAVE, encoding="utf-8")
    load_with_log(p04, path, caplog)
    mine = [r for r in caplog.records if r.name == p04.__name__]
    others = sorted({r.name for r in caplog.records})
    assert mine, f"没有找到 logger {p04.__name__!r} 记的日志，实际记日志的 logger 是 {others}"
    pre_formatted = [r.getMessage() for r in mine if not r.args]
    assert not pre_formatted, f"这些日志是先拼好字符串再传进去的：{pre_formatted}"


def test_p04_summary(p04: ModuleType, tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    """要求 4：读完记一条 INFO 汇总。"""
    path = tmp_path / "games.json"
    path.write_text(MIXED_SAVE, encoding="utf-8")
    load_with_log(p04, path, caplog)
    infos = [r.getMessage() for r in caplog.records if r.levelno == logging.INFO]
    assert "读取 games.json：2 局，跳过 2 局" in infos, (
        f"实际的 INFO：{infos}。如果是空的，先看 test_p04_module_logger 过了没有 —— "
        "logger 名字不对时，测试只把 WARNING 及以上收进来")


def test_p04_missing_file(p04: ModuleType, tmp_path: Path,
                          caplog: pytest.LogCaptureFixture) -> None:
    assert load_with_log(p04, tmp_path / "games.json", caplog) == {}
    records = [r for r in caplog.records if r.name == p04.__name__]
    assert [r.levelname for r in records] == ["INFO"], "文件不存在是正常情况，记一条 INFO 就够了"
    assert "games.json" in records[0].getMessage()


@pytest.mark.parametrize("text", ['{"1": ', "[]"], ids=["broken_json", "top_is_list"])
def test_p04_whole_file_bad_still_raises(p04: ModuleType, tmp_path: Path, text: str) -> None:
    """整个文件都坏了，没法「跳过一部分」，照样抛 SaveFormatError。"""
    path = tmp_path / "games.json"
    path.write_text(text, encoding="utf-8")
    run_or_skip(p04.load_games_lenient, tmp_path / "没有.json")
    with pytest.raises(p04.SaveFormatError):
        p04.load_games_lenient(path)


def test_p04_no_print(p04: ModuleType, tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    path = tmp_path / "games.json"
    path.write_text(MIXED_SAVE, encoding="utf-8")
    run_or_skip(p04.load_games_lenient, path)
    out = capsys.readouterr()
    assert out.out == "", f"标准输出里出现了 {out.out!r} —— 用日志，不要 print"


# setup_logging 必须在子进程里测：pytest 自己在根 logger 上装了 handler，
# 在这个进程里调 basicConfig(force=True) 会把它们拆掉，后面的测试就收不到日志了。

def run_entry(p04_entry: ModuleType, body: str, cwd: Path,
              strict_encoding: bool = False) -> subprocess.CompletedProcess[str]:
    code = (f"import logging\nfrom {p04_entry.__name__} import setup_logging\n"
            "log = logging.getLogger('m04_persistence.demo')\n" + body)
    flags = ["-X", "utf8=0", "-X", "warn_default_encoding", "-W", "error::EncodingWarning"] \
        if strict_encoding else []
    env = {**os.environ, "PYTHONPATH": str(CODE_DIR), "PYTHONIOENCODING": "utf-8"}
    return subprocess.run([sys.executable, *flags, "-c", code], cwd=cwd, capture_output=True,
                          text=True, encoding="utf-8", env=env, check=False)


def entry_or_skip(p04_entry: ModuleType, done: subprocess.CompletedProcess[str]) -> None:
    if "NotImplementedError" in done.stderr:
        pytest.skip("setup_logging 还没完成")
    assert done.returncode == 0, done.stderr


def test_p04_setup_console(p04_entry: ModuleType, tmp_path: Path) -> None:
    """要求 5：输出到标准错误，格式是 CONSOLE_FORMAT，级别按参数。"""
    done = run_entry(p04_entry, "setup_logging('INFO')\nlog.debug('看不到')\nlog.info('读取存档')\n",
                     tmp_path)
    entry_or_skip(p04_entry, done)
    assert done.stdout == "", "日志要输出到标准错误，标准输出留给程序的结果"
    assert done.stderr.strip() == "INFO m04_persistence.demo: 读取存档"


def test_p04_setup_twice(p04_entry: ModuleType, tmp_path: Path) -> None:
    """要求 5：调两次，第二次的级别生效，每条日志也只出现一次。"""
    done = run_entry(p04_entry, "setup_logging('INFO')\nsetup_logging('DEBUG')\n"
                     "log.debug('第二次配置生效了')\nlog.info('只出现一次')\n", tmp_path)
    entry_or_skip(p04_entry, done)
    assert "第二次配置生效了" in done.stderr, (
        "第二次 setup_logging('DEBUG') 没有生效 —— basicConfig 默认只在第一次调用时起作用")
    assert done.stderr.count("只出现一次") == 1, f"同一条日志出现了多次：\n{done.stderr}"


def test_p04_setup_logfile(p04_entry: ModuleType, tmp_path: Path) -> None:
    """要求 5：同时写文件，UTF-8，带时间。关掉 UTF-8 模式，检查有没有漏写 encoding。"""
    done = run_entry(p04_entry, "setup_logging('INFO', 'game.log')\n"
                     "log.warning('跳过第 %s 局', '欧阳修文')\nlogging.shutdown()\n",
                     tmp_path, strict_encoding=True)
    if "EncodingWarning" in done.stderr:
        raise AssertionError("FileHandler 没写 encoding：\n" + done.stderr.strip().splitlines()[-1])
    entry_or_skip(p04_entry, done)
    line = (tmp_path / "game.log").read_bytes().decode("utf-8").strip()
    assert re.fullmatch(r"\d{4}-\d\d-\d\d \d\d:\d\d:\d\d,\d{3} WARNING m04_persistence\.demo: "
                        r"跳过第 欧阳修文 局", line), f"日志文件里的这一行格式不对：{line!r}"


def test_p04_entry_main(tmp_path: Path) -> None:
    """参考答案的入口：坏的局在 stderr 里有记录，结果在 stdout，日志文件里有同样的内容。"""
    (tmp_path / "games.json").write_text(MIXED_SAVE, encoding="utf-8")
    env = {**os.environ, "PYTHONPATH": str(CODE_DIR), "PYTHONUTF8": "1"}
    done = subprocess.run([sys.executable, "-m", "m04_persistence.p04_entry_solution",
                           "games.json"], cwd=tmp_path, capture_output=True, text=True,
                          encoding="utf-8", env=env, check=False)
    assert done.returncode == 0, done.stderr
    assert done.stdout.strip() == "读到 2 局"
    assert "WARNING m04_persistence.p04_load_solution: 跳过局号 '01'" in done.stderr
    assert "跳过第 2 局" in (tmp_path / "games.log").read_text(encoding="utf-8")


# --- 讲评里的实测结论 --------------------------------------------------------


def run_logging(code: str, *flags: str) -> subprocess.CompletedProcess[str]:
    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    return subprocess.run([sys.executable, *flags, "-c", code], capture_output=True, text=True,
                          encoding="utf-8", env=env, check=False)


def test_p04_review_basic_config_once() -> None:
    done = run_logging(
        "import logging\n"
        "logging.basicConfig(level=logging.WARNING, format='第一次 %(message)s')\n"
        "logging.basicConfig(level=logging.DEBUG, format='第二次 %(message)s')\n"
        "logging.getLogger('a').info('info')\nlogging.getLogger('a').warning('warning')\n"
        "logging.basicConfig(level=logging.DEBUG, format='force %(message)s', force=True)\n"
        "logging.getLogger('a').info('之后')\n")
    assert done.stderr.splitlines() == ["第一次 warning", "force 之后"]


def test_p04_review_duplicate_handler() -> None:
    done = run_logging(
        "import logging, sys\n"
        "for _ in range(2):\n"
        "    logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))\n"
        "logging.getLogger().setLevel(logging.INFO)\nlogging.getLogger('x').info('读取存档')\n")
    assert done.stdout.splitlines() == ["读取存档", "读取存档"]


def test_p04_review_wrong_arg_count_does_not_raise() -> None:
    done = run_logging("import logging\nlogging.getLogger('x').warning('第 %s 局：%s', 3)\n"
                       "print('程序还在跑')\n")
    assert done.returncode == 0 and done.stdout.strip() == "程序还在跑"
    assert "--- Logging error ---" in done.stderr
    assert "TypeError: not enough arguments for format string" in done.stderr


def test_p04_review_fstring_evaluated_even_if_filtered() -> None:
    calls: list[int] = []

    class Expensive:
        def __str__(self) -> str:
            calls.append(1)
            return "E"

    log = logging.getLogger("pe.review.lazy")
    log.setLevel(logging.WARNING)
    e = Expensive()
    log.debug(f"调试 {e}")
    assert len(calls) == 1, "f-string 在调用 debug 之前就已经求值了"
    log.debug("调试 %s", e)
    assert len(calls) == 1, "%s 的参数在被过滤时不会格式化"


def test_p04_review_exception_outside_except() -> None:
    done = run_logging("import logging\nlogging.basicConfig(format='%(levelname)s %(message)s')\n"
                       "logging.getLogger('x').exception('出错了')\n")
    assert done.stderr.splitlines() == ["ERROR 出错了", "NoneType: None"]


def test_p04_review_basic_config_inside_pytest_is_noop() -> None:
    """在 pytest 里，根 logger 上已经有 pytest 的 handler，basicConfig 什么都不做。"""
    root = logging.getLogger()
    before = list(root.handlers)
    assert before, "pytest 应该已经在根 logger 上装了 handler"
    logging.basicConfig(level=logging.DEBUG, format="自定义 %(message)s")
    assert root.handlers == before


def test_p04_review_filehandler_encoding(tmp_path: Path) -> None:
    done = run_logging("import logging\nlogging.FileHandler('a.log')\n",
                       "-X", "utf8=0", "-X", "warn_default_encoding", "-W", "error::EncodingWarning")
    assert "EncodingWarning: 'encoding' argument not specified" in done.stderr


# ============================================================================
# 第 5 题 · 该返回空值还是抛异常
# ============================================================================

P05 = {"exercise": p05_result_exercise, "solution": p05_result_solution}


@pytest.fixture(params=list(P05))
def p05(request: pytest.FixtureRequest) -> ModuleType:
    return P05[request.param]


def rec_json(player: str, target: int, history: list[int]) -> str:
    return json.dumps(record(player, target, history), ensure_ascii=False)


# 张三赢了两局（3 次、2 次），李四赢了一局（2 次），王五一局没赢
LEAGUE = ("{" + ", ".join([
    '"1": ' + rec_json("张三", 42, [50, 30, 42]),
    '"2": ' + rec_json("李四", 7, [9, 7]),
    '"3": ' + rec_json("王五", 5, [1, 2, 3, 4, 6, 7, 8]),
    '"4": ' + rec_json("张三", 9, [10, 9]),
]) + "}")


def write(tmp_path: Path, text: str) -> Path:
    path = tmp_path / "games.json"
    path.write_text(text, encoding="utf-8")
    return path


def test_p05_missing_file(p05: ModuleType, tmp_path: Path) -> None:
    result = run_or_skip(p05.load_save, tmp_path / "games.json")
    assert result == p05.LoadResult(found=False)


def test_p05_empty_save_is_not_missing(p05: ModuleType, tmp_path: Path) -> None:
    """要求 1：文件存在但里面没有一局，和文件不存在是两回事。"""
    result = run_or_skip(p05.load_save, write(tmp_path, "{}"))
    assert result.found is True and result.games == {} and result.skipped == {}


def test_p05_skipped_with_reasons(p05: ModuleType, tmp_path: Path) -> None:
    result = run_or_skip(p05.load_save, write(tmp_path, MIXED_SAVE))
    assert result.found is True
    assert sorted(result.games) == [1, 3]
    assert sorted(result.skipped) == ["01", "2"]
    assert "won" in result.skipped["2"], "跳过的原因要记下来（parse_record 抛的异常消息）"


@pytest.mark.parametrize("text", ['{"1": ', "[]"], ids=["broken_json", "top_is_list"])
def test_p05_whole_file_bad_raises(p05: ModuleType, tmp_path: Path, text: str) -> None:
    run_or_skip(p05.load_save, tmp_path / "没有.json")
    with pytest.raises(p05.SaveFormatError):
        p05.load_save(write(tmp_path, text))


def test_p05_unreadable_is_not_missing(p05: ModuleType, tmp_path: Path) -> None:
    """要求 1：路径是一个目录 —— 读不了，但不是「没有存档」，异常要原样抛出。"""
    folder = tmp_path / "games.json"
    folder.mkdir()
    run_or_skip(p05.load_save, tmp_path / "没有.json")
    try:
        result = p05.load_save(folder)
    except OSError as e:
        assert not isinstance(e, FileNotFoundError)
    else:
        pytest.fail(f"路径是个目录，却返回了 {result!r} —— 这会让程序以为还没有存档，"
                    "下一次保存时才在别的地方出错")


DESCRIBE_CASES = [
    ("missing", None, "还没有存档，从第 1 局开始"),
    ("empty", "{}", "存档是空的"),
    ("all_good", LEAGUE, "读到 4 局"),
    ("some_bad", MIXED_SAVE, "读到 2 局，跳过 2 局（01、2）"),
    ("all_bad", '{"1": ' + with_field("won", "1") + ', "x": {}}',
     "存档里的 2 局全都坏了（1、x），没有读到任何一局"),
]


@pytest.mark.parametrize(("text", "expected"), [c[1:] for c in DESCRIBE_CASES],
                         ids=[c[0] for c in DESCRIBE_CASES])
def test_p05_describe(p05: ModuleType, tmp_path: Path, text: str | None, expected: str) -> None:
    path = tmp_path / "games.json" if text is None else write(tmp_path, text)
    result = p05_result_solution.load_save(path)       # 用参考答案读，只测 describe
    got = run_or_skip(p05.describe, p05.LoadResult(result.games, result.skipped, result.found))
    assert got == expected


def test_p05_best_attempts(p05: ModuleType, tmp_path: Path) -> None:
    result = p05_result_solution.load_save(write(tmp_path, LEAGUE))
    mine = p05.LoadResult(result.games, result.skipped, result.found)
    assert run_or_skip(p05.best_attempts, mine, "张三") == 2
    assert p05.best_attempts(mine, "李四") == 2
    assert p05.best_attempts(mine, "王五") is None, "没赢过要返回 None，不是 0"
    assert p05.best_attempts(mine, "没玩过的人") is None


def test_p05_leaderboard(p05: ModuleType, tmp_path: Path) -> None:
    result = p05_result_solution.load_save(write(tmp_path, LEAGUE))
    mine = p05.LoadResult(result.games, result.skipped, result.found)
    board = run_or_skip(p05.leaderboard, mine)
    assert board == sorted([("张三", 2), ("李四", 2)]) + [("王五", None)], (
        f"实际：{board}。没赢过的要排在最后")
    assert run_or_skip(p05.leaderboard, p05.LoadResult()) == []


# --- 讲评里的实测结论 --------------------------------------------------------


def test_p05_review_dataclass_always_truthy() -> None:
    empty = p05_result_solution.LoadResult()
    assert bool(empty) is True, "dataclass 对象永远是真，if not result 永远不成立"
    assert bool({}) is False


def test_p05_review_none_fails_loud() -> None:
    nothing: Any = None
    with pytest.raises(TypeError, match="object of type 'NoneType' has no len"):
        len(nothing)
    best: dict[str, int | None] = {"张三": 3, "李四": None}
    with pytest.raises(TypeError, match="'<' not supported"):
        sorted(best, key=best.get)  # type: ignore[arg-type]


def test_p05_review_sentinel_zero_sorts_first() -> None:
    best = {"张三": 3, "李四": 0, "王五": 5}
    assert sorted(best, key=best.__getitem__) == ["李四", "张三", "王五"], "没赢过的李四排第一"


def test_p05_review_directory_exists(tmp_path: Path) -> None:
    folder = tmp_path / "games.json"
    folder.mkdir()
    assert folder.exists() and not folder.is_file()
    with pytest.raises(OSError) as excinfo:
        open(folder, encoding="utf-8")  # noqa: SIM115
    if os.name == "nt":
        assert type(excinfo.value) is PermissionError
