"""第 0.2 章 · 环境自检。

跑法：

    python -m m00_setup.check_env

逐项检查环境配置，任何一项失败都会打印出具体的修复命令。
全部通过时退出码为 0，有失败时为 1（方便接进 CI 或脚本）。

这个脚本刻意不 import 任何第三方包 —— 它要在依赖还没装好的时候也能跑起来。
检查第三方包是否存在用的是 importlib.util.find_spec，它只查找不导入。
"""

from __future__ import annotations

import importlib.util
import os
import platform
import sys
import unicodedata
from dataclasses import dataclass, field

# 这门课要求的最低 Python 版本。
# 3.10 是因为用到了 X | Y 类型联合语法（PEP 604）。
MIN_PYTHON = (3, 10)

# 运行必需的依赖，对应 pyproject.toml 的 [project] dependencies。
# 键是 import 时的模块名，值是 pip 安装时的包名 —— 两者经常不一样。
RUNTIME_DEPS = {
    "requests": "requests",
    "dotenv": "python-dotenv",
}

# 开发工具，对应 [project.optional-dependencies] 的 dev。
DEV_TOOLS = {
    "pytest": "pytest",
    "ruff": "ruff",
    "mypy": "mypy",
}

# 课程的模块包。
# 注意：用 python -m m00_setup.check_env 运行时，当前目录 code/ 本身就在 sys.path 里，
# 所以没做 pip install -e 也能导入。这一项通过只说明「在 code/ 下用 python -m 没问题」，
# 不说明直接敲 pytest 也没问题 —— 两者的区别见第 3.1 章第 9 节。
COURSE_PACKAGES = ["m00_setup", "m01_basics", "m02_testing", "m03_structure"]


@dataclass
class Result:
    """一项检查的结果。

    level 有三种：
      ok   —— 通过
      warn —— 不影响做练习，但建议处理
      fail —— 必须修，否则后面的章节跑不起来
    """

    name: str
    level: str
    detail: str
    fixes: list[str] = field(default_factory=list)

    @property
    def tag(self) -> str:
        return {"ok": "[ OK ]", "warn": "[WARN]", "fail": "[FAIL]"}[self.level]


def check_python_version() -> Result:
    """Python 版本必须 >= 3.10。"""
    current = sys.version_info[:3]
    version_text = ".".join(str(n) for n in current)
    required = ".".join(str(n) for n in MIN_PYTHON)

    if current[:2] >= MIN_PYTHON:
        return Result(
            "Python 版本",
            "ok",
            f"{version_text}（要求 >= {required}）",
        )
    return Result(
        "Python 版本",
        "fail",
        f"{version_text} 太低，要求 >= {required}",
        [
            "去 https://www.python.org/downloads/ 装 3.10 或更高版本",
            "装好后用新版本重建虚拟环境：py -3.13 -m venv .venv",
        ],
    )


def check_virtualenv() -> Result:
    """是否在虚拟环境里。

    判断依据是 sys.prefix != sys.base_prefix，这是标准做法。
    不用 VIRTUAL_ENV 环境变量 —— 它只在用激活脚本时才会设置，
    直接调用 .venv/Scripts/python.exe 时是空的。
    """
    in_venv = sys.prefix != sys.base_prefix

    if in_venv:
        return Result("虚拟环境", "ok", f"已激活：{sys.prefix}")

    activate = (
        ".\\.venv\\Scripts\\Activate.ps1"
        if platform.system() == "Windows"
        else "source .venv/bin/activate"
    )
    return Result(
        "虚拟环境",
        "fail",
        f"没有激活，当前用的是系统 Python：{sys.prefix}",
        [
            "如果还没创建：python -m venv .venv",
            f"激活：{activate}",
            "验证：python -c \"import sys; print(sys.prefix != sys.base_prefix)\"",
        ],
    )


def _check_packages(
    title: str, mapping: dict[str, str], extra: str, level_if_missing: str
) -> Result:
    """检查一组包是否可导入。

    find_spec 只查找模块、不执行它，所以不会因为某个包导入时报错而中断自检。
    """
    missing = [
        pip_name
        for module_name, pip_name in mapping.items()
        if importlib.util.find_spec(module_name) is None
    ]

    if not missing:
        return Result(title, "ok", "、".join(mapping.values()) + " 都已安装")

    return Result(
        title,
        level_if_missing,
        f"缺少：{'、'.join(missing)}",
        [f'pip install -e "{extra}"'],
    )


def check_runtime_deps() -> Result:
    return _check_packages("运行依赖", RUNTIME_DEPS, ".", "fail")


def check_dev_tools() -> Result:
    return _check_packages("开发工具", DEV_TOOLS, ".[dev]", "fail")


def check_course_packages() -> Result:
    """课程模块能不能导入。

    不能导入说明 pip install -e 没做，或者当前目录不对。
    """
    missing = [
        name for name in COURSE_PACKAGES if importlib.util.find_spec(name) is None
    ]

    if not missing:
        return Result("课程模块", "ok", "、".join(COURSE_PACKAGES) + " 都可导入")

    return Result(
        "课程模块",
        "fail",
        f"导入不到：{'、'.join(missing)}",
        [
            "确认当前在 code/ 目录下",
            'pip install -e ".[dev]"',
            "注意用 python -m 模块名 运行，不要用 python 路径/文件.py",
        ],
    )


def check_utf8_output() -> Result:
    """Windows 下的中文乱码检查。

    PYTHONUTF8=1 让 Python 用 UTF-8 读写文件和输出；
    控制台代码页还需要单独设置，但那个从 Python 里改不了，只能提示。
    """
    if platform.system() != "Windows":
        return Result("UTF-8 输出", "ok", "非 Windows 平台，默认就是 UTF-8")

    utf8_mode = sys.flags.utf8_mode
    encoding = sys.stdout.encoding or "unknown"

    if utf8_mode:
        return Result(
            "UTF-8 输出",
            "ok",
            f"PYTHONUTF8 已开启，stdout 编码 {encoding}",
        )

    return Result(
        "UTF-8 输出",
        "warn",
        f"PYTHONUTF8 未开启，stdout 编码 {encoding}，中文可能乱码",
        [
            "$env:PYTHONUTF8 = 1",
            "[Console]::OutputEncoding = [System.Text.Encoding]::UTF8",
            "想一劳永逸就写进 PowerShell 配置：notepad $PROFILE",
        ],
    )


def check_assert_enabled() -> Result:
    """检查有没有用 -O 跑这个脚本。

    -O 会删掉所有 assert，而这门课 M2 模块大量依赖 assert。
    用 -O 跑测试会让一部分测试静默通过 —— 这正是第 2.1 章要讲的坑。
    """
    if __debug__:
        return Result("断言开关", "ok", "__debug__ = True，assert 正常生效")

    return Result(
        "断言开关",
        "fail",
        "__debug__ = False，说明用了 -O，所有 assert 都被删除了",
        [
            "去掉命令里的 -O 重新运行",
            "第 2.1 章会专门讲这个：-O 模式下 assert 校验会静默失效",
        ],
    )


CHECKS = [
    check_python_version,
    check_virtualenv,
    check_runtime_deps,
    check_dev_tools,
    check_course_packages,
    check_utf8_output,
    check_assert_enabled,
]


def run_all() -> list[Result]:
    return [check() for check in CHECKS]


def display_width(text: str) -> int:
    """文本在等宽终端里占几列。

    中文、日文这类全角字符占两列，ASCII 占一列。
    直接用 len() 对齐中英混排的表格会歪掉 —— 这是个很常见的小坑。
    """
    return sum(
        2 if unicodedata.east_asian_width(char) in ("W", "F") else 1 for char in text
    )


def pad(text: str, width: int) -> str:
    """按显示宽度右侧补空格。"""
    return text + " " * max(0, width - display_width(text))


def report(results: list[Result]) -> int:
    """打印检查结果，返回退出码。"""
    line = "=" * 70
    print(line)
    print(" Python 工程化实战 · 环境自检")
    print(line)

    width = max(display_width(r.name) for r in results)
    for r in results:
        print(f"{r.tag} {pad(r.name, width)}  {r.detail}")

    failed = [r for r in results if r.level == "fail"]
    warned = [r for r in results if r.level == "warn"]

    if failed or warned:
        print()
        print("-" * 70)
        for r in failed + warned:
            print(f"{r.tag} {r.name} —— 怎么修：")
            for fix in r.fixes:
                print(f"       {fix}")
            print()

    print(line)
    if failed:
        print(f" 还有 {len(failed)} 项必须修复，修完再继续第 1.1 章。")
        return 1
    if warned:
        print(f" 全部必需项通过，另有 {len(warned)} 项建议处理。可以继续第 1.1 章。")
        return 0
    print(" 全部通过，环境配置正确。开始第 1.1 章。")
    return 0


def main() -> int:
    results = run_all()
    code = report(results)
    # 顺手打印几条环境信息，排查问题时有用
    print()
    print(f" Python     {sys.version.splitlines()[0]}")
    print(f" 可执行文件 {sys.executable}")
    print(f" 平台       {platform.platform()}")
    print(f" 工作目录   {os.getcwd()}")
    return code


if __name__ == "__main__":
    sys.exit(main())
