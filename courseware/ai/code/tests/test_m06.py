"""M6 每日一题的测试。

    pytest tests/test_m06.py -k p10 -v
"""

from __future__ import annotations

import os
import subprocess
import sys
import textwrap
from collections.abc import Callable
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest
from dotenv import dotenv_values, load_dotenv

from m06_config import (
    p10_settings_exercise,
    p10_settings_solution,
    p11_layers_exercise,
    p11_layers_solution,
)

CODE_DIR = Path(__file__).resolve().parents[1]
SECRET = "sk-test-0123456789abcdef"


def run_or_skip(fn: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
    try:
        return fn(*args, **kwargs)
    except NotImplementedError:
        pytest.skip(f"{fn.__name__} 还没完成")


# ============================================================================
# 第 10 题 · 读配置
# ============================================================================

P10 = {"exercise": p10_settings_exercise, "solution": p10_settings_solution}


@pytest.fixture(params=list(P10))
def p10(request: pytest.FixtureRequest) -> ModuleType:
    return P10[request.param]


BASE = {"API_KEY": SECRET, "API_BASE_URL": "https://scores.example.com/"}


def test_p10_defaults(p10: ModuleType) -> None:
    s = run_or_skip(p10.load_settings, BASE)
    assert (s.api_key, s.base_url, s.timeout, s.retries, s.debug) == \
        (SECRET, "https://scores.example.com", 5.0, 3, False), "末尾的 / 要去掉"
    assert type(s.timeout) is float and type(s.retries) is int and type(s.debug) is bool


def test_p10_conversions(p10: ModuleType) -> None:
    s = run_or_skip(p10.load_settings, {**BASE, "TIMEOUT": " 2.5 ", "RETRIES": "0",
                                        "DEBUG": "True"})
    assert (s.timeout, s.retries, s.debug) == (2.5, 0, True)


@pytest.mark.parametrize(("raw", "expected"), [("true", True), ("TRUE", True), ("1", True),
                                               ("yes", True), ("On", True), ("false", False),
                                               ("False", False), ("0", False), ("no", False),
                                               ("off", False), ("", False)])
def test_p10_debug_words(p10: ModuleType, raw: str, expected: bool) -> None:
    s = run_or_skip(p10.load_settings, {**BASE, "DEBUG": raw})
    assert s.debug is expected, f"DEBUG={raw!r} 应该是 {expected}"


@pytest.mark.parametrize("name", ["API_KEY", "API_BASE_URL"])
@pytest.mark.parametrize("value", [None, "", "   "], ids=["unset", "empty", "spaces"])
def test_p10_required(p10: ModuleType, name: str, value: str | None) -> None:
    """要求 1：必填项没设、设成空、只有空格，都算缺失。"""
    environ = {k: v for k, v in BASE.items() if k != name}
    if value is not None:
        environ[name] = value
    run_or_skip(p10.load_settings, BASE)
    with pytest.raises(p10.ConfigError, match=name):
        p10.load_settings(environ)


BAD = [
    ("TIMEOUT", "ten", "TIMEOUT"), ("TIMEOUT", "0", "TIMEOUT"), ("TIMEOUT", "-1", "TIMEOUT"),
    ("TIMEOUT", "nan", "TIMEOUT"), ("RETRIES", "1.5", "RETRIES"), ("RETRIES", "11", "RETRIES"),
    ("DEBUG", "ture", "DEBUG"), ("API_BASE_URL", "scores.example.com", "API_BASE_URL"),
]


@pytest.mark.parametrize(("name", "value", "mentioned"), BAD,
                         ids=[f"{n}={v}" for n, v, _ in BAD])
def test_p10_bad_values(p10: ModuleType, name: str, value: str, mentioned: str) -> None:
    run_or_skip(p10.load_settings, BASE)
    with pytest.raises(p10.ConfigError) as excinfo:
        p10.load_settings({**BASE, name: value})
    message = str(excinfo.value)
    assert mentioned in message and repr(value) in message, (
        f"报错要写出是哪一项、实际的值（用 !r）：{message!r}")


def test_p10_all_problems_at_once(p10: ModuleType) -> None:
    """要求 3：一次把所有问题都报出来。"""
    run_or_skip(p10.load_settings, BASE)
    with pytest.raises(p10.ConfigError) as excinfo:
        p10.load_settings({"TIMEOUT": "ten", "DEBUG": "ture", "RETRIES": "-1"})
    message = str(excinfo.value)
    missing = [part for part in ("API_KEY", "API_BASE_URL", "TIMEOUT", "DEBUG", "RETRIES")
               if part not in message]
    assert not missing, f"一次只报了一部分，漏了 {missing}：{message!r}"


def test_p10_config_error_is_value_error(p10: ModuleType) -> None:
    assert issubclass(p10.ConfigError, ValueError)


def test_p10_secret_not_in_repr(p10: ModuleType) -> None:
    """要求 5：打印 Settings、把它拼进字符串，都不能带出密钥。"""
    s = run_or_skip(p10.load_settings, BASE)
    for text in (repr(s), str(s), f"{s}", f"{s!r}"):
        assert SECRET not in text, f"密钥出现在了 {text!r} 里"
    assert "base_url" in repr(s), "其他字段照常显示"


def test_p10_secret_not_in_error(p10: ModuleType) -> None:
    run_or_skip(p10.load_settings, BASE)
    with pytest.raises(p10.ConfigError) as excinfo:
        p10.load_settings({**BASE, "TIMEOUT": "ten"})
    assert SECRET not in str(excinfo.value)


def test_p10_works_with_os_environ(p10: ModuleType, monkeypatch: pytest.MonkeyPatch) -> None:
    """平时的用法：load_settings(os.environ)。"""
    run_or_skip(p10.load_settings, BASE)
    for k, v in BASE.items():
        monkeypatch.setenv(k, v)
    monkeypatch.setenv("TIMEOUT", "7")
    assert p10.load_settings(os.environ).timeout == 7.0


# --- 讲评里的实测结论 --------------------------------------------------------


def test_p10_review_getenv_default_and_empty(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PE_EMPTY", "")
    assert os.getenv("PE_EMPTY", "默认") == "", "变量存在、值为空时，默认值不生效"
    assert (os.getenv("PE_EMPTY") or "默认") == "默认"
    assert bool("false") is True


def test_p10_review_environ_only_takes_str(monkeypatch: pytest.MonkeyPatch) -> None:
    with pytest.raises(TypeError, match="str expected, not int"):
        os.environ["PE_NUM"] = 10  # type: ignore[assignment]


def test_p10_review_dataclass_repr_leaks() -> None:
    from dataclasses import dataclass

    @dataclass(frozen=True)
    class Leaky:
        api_key: str

    assert repr(Leaky(SECRET)).endswith(f"Leaky(api_key='{SECRET}')")
    done = subprocess.run([sys.executable, "-c", textwrap.dedent(f"""
        from dataclasses import dataclass
        @dataclass(frozen=True)
        class S:
            api_key: str
        raise ValueError(f"配置不对：{{S('{SECRET}')}}")
    """)], capture_output=True, text=True, encoding="utf-8", check=False)
    assert f"ValueError: 配置不对：S(api_key='{SECRET}')" in done.stderr


def test_p10_review_dotenv_parsing(tmp_path: Path) -> None:
    env = tmp_path / ".env"
    env.write_text('EMPTY=\nINLINE=value # 注释\nHASH=abc#def\nQUOTED="a # b"\n'
                   "export EXP=yes\nURL=http://${HOST}/api\nHOST=h\n", encoding="utf-8")
    assert dict(dotenv_values(env)) == {"EMPTY": "", "INLINE": "value", "HASH": "abc#def",
                                        "QUOTED": "a # b", "EXP": "yes", "URL": "http:///api",
                                        "HOST": "h"}


def test_p10_review_load_dotenv_returns_false(tmp_path: Path) -> None:
    (tmp_path / "empty.env").write_text("", encoding="utf-8")
    assert load_dotenv(tmp_path / "nope.env") is False
    assert load_dotenv(tmp_path) is False, "传了目录"
    assert load_dotenv(tmp_path / "empty.env") is False, "文件存在但是空的，也是 False"


# ============================================================================
# 第 11 题 · 多环境配置
# ============================================================================

P11 = {"exercise": p11_layers_exercise, "solution": p11_layers_solution}


@pytest.fixture(params=list(P11))
def p11(request: pytest.FixtureRequest) -> ModuleType:
    return P11[request.param]


def make_dir(root: Path, files: dict[str, str]) -> Path:
    for name, text in files.items():
        (root / name).write_text(text, encoding="utf-8")
    return root


STANDARD = {
    ".env": "TIMEOUT=8\nRETRIES=2\n",
    ".env.development": "API_KEY=dev-key\nAPI_BASE_URL=https://dev.example.com\nDEBUG=true\n",
    ".env.testing": "API_KEY=test-key\nAPI_BASE_URL=https://test.example.com\n",
    ".env.production": "API_KEY=prod-file-key\nAPI_BASE_URL=https://example.com\nDEBUG=false\n"
                       "TIMEOUT=3\n",
}


def merge(p11: ModuleType, root: Path, environ: dict[str, str]) -> Any:
    return run_or_skip(p11.merge_layers, root, environ)


def test_p11_default_environment(p11: ModuleType, tmp_path: Path) -> None:
    env, values, sources = merge(p11, make_dir(tmp_path, STANDARD), {})
    assert env == "development"
    assert values["API_KEY"] == "dev-key" and values["TIMEOUT"] == "8"
    assert sources["API_KEY"] == ".env.development" and sources["TIMEOUT"] == ".env"


def test_p11_env_file_overrides_base(p11: ModuleType, tmp_path: Path) -> None:
    """要求 3：.env.production 的 TIMEOUT=3 覆盖 .env 的 TIMEOUT=8。"""
    env, values, sources = merge(p11, make_dir(tmp_path, STANDARD), {"APP_ENV": "production"})
    assert env == "production"
    assert values["TIMEOUT"] == "3" and sources["TIMEOUT"] == ".env.production"
    assert values["RETRIES"] == "2", ".env.production 里没有的，用 .env 的"


def test_p11_system_wins(p11: ModuleType, tmp_path: Path) -> None:
    """要求 3：部署平台注入的环境变量优先于所有文件。"""
    _, values, sources = merge(p11, make_dir(tmp_path, STANDARD),
                               {"APP_ENV": "production", "API_KEY": "injected"})
    assert values["API_KEY"] == "injected", "注入的密钥被文件覆盖了"
    assert sources["API_KEY"] == "环境变量"


def test_p11_system_only_keys(p11: ModuleType, tmp_path: Path) -> None:
    """密钥只在系统环境变量里、文件里一个字都没有，也要读得到。"""
    files = {**STANDARD, ".env.production": "API_BASE_URL=https://example.com\n"}
    _, values, _ = merge(p11, make_dir(tmp_path, files), {"APP_ENV": "production",
                                                         "API_KEY": "injected"})
    assert values["API_KEY"] == "injected"


def test_p11_unrelated_environ_ignored(p11: ModuleType, tmp_path: Path) -> None:
    _, values, _ = merge(p11, make_dir(tmp_path, STANDARD), {"PATH": "C:\\x", "USERNAME": "hubo"})
    assert "PATH" not in values and "USERNAME" not in values


def test_p11_local_file(p11: ModuleType, tmp_path: Path) -> None:
    """.env.local 覆盖环境文件，但仍然输给系统环境变量。"""
    files = {**STANDARD, ".env.local": "API_KEY=my-real-key\nDEBUG=false\n"}
    _, values, sources = merge(p11, make_dir(tmp_path, files), {"DEBUG": "1"})
    assert values["API_KEY"] == "my-real-key" and sources["API_KEY"] == ".env.local"
    assert values["DEBUG"] == "1" and sources["DEBUG"] == "环境变量"


def test_p11_app_env_from_base_file(p11: ModuleType, tmp_path: Path) -> None:
    """要求 1：APP_ENV 可以写在 .env 里；系统环境变量里有的话以系统的为准。"""
    root = make_dir(tmp_path, {**STANDARD, ".env": "APP_ENV=testing\nTIMEOUT=8\n"})
    assert merge(p11, root, {})[0] == "testing"
    assert merge(p11, root, {"APP_ENV": "production"})[0] == "production"


@pytest.mark.parametrize("raw", ["Production", " production ", "PRODUCTION"])
def test_p11_app_env_normalized(p11: ModuleType, tmp_path: Path, raw: str) -> None:
    assert merge(p11, make_dir(tmp_path, STANDARD), {"APP_ENV": raw})[0] == "production"


@pytest.mark.parametrize("raw", ["prodution", "staging", "dev"])
def test_p11_app_env_rejected(p11: ModuleType, tmp_path: Path, raw: str) -> None:
    root = make_dir(tmp_path, STANDARD)
    run_or_skip(p11.merge_layers, root, {})
    with pytest.raises(p10_settings_solution.ConfigError) as excinfo:
        p11.merge_layers(root, {"APP_ENV": raw})
    assert repr(raw) in str(excinfo.value), f"报错要写出原来的值：{excinfo.value}"


def test_p11_missing_env_file(p11: ModuleType, tmp_path: Path) -> None:
    """要求 2：当前环境的配置文件不存在，报错并写出路径。"""
    root = make_dir(tmp_path, {k: v for k, v in STANDARD.items() if k != ".env.testing"})
    run_or_skip(p11.merge_layers, root, {})
    with pytest.raises(p10_settings_solution.ConfigError) as excinfo:
        p11.merge_layers(root, {"APP_ENV": "testing"})
    assert ".env.testing" in str(excinfo.value)


def test_p11_does_not_touch_os_environ(p11: ModuleType, tmp_path: Path,
                                       monkeypatch: pytest.MonkeyPatch) -> None:
    """要求 4：不修改 os.environ。"""
    for key in ("API_KEY", "API_BASE_URL", "TIMEOUT", "RETRIES", "DEBUG", "APP_ENV"):
        monkeypatch.delenv(key, raising=False)
    before = dict(os.environ)
    merge(p11, make_dir(tmp_path, STANDARD), dict(os.environ))
    changed = sorted(set(os.environ.items()) ^ set(before.items()))
    assert not changed, f"os.environ 被改了：{changed} —— 用 dotenv_values，不要 load_dotenv"


def test_p11_switch_environment_in_one_process(p11: ModuleType, tmp_path: Path) -> None:
    """同一个进程里先读 development 再读 testing，不能残留 development 的值。"""
    root = make_dir(tmp_path, {**STANDARD, ".env.development":
                               STANDARD[".env.development"] + "DEV_ONLY=1\n"})
    merge(p11, root, {})
    _, values, _ = p11.merge_layers(root, {"APP_ENV": "testing"})
    assert values["API_KEY"] == "test-key", "拿到的还是 development 的密钥"
    assert "DEV_ONLY" not in values


def test_p11_load_for(p11: ModuleType, tmp_path: Path) -> None:
    env, settings = run_or_skip(p11.load_for, make_dir(tmp_path, STANDARD),
                                {"APP_ENV": "testing"})
    assert env == "testing"
    assert (settings.api_key, settings.base_url, settings.timeout, settings.retries,
            settings.debug) == ("test-key", "https://test.example.com", 8.0, 2, False)


def test_p11_production_debug_forbidden(p11: ModuleType, tmp_path: Path) -> None:
    """要求 5：生产环境开了 DEBUG 要报错，并写明 DEBUG 是从哪来的。"""
    root = make_dir(tmp_path, STANDARD)
    run_or_skip(p11.load_for, root, {})
    with pytest.raises(p10_settings_solution.ConfigError) as excinfo:
        p11.load_for(root, {"APP_ENV": "production", "DEBUG": "yes"})
    assert "DEBUG" in str(excinfo.value) and "环境变量" in str(excinfo.value)


# --- 讲评里的实测结论 --------------------------------------------------------


def run_clean(code: str, cwd: Path, script: Path | None = None) -> str:
    env = {k: v for k, v in os.environ.items()
           if k not in ("API_KEY", "DEV_ONLY", "WHERE", "APP_ENV")}
    env["PYTHONIOENCODING"] = "utf-8"
    args = [sys.executable, str(script)] if script else [sys.executable, "-c", code]
    done = subprocess.run(args, cwd=cwd, capture_output=True, text=True, encoding="utf-8",
                          env=env, check=False)
    assert done.returncode == 0, done.stderr
    return done.stdout.strip()


def test_p11_review_load_dotenv_leftovers(tmp_path: Path) -> None:
    make_dir(tmp_path, {".env.development": "API_KEY=dev-key\nDEV_ONLY=1\n",
                        ".env.testing": "API_KEY=test-key\n"})
    out = run_clean("import os\nfrom dotenv import load_dotenv\n"
                    "load_dotenv('.env.development')\nload_dotenv('.env.testing')\n"
                    "print(os.environ['API_KEY'], os.environ.get('DEV_ONLY'))", tmp_path)
    assert out == "dev-key 1"


def test_p11_review_override_true_beats_injected(tmp_path: Path) -> None:
    make_dir(tmp_path, {".env.production": "API_KEY=from-file\n"})
    out = run_clean("import os\nfrom dotenv import load_dotenv\n"
                    "os.environ['API_KEY'] = 'injected-by-platform'\n"
                    "load_dotenv('.env.production', override=True)\nprint(os.environ['API_KEY'])",
                    tmp_path)
    assert out == "from-file"


def test_p11_review_find_dotenv_starts_from_script(tmp_path: Path) -> None:
    """load_dotenv() 不传路径：从调用它的 .py 文件所在目录往上找，不是从当前目录。"""
    (tmp_path / "proj" / "src").mkdir(parents=True)
    (tmp_path / "other").mkdir()
    (tmp_path / "proj" / ".env").write_text("WHERE=proj\n", encoding="utf-8")
    (tmp_path / "other" / ".env").write_text("WHERE=other\n", encoding="utf-8")
    script = tmp_path / "proj" / "src" / "main.py"
    script.write_text("import os\nfrom dotenv import load_dotenv\nload_dotenv()\n"
                      "print(os.getenv('WHERE'))\n", encoding="utf-8")
    for cwd in ("proj", "proj/src", "other"):
        assert run_clean("", tmp_path / cwd, script) == "proj", f"cwd={cwd}"
    out = run_clean("import os\nfrom dotenv import load_dotenv\nload_dotenv()\n"
                    "print(os.getenv('WHERE'))", tmp_path / "other")
    assert out == "other", "python -c 没有脚本文件，这时才从当前目录找"
