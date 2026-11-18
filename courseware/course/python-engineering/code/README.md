# 配套代码

《Python 工程化实战》的全部可运行代码。**这个目录是自包含的，可以单独拷出去用。**

## 跑起来

```powershell
# 1. 建虚拟环境（第 0.2 章详细讲为什么要这么做）
python -m venv .venv
.\.venv\Scripts\Activate.ps1          # Windows PowerShell
# source .venv/bin/activate           # macOS / Linux

# 2. 安装（-e 是可编辑安装，改代码不用重装）
pip install -e ".[dev]"

# 3. 验证环境没问题
pytest
```

如果跳过了第 2 步，直接敲 `pytest` 会报 `ModuleNotFoundError: No module named 'm00_setup'`，这时要么补上第 2 步，要么在 `code/` 下改用 `python -m pytest`。两者的区别第 3.1 章第 9 节专门讲。

看到 `N passed, M skipped`、**没有 `failed`** 就对了。**skipped 是正常的**——那些是你还没做的练习，做完一道就少一个。全部做完时 skipped 为 0。

## 每章三个文件

| 文件 | 用途 |
|---|---|
| `chXX_YY_example.py` | 讲解里出现的可运行示例。**先跑它**，再回去读讲解 |
| `chXX_YY_exercise.py` | 练习骨架，按 `TODO` 写 |
| `chXX_YY_solution.py` | 参考答案。**先自己试 20 分钟再看** |

## 常用命令

```powershell
# 跑某一章的示例
python -m m02_testing.ch02_01_example

# 检查你的练习
pytest tests/test_m02.py -k ch02_01 -v

# 跑全部测试
pytest

# 看哪些练习还没做（skip 的就是没做的）
pytest -v -rs

# 代码风格检查
ruff check .

# 类型检查
mypy .
```

**注意用 `python -m 模块名` 而不是 `python 路径/文件.py`**。两者的 `sys.path` 不同，前者能正确处理包内导入。第 3.1 章专门讲这个区别。

## 目录结构

```
code/
  pyproject.toml          依赖与工具配置（ruff、mypy、pytest 都在这里）
  m01_basics/             M1 语言基础
  m02_testing/            M2 测试入门
  m03_structure/          M3 工程结构
  m04_persistence/        M4 数据持久化
  m05_http/               M5 网络请求
  m06_config/             M6 配置管理
  m07_integration/        M7 综合实战
  m08_testing_advanced/   M8 测试进阶
  tests/
    test_m01.py           每个模块一个测试文件
    test_m02.py
    ...
```

## 两个要注意的地方

**一、有些示例要用两种方式各跑一次。** 比如第 2.1 章的 `ch02_01_example.py`：

```powershell
python -m m02_testing.ch02_01_example
python -O -m m02_testing.ch02_01_example      # 加 -O，对比输出
```

输出差异本身就是那一章的教学内容。章节里会明确说明哪些示例需要这样跑。

**二、练习文件里有故意留着的坏代码。** 比如 `ch02_01_exercise.py` 里的 `test_broken()`，
三条断言都有问题，题目要求你找出来。**不要「顺手修好」它**，测试会检查它保持原样。

## Windows 用户：先解决中文乱码

PowerShell 的默认控制台代码页是 **936（GBK）**，而 Python 和 pytest 输出的是 UTF-8。
不处理的话，报错信息里的中文会变成这样：

```text
>       assert example.check_num(30, 50) == "澶т簡"
E       assert ("assert '灏忎簡'... 澶т簡\n  + 灏忎簡",) == ()
```

**每次开新终端先执行这两行：**

```powershell
$env:PYTHONUTF8 = 1
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
```

想一劳永逸，把它们加进 PowerShell 配置文件：

```powershell
notepad $PROFILE
```

> 注意：`$env:PYTHONUTF8=1` 还有一个副作用——它会让 `open()` 默认用 UTF-8 读写文件，
> 从而**掩盖「忘记写 `encoding="utf-8"`」这个 bug**。第 4.1 章会专门讲这件事，
> 到那一章会要求你临时去掉这个设置来复现问题。

## 环境要求

- Python **3.10+**（用到了 `X | Y` 类型联合语法）
- 不需要联网，除了 M5 网络请求那几章（会用公开的测试 API，也提供离线的 Mock 版本）

## 工具检查说明

| 命令 | 作用 | 什么时候用 |
|---|---|---|
| `pytest` | 跑测试 | 每章练习完 |
| `ruff check .` | 风格与潜在错误 | 提交代码前 |
| `mypy .` | 类型检查 | 第 1.6 章学完类型注解之后 |

三者的配置都在 `pyproject.toml` 里，**配置项都带了注释说明为什么这么设**。`mypy` 的配置刻意没开 `strict`，而是逐条列出四个开关，因为 `strict` 会连带打开十几条规则，报错时分不清是哪条在管。

练习文件（`*_exercise.py`）被 `mypy` 排除了——它们是留给你填的，没写完时不该被类型检查拦住。
