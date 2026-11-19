"""M0 模块的测试。

自检脚本本身也要有测试 —— 否则「环境没配好」和「自检脚本有 bug」
这两种情况分不出来。

跑法：
    pytest tests/test_m00.py -v
"""

from __future__ import annotations

import subprocess
import sys

import pytest

from m00_setup import check_env

# ============================================================================
# 每一项检查的返回值结构
# ============================================================================


def test_ch00_02_all_checks_return_result() -> None:
    """每个检查函数都要返回一个结构完整的 Result。"""
    for check in check_env.CHECKS:
        result = check()
        assert isinstance(result, check_env.Result), f"{check.__name__} 返回类型不对"
        assert result.name, f"{check.__name__} 没有填 name"
        assert result.level in ("ok", "warn", "fail"), f"{check.__name__} 的 level 非法"
        assert result.detail, f"{check.__name__} 没有填 detail"


def test_ch00_02_failures_must_carry_fixes() -> None:
    """不通过的检查必须给出修复建议。

    一个只说「失败了」却不说怎么办的自检脚本没有价值。
    """
    for result in check_env.run_all():
        if result.level in ("fail", "warn"):
            assert result.fixes, f"{result.name} 判定为 {result.level} 但没给修复建议"


def test_ch00_02_result_tag() -> None:
    """三种 level 各有对应的显示标签。"""
    assert check_env.Result("x", "ok", "d").tag == "[ OK ]"
    assert check_env.Result("x", "warn", "d").tag == "[WARN]"
    assert check_env.Result("x", "fail", "d").tag == "[FAIL]"


# ============================================================================
# 当前环境应该满足的条件
#
# 这些测试能跑起来，本身就说明环境是好的 —— 所以它们应该全部通过。
# 如果有失败，说明自检脚本的判断逻辑写错了。
# ============================================================================


def test_ch00_02_python_version_passes() -> None:
    """能跑 pytest 的环境，Python 版本一定达标。"""
    assert check_env.check_python_version().level == "ok"


def test_ch00_02_virtualenv_detected() -> None:
    """判断依据是 sys.prefix != sys.base_prefix。"""
    result = check_env.check_virtualenv()
    expected = "ok" if sys.prefix != sys.base_prefix else "fail"
    assert result.level == expected


def test_ch00_02_dev_tools_present() -> None:
    """pytest 正在跑，所以开发工具这项必须通过。"""
    assert check_env.check_dev_tools().level == "ok"


def test_ch00_02_course_packages_importable() -> None:
    """测试能 import m00_setup，所以课程模块这项必须通过。"""
    assert check_env.check_course_packages().level == "ok"


def test_ch00_02_assert_enabled_in_normal_mode() -> None:
    """普通模式下 __debug__ 为 True。"""
    assert check_env.check_assert_enabled().level == "ok"


# ============================================================================
# -O 模式下自检应该报错
#
# 这是第 2.1 章那个坑的预埋：用 -O 跑测试会让 assert 静默失效，
# 自检脚本必须拦住这种情况。
# ============================================================================


def test_ch00_02_detects_optimize_mode() -> None:
    """用 -O 跑自检，断言开关这一项必须判 fail。"""
    code = (
        "from m00_setup.check_env import check_assert_enabled\n"
        "r = check_assert_enabled()\n"
        "print(r.level)\n"
    )
    done = subprocess.run(
        [sys.executable, "-O", "-c", code],
        capture_output=True,
        text=True,
        check=True,
    )
    assert done.stdout.strip() == "fail", f"实际输出: {done.stdout!r}"


def test_ch00_02_normal_mode_passes_assert_check() -> None:
    """对照：不加 -O 时同一项判 ok。"""
    code = (
        "from m00_setup.check_env import check_assert_enabled\n"
        "print(check_assert_enabled().level)\n"
    )
    done = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        check=True,
    )
    assert done.stdout.strip() == "ok"


# ============================================================================
# 退出码：接进 CI 时依赖这个
# ============================================================================


def test_ch00_02_report_exit_code_on_failure(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """有 fail 项时退出码必须是 1。"""
    results = [
        check_env.Result("甲", "ok", "没问题"),
        check_env.Result("乙", "fail", "坏了", ["执行某条命令"]),
    ]
    assert check_env.report(results) == 1

    out = capsys.readouterr().out
    assert "[FAIL]" in out
    assert "执行某条命令" in out, "修复建议必须打印出来"


def test_ch00_02_report_exit_code_on_warning(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """只有 warn 项时退出码是 0，但建议仍要打印。"""
    results = [
        check_env.Result("甲", "ok", "没问题"),
        check_env.Result("乙", "warn", "建议处理", ["设个环境变量"]),
    ]
    assert check_env.report(results) == 0

    out = capsys.readouterr().out
    assert "[WARN]" in out
    assert "设个环境变量" in out


def test_ch00_02_report_all_ok(capsys: pytest.CaptureFixture[str]) -> None:
    """全部通过时退出码 0，且不打印修复区块。"""
    results = [check_env.Result("甲", "ok", "没问题")]
    assert check_env.report(results) == 0

    out = capsys.readouterr().out
    assert "全部通过" in out
    assert "怎么修" not in out


def test_ch00_02_script_runs_as_module() -> None:
    """python -m m00_setup.check_env 能跑通，且退出码为 0。

    这条测试覆盖的是第 0.2 章练习 1 要求的那条命令。
    """
    done = subprocess.run(
        [sys.executable, "-m", "m00_setup.check_env"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    assert done.returncode == 0, f"自检失败：\n{done.stdout}\n{done.stderr}"
    assert "环境自检" in done.stdout


# ============================================================================
# 中英混排的对齐：用 len() 会歪，必须按显示宽度算
# ============================================================================


def test_ch00_02_display_width() -> None:
    """全角字符占两列，ASCII 占一列。"""
    assert check_env.display_width("abc") == 3
    assert check_env.display_width("中文") == 4
    assert check_env.display_width("UTF-8 输出") == 10  # 6 个 ASCII + 2 个汉字
    assert check_env.display_width("") == 0

    # 这就是直接用 len() 会出问题的地方
    assert len("UTF-8 输出") == 8
    assert check_env.display_width("UTF-8 输出") != len("UTF-8 输出")


def test_ch00_02_pad_aligns_by_display_width() -> None:
    """补齐后的显示宽度必须一致，而不是字符数一致。"""
    names = ["Python 版本", "UTF-8 输出", "虚拟环境", "课程模块"]
    width = max(check_env.display_width(n) for n in names)

    padded = [check_env.pad(n, width) for n in names]
    widths = {check_env.display_width(p) for p in padded}
    assert widths == {width}, f"补齐后宽度不一致：{widths}"


def test_ch00_02_pad_never_truncates() -> None:
    """目标宽度比内容还小时，原样返回，不截断。"""
    assert check_env.pad("中文很长", 2) == "中文很长"
