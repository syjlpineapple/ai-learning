"""M4 每日一题的测试。

    pytest tests/test_m04.py -k p01 -v

每道题的测试同时跑在你的练习（exercise）和参考答案（solution）上。
练习还没做时显示 skip。
"""

from __future__ import annotations

import contextlib
import os
import subprocess
import sys
from collections.abc import Callable, Iterator
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest

from m04_persistence import p01_scoreboard_exercise, p01_scoreboard_solution

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
    env = {**os.environ, "PYTHONPATH": str(CODE_DIR), "PYTHONIOENCODING": "utf-8"}
    done = subprocess.run(
        [sys.executable, "-X", "utf8=0", "-X", "warn_default_encoding",
         "-W", "error::EncodingWarning", "-c", code],
        cwd=tmp_path, capture_output=True, text=True, encoding="utf-8", env=env, check=False)
    assert "EncodingWarning" not in done.stderr, (
        "有一处 open() 没写 encoding：\n" + done.stderr.strip().splitlines()[-1])
    assert done.returncode == 0, done.stderr
    assert done.stdout.strip() == "[('张三', 3), ('欧阳修文', 5)]"
    (tmp_path / "s.txt").read_bytes().decode("utf-8")   # 文件本身必须是 UTF-8


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
