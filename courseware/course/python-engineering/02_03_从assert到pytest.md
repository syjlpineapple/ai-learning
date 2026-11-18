# 2.3 从 `assert` 到 `pytest`

> **前置** 2.2 异常体系与 `raise`
> **时长** 约 100 分钟（讲解 40 + 练习 60）
> **配套代码** [`code/m02_testing/ch02_03_*.py`](code/m02_testing/)
>
> 🆕 这一章是为课程新写的。原学习记录到第 21 天才开始用 pytest，中间留下了一个「测试一次都没跑过」的真实问题。

## 学习目标

学完这一章，你应该能够：

1. 说出手写测试的四个根本问题，以及 `pytest` 分别怎么解决
2. **说出 `collected 0 items` 意味着什么，以及 pytest 的退出码 5**
3. **准确说出 pytest 默认的发现规则**，包括 `testing_data` 会被当成测试这个反直觉的情况
4. 读懂 pytest 的失败报告，包括 `+ where 50 = parse_guess('50')` 这一行
5. 用 `@pytest.mark.parametrize` 代替循环里的 `assert`，并说清为什么
6. 用 `pytest.raises` 测异常，**知道 `match` 是正则表达式、什么时候必须 `re.escape`**
7. 用 `-v`、`-x`、`-k`、`-rs` 控制 pytest 的运行，**知道 `-q` 和 `-v` 会互相抵消**
8. 说清「测试通过」和「测试有用」的区别，并用「改错版本」检验自己的测试

## 为什么需要这一章

到第 2.2 章为止，测试全是手写的：

```python
def test_check_num() -> None:
    assert check_num(30, 50) == "小了"
    assert check_num(50, 50) == "正确"
    assert check_num(70, 50) == "大了"

test_check_num()               # 自己调用
print("所有测试通过！")
```

这样写有四个问题，每一个都在前面的章节里出现过：

| 问题 | 在哪出现过 |
|---|---|
| **忘了调用测试函数，测试就不跑**，而且没有任何提示 | 第 2.1 章 |
| **第一个 `assert` 失败，后面的全部不执行**，你只知道一个错误 | 本章第 5 节 |
| **测异常要写六行 `try / except / else`**，漏了 `else` 就是假测试 | 第 2.2 章 |
| **没有汇总**：跑了几条、过了几条、失败的是哪几条 | —— |

**测试框架就是为了解决这些问题而存在的。** Python 生态里最常用的是 `pytest`，第 0.2 章已经装好了。

而且其实你已经用了它很久：课程配套代码里的 `tests/test_m01.py` 有三百多条测试，每次跑 `pytest tests/test_m01.py -k ch01_05` 都是它在工作。这一章讲它到底在做什么。

---

# 一、概念与原理

## 1. 最小的 pytest 测试

```python
# test_game.py
def check_num(guess: int, target: int) -> str:
    ...

def test_check_num() -> None:
    assert check_num(30, 50) == "小了"
```

```powershell
pytest test_game.py
```

**和手写测试的区别：没有 `test_check_num()` 那一行调用，也没有 `print`。** pytest 会自己找到 `test_` 开头的函数并调用它，最后给出汇总。

pytest 用的就是普通的 `assert`——第 2.1 章学的那个。不需要学新的断言语法。

## 2. ⚠️ `collected 0 items`：测试一次都没跑

学习记录第 10 天的测试文件是这样写的：

```python
# test_game.py
def check_num(guess, target):
    ...

if __name__ == "__main__":
    assert check_num(10, 20) == "小了"
    assert check_num(20, 20) == "正确"
    print("所有测试通过")
```

```text
1. 断言写在 if __name__ == '__main__' 里
   pytest main_guard 的输出：
      no tests ran in 0.01s
   退出码：5   ← 5 表示「一个测试都没收集到」
   直接 python 运行它：所有测试通过（退出码 0）
```

**直接运行它，打印「所有测试通过」；用 pytest 运行它，一个测试都没跑。**

两个原因叠加：

**一、断言写在 `if __name__ == "__main__":` 里。** pytest 是**导入**测试文件，不是直接运行它。导入时 `__name__` 是模块名，整个块被跳过（第 3.1 章细讲 `__name__`）。

**二、文件里没有 `test_` 开头的函数。** pytest 靠命名找测试，这个文件里一个都没有。

学习记录里这份测试从写下到整理时被发现，**一次都没有被 pytest 执行过**。全仓库 `pytest` 跑出 13 passed，没有一个来自这里。

> **「测试文件存在」和「测试在跑」是两件事。** 判断依据只有一个：看 pytest 报告的收集数量。
> 看到 `collected 0 items`，或者数字比你预期的少，要立刻警觉。

### pytest 的退出码

| 退出码 | 含义 |
|---|---|
| **0** | 全部通过 |
| **1** | 有测试失败 |
| 2 | 被用户中断（Ctrl+C） |
| 3 | pytest 内部错误 |
| 4 | 命令行用法错误 |
| **5** | **一个测试都没收集到** |

**退出码 5 是个有用的信号。** CI（持续集成，自动跑测试的服务器）看到非 0 退出码会判定失败。如果测试因为命名错误一条都没收集到，至少不会被当成「全部通过」。

对比一下第 1.3 章：`sys.exit()` 让程序少做了事，退出码却是 0。**pytest 在这件事上的设计是对的**——什么都没测，就不该说成功。

## 3. 发现规则

pytest 按这些规则找测试（pytest 9.2，没有自定义配置时）：

| 对象 | 规则 |
|---|---|
| 文件 | `test_*.py` 或 `*_test.py` |
| 函数 | **以 `test` 开头** |
| 类 | 以 `Test` 开头，**且没有 `__init__`**；类里的方法同样以 `test` 开头 |

配套示例搭了一个目录，里面放了各种命名的文件和函数，然后跑 `pytest names --collect-only`（只收集、不运行）：

```text
2. 命名规则：pytest names --collect-only 收集了什么
      names/game_test.py::test_in_suffix_file
      names/test_names.py::test_ok
      names/test_names.py::testing_data
      names/test_names.py::TestGame::test_inside_class
   ↑ 注意 testing_data 也被当成了测试；Test_upper、check_test、GameTest 没有
   ↑ TestWithInit 有 __init__，pytest 给了一条警告后跳过了它
```

| 名字 | 被收集了吗 | 原因 |
|---|---|---|
| `test_ok` | ✓ | |
| `check_test` | ✗ | 以 `check` 开头 |
| **`testing_data`** | **✓** | **以 `test` 开头**——规则是 `test`，不是 `test_` |
| `Test_upper` | ✗ | 大小写敏感，`Test` 不是 `test` |
| `TestGame.test_inside_class` | ✓ | |
| `GameTest.test_in_wrong_class` | ✗ | 类名不是 `Test` 开头 |
| `TestWithInit.test_never_collected` | ✗ | 类有 `__init__`，被跳过并给出警告 |
| `game_test.py` 里的函数 | ✓ | `*_test.py` 也是规则之一 |
| `tests_game.py` 里的函数 | ✗ | `tests_` 不是 `test_` |
| `checks.py` 里的函数 | ✗ | 文件名不符合规则 |

### ⚠️ 最反直觉的一条：`testing_data`

在测试文件里写一个辅助函数，起名 `testing_data()` 或者 `test_helper()`——**pytest 会把它当成测试执行**。如果它需要参数，pytest 会报「fixture 'xxx' not found」；如果不需要参数，它会被执行一遍，然后算作一条「通过的测试」。

**辅助函数不要以 `test` 开头。** 用 `make_xxx`、`build_xxx`、`_helper` 这样的名字。

### 显式写出的文件不受命名规则限制

```text
3. 显式写出路径时，不符合命名规则的文件也会被收集
      names/checks.py::test_in_plain_file
      names/tests_game.py::test_in_tests_prefix_file
```

命名规则只用于 pytest **自己去目录里找**文件的时候。你在命令行上明确写了文件路径，它就收集那个文件。

这正是本章练习的工作方式：练习文件叫 `ch02_03_exercise.py`，平时 `pytest` 不会收集它；检查程序会显式写出它的路径来运行。

### 配置在哪里

课程的 `pyproject.toml` 里有一行：

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
```

`testpaths` 告诉 pytest：不带参数直接运行 `pytest` 时，只去 `tests/` 目录里找。所以示例和练习文件不会被意外收集。

## 4. 读懂失败报告

第 2.1 章讲过 pytest 会**重写断言**，失败时自动显示两边的值。看一个真实的失败：

```text
E   AssertionError: assert 50 == 999
     +  where 50 = parse_guess('50')
```

| 行 | 含义 |
|---|---|
| `assert 50 == 999` | 断言两边**算出来的值** |
| `+  where 50 = parse_guess('50')` | 左边的 50 **是从哪来的** |

**不需要写断言消息，pytest 已经告诉你「调用了什么、得到了什么、期望什么」。** 这是用框架最直接的好处。

失败报告的结构：

```text
================================== FAILURES ===================================
______________________ test_parametrized[50-999] ______________________   ← 哪条测试
behaviour/test_behaviour.py:18: in test_parametrized                     ← 哪个文件哪一行
E   AssertionError: assert 50 == 999                                     ← 断言
E    +  where 50 = parse_guess('50')                                     ← 值的来源
=========================== short test summary info ===========================
FAILED behaviour/test_behaviour.py::test_parametrized[50-999] - ...      ← 汇总
```

**先看最下面的 `short test summary info`**，知道有哪些失败；再往上翻到具体的那一条。

## 5. 参数化：代替循环里的 `assert`

同一组用例，两种写法（第 2、4 条的期望值是故意写错的）：

```python
CASES = [("1", 1), ("50", 999), ("100", 100), ("7", 777)]

# 写法 A：循环
def test_loop():
    for raw, expected in CASES:
        assert parse_guess(raw) == expected

# 写法 B：参数化
@pytest.mark.parametrize(("raw", "expected"), CASES)
def test_parametrized(raw, expected):
    assert parse_guess(raw) == expected
```

```text
4. 循环里的 assert vs 参数化（同一组用例，第 2、4 条是错的）
      FAILED behaviour/test_behaviour.py::test_loop - AssertionError: assert 50 == 999
      FAILED behaviour/test_behaviour.py::test_parametrized[50-999] - AssertionErro...
      FAILED behaviour/test_behaviour.py::test_parametrized[7-777] - AssertionError...
   ↑ test_loop 只报了 50 那一条；参数化把 50 和 7 两条都报了
```

**循环里的第一个 `assert` 失败后，整个测试函数就结束了**，`7 → 777` 那一条根本没被检查。你修好第一个，再跑，才会发现第二个。

**参数化把每组参数变成一条独立的测试**，一条失败不影响其他条，所有问题一次全部报出来。

### 写法

```python
@pytest.mark.parametrize(
    ("raw", "expected"),                         # 参数名，和函数参数对应
    [("1", 1), ("42", 42), ("100", 100)],        # 每个元组是一组参数
    ids=["lower", "middle", "upper"],            # 可选：每组的名字
)
def test_parse_guess_valid(raw: str, expected: int) -> None:
    assert parse_guess(raw) == expected
```

只有一个参数时可以简写：

```python
@pytest.mark.parametrize("raw", ["abc", "", "3.14"])
def test_format_error(raw: str) -> None:
    ...
```

### ⚠️ `ids` 不要用中文

`ids` 让测试名更好读：`test_parse_guess_valid[upper]` 比 `test_parse_guess_valid[100-100]` 一眼就能看懂。

但我第一版用的是中文 `ids=["下边界", "中间", "上边界"]`，`pytest -v` 的输出变成了这样：

```text
m02_testing/ch02_03_example.py::test_parse_guess_valid[\u4e0b\u8fb9\u754c] PASSED
m02_testing/ch02_03_example.py::test_parse_guess_valid[\u4e2d\u95f4] PASSED
```

**pytest 默认会把非 ASCII 字符的 id 转义成 `\u` 编码。** 反而更难读了。所以 `ids` 用英文。

## 6. `pytest.raises`：测异常

第 2.2 章那六行：

```python
try:
    parse_guess("abc")
except GuessFormatError:
    pass
else:
    raise AssertionError("预期 GuessFormatError")
```

变成两行：

```python
with pytest.raises(GuessFormatError):
    parse_guess("abc")
```

`with` 是一种语法结构（第 4.1 章细讲），这里可以读作「**在这个范围里，我预期会抛出 `GuessFormatError`**」。

| 实际发生了什么 | 结果 |
|---|---|
| 抛出了 `GuessFormatError` 或它的子类 | 通过 |
| **没有抛异常** | **失败**：`DID NOT RAISE GuessFormatError` |
| 抛出了别的类型的异常 | **失败**：那个异常原样抛出 |

```text
6. 预期的异常没有抛出
      E   Failed: DID NOT RAISE ValueError
```

**这三种行为和第 2.2 章练习 4 的 `expect_raises` 完全一样。** 如果你做过那道题，现在知道 `pytest.raises` 里面在做什么了。

### 拿到异常对象：`as excinfo`

```python
with pytest.raises(GuessFormatError) as excinfo:
    parse_guess("abc")

assert isinstance(excinfo.value, ValueError)          # excinfo.value 就是那个异常对象
assert excinfo.value.__suppress_context__ is True     # 确认用了 from None
```

### ⚠️ `match` 是正则表达式

```python
with pytest.raises(ValueError, match="必须在 [1, 100] 之间"):
    parse_guess("101")
```

被测函数抛出的消息是「数字必须在 [1, 100] 之间」。这条测试**失败了**：

```text
5. match 是正则表达式
      E   AssertionError: Regex pattern did not match.
      E     Expected regex: '必须在 [1, 100] 之间'
      E     Actual message: '数字必须在 [1, 100] 之间'
```

**两行看起来明明都有「必须在 [1, 100] 之间」，为什么不匹配？**

因为 `match` 的参数是**正则表达式**，不是普通字符串。正则里的 `[1, 100]` 不是字面上的方括号，而是「**`1`、逗号、空格、`0` 这四个字符中的任意一个**」——它只能匹配**一个**字符。

修法是 `re.escape`，把所有正则特殊字符转义掉：

```python
import re

with pytest.raises(ValueError, match=re.escape("必须在 [1, 100] 之间")):
    parse_guess("101")
```

| `match` 里有这些字符时 | 必须 `re.escape` |
|---|---|
| `.` `*` `+` `?` | 量词和通配 |
| `(` `)` `[` `]` `{` `}` | 分组和字符集 |
| `^` `$` `\|` `\` | 锚点、或、转义 |

> **为什么报错信息让人困惑**：pytest 显示的「Expected regex」是你写的那个字符串原样，
> 人眼看过去就是「方括号、1、逗号……」，很难意识到它被当成了字符集。
> 记住：**看到 `Regex pattern did not match` 而两行看起来一样，先想特殊字符。**

### `match` 用 `search` 而不是全文匹配

`match="必须在"` 能匹配「数字必须在 [1, 100] 之间」——它只要求**消息里包含**这段内容，不要求从头开始，也不要求完全相等。所以只写最关键的那几个字就行，不需要把整条消息抄下来。

> 第 1.9 章说过 Python 3.13 改了 `max([])` 的报错措辞。**`match` 依赖的正是消息文本**，
> 所以只在消息是**你自己定义的**时候用它。测试第三方库或 Python 内置的异常，判断类型就够了。

## 7. 常用命令行选项

| 选项 | 作用 |
|---|---|
| `-v` | 详细：每条测试一行，显示名字和结果 |
| `-q` | 安静：只显示点和汇总 |
| `-x` | **第一个失败就停** |
| `-k 表达式` | **只跑名字匹配的测试**，如 `-k "ch02_03 and not mutant"` |
| `-rs` | 汇总里显示 skip 的原因 |
| `--lf` | 只重跑上次失败的（last failed） |
| `--collect-only` | 只收集、不运行，看看找到了哪些测试 |
| `--tb=short` / `--tb=line` / `--tb=no` | 控制 traceback 的详细程度 |

```text
=== -x 第一个失败就停 ===
FAILED behaviour/test_behaviour.py::test_loop - Assert...
!!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!
1 failed in 0.01s
```

### ⚠️ `-q` 和 `-v` 会互相抵消

写这一章时我发现，课程的 `pyproject.toml` 原来有一行 `addopts = "-q"`（每次运行 pytest 都自动加上 `-q`）。于是：

```text
=== -q -v（相互抵消） ===
m02_testing\ch02_03_example.py .............                             [100%]
============================= 13 passed in 0.06s ==============================
```

**`-q` 和 `-v` 是同一个计数器的加和减**：一个 `-q` 减一级，一个 `-v` 加一级，两者叠加回到了默认的详细程度。所以课程里所有写着 `pytest ... -v` 的命令，实际上**看不到每条测试的名字**。

这个配置已经删掉了。教训是：**`addopts` 里的选项会和命令行选项叠加**，往里加东西之前想清楚它会影响什么。

## 8. `pytest.skip`：课程练习是怎么「跳过」的

你在跑 `pytest tests/test_m01.py` 时一直看到 `skipped`。它来自 `pytest.skip()`：

```python
def run_or_skip(fn, *args):
    try:
        return fn(*args)
    except NotImplementedError:
        pytest.skip(f"{fn.__name__} 还没完成")
```

练习骨架里的函数体是 `raise NotImplementedError(...)`。检查程序接住它，调用 `pytest.skip()`，这条测试就被标记为「跳过」而不是「失败」。

```powershell
pytest tests/test_m02.py -rs     # -rs 会列出每条 skip 的原因
```

```text
SKIPPED [1] tests\test_m02.py:45: parse_guess 还没完成
SKIPPED [1] tests\test_m02.py:764: 练习 1-3 还没写测试（collected 0 items）
```

**`skip` 用于「这条测试现在不该跑」**：功能还没写完、只在某个操作系统上有意义、依赖的服务不可用。不要用它掩盖失败的测试——那和 `except: pass` 是一回事。

## 9. ⚠️ 测试通过 ≠ 测试有用

这是本章最重要的一节，也是练习的核心。

看这两条测试：

```python
def test_middle():
    assert parse_guess("42") == 42

def test_bad():
    with pytest.raises(ValueError):
        parse_guess("abc")
```

**它们都能通过。** 但它们有用吗？

我准备了 4 个「故意改错」的 `parse_guess`：

| 改错版本 | 改了什么 |
|---|---|
| 下边界改错 | `1` 被当成超范围拒绝 |
| 上边界改错 | `100` 被当成超范围拒绝 |
| 异常类型改错 | 格式错误抛成了普通 `ValueError`，而不是 `GuessFormatError` |
| 消息改错 | 「必须在 [1, 100] 之间」改成了「必须在 1 到 100 之间」 |

然后用上面那两条测试分别去测这 4 个版本。配套测试 `test_ch02_03_mutants_pass_a_weak_suite` 的结论是：

**4 个改错版本，全部通过了这两条测试。**

- 只测 `42` → 两个边界改错都抓不住
- 只断言 `ValueError` → 异常类型改错抓不住（`GuessFormatError` 也是 `ValueError`）
- 没检查消息 → 消息改错抓不住

**这两条测试通过了，但它们什么也没保护。**

### 这叫变异测试

故意把被测代码改错（每次改一处），看测试能不能发现。能发现叫「**杀死**了这个变异体」，发现不了叫「变异体**存活**」。存活的变异体指出了测试的盲区。

这就是第 2.1 章「故意改错代码，验证测试有效」的系统化版本。第 2.1 章是手动改一次，这里是自动化地改四次。

> 真实项目里有专门的变异测试工具（比如 `mutmut`），会自动生成成百上千个变异体。
> 本课程的练习只用 4 个手写的，原理一样。

### 本章练习就是这样检查的

练习 1-3 要你**写测试**。检查程序会用 pytest 跑你的测试两轮：

1. **被测代码是对的**：你的测试应该全部通过
2. **依次换成 4 个改错版本**：每个版本下，你的测试都应该**至少失败一条**

```text
test_ch02_03_exercise_kills_mutant[lower_bound]         PASSED  ← 抓住了
test_ch02_03_exercise_kills_mutant[message_changed]     FAILED  ← 没抓住：你的测试没检查消息
```

**第二轮失败时，说明你的测试有盲区。** 去想想需要补什么用例。

## 10. 课程测试里用到的其他 pytest 功能

你在读 `tests/test_m01.py` 时可能注意到函数参数里有这些名字：

```python
def test_xxx(tmp_path: Path, capsys, monkeypatch) -> None:
```

它们叫 **fixture**：pytest 看到参数名，就自动准备好对应的东西传进来。

| fixture | 提供什么 |
|---|---|
| `tmp_path` | 一个临时目录，测试结束后自动清理 |
| `capsys` | 捕获 `print` 的输出，`capsys.readouterr().out` 拿到 |
| `monkeypatch` | 临时替换某个函数或变量，测试结束后自动恢复 |

第 1.6 章用依赖注入替代了 `monkeypatch`，第 8.1 章讲 Mock、第 8.2 章讲 fixture 时会正式展开。

---

# 二、动手练习

打开 `ch02_03_exercise.py`。**这一章你要写的是测试本身。**

文件里已经写好了被测代码 `parse_guess` 和三个异常类。

## 练习 1（基础）· 合法输入：用参数化

写一个参数化的测试函数，测至少 3 个合法输入。

检查程序里有两个改错版本和这一题有关：一个把下边界改错了，一个把上边界改错了。**想清楚你的用例里必须包含哪两个值。**

## 练习 2（基础）· 非法输入：区分两种错误

写两个参数化的测试函数：

- 一个测「不是整数」的输入，断言 `GuessFormatError`
- 一个测「超出范围」的输入，断言 `GuessRangeError`

**不要只写 `pytest.raises(GuessError)`**——检查程序里有一个改错版本把格式错误抛成了普通 `ValueError`。

## 练习 3（进阶）· 检查错误消息

断言 `parse_guess("101")` 的错误消息里包含「必须在 [1, 100] 之间」。

**先不加 `re.escape` 跑一次**，看看第 6 节说的那个困惑的报错，再改对。

## 练习 4（基础）· pytest 会收集哪些测试

填 `DISCOVERY` 字典，判断 10 个名字会不会被收集。**不要先跑示例**，先自己判断。检查程序会真的搭一遍目录、跑一遍 pytest 来核对。

## 怎么验证

```powershell
# 只跑你写的测试，看它们本身过没过
pytest m02_testing/ch02_03_exercise.py -v

# 完整检查：正确版本 + 4 个改错版本 + 练习 4
pytest tests/test_m02.py -k ch02_03 -v
```

完整检查要跑十几次 pytest，大约需要 10-20 秒。

---

# 三、常见错误

| # | 错误 | 表现 | 怎么避免 |
|---|---|---|---|
| **1** | **断言写在 `if __name__ == "__main__"` 里** | `collected 0 items`，退出码 5 | 断言放进 `test_` 函数 |
| **2** | **测试函数名不是 `test` 开头** | 不被收集，没有任何提示 | 看收集数量 |
| **3** | **辅助函数以 `test` 开头** | 被当成测试执行 | 用 `make_`、`build_`、`_` 开头 |
| **4** | **测试类有 `__init__`** | 整个类被跳过，只有一条警告 | 不要给测试类写 `__init__` |
| **5** | **在循环里写 `assert`** | 只报第一个失败 | `@pytest.mark.parametrize` |
| **6** | **`match` 里有特殊字符没转义** | `Regex pattern did not match`，两行看起来一样 | `re.escape(...)` |
| **7** | **用 `match` 测第三方/内置异常的消息** | 升级版本后失败 | 只对自己定义的消息用 `match` |
| **8** | **`ids` 用中文** | 显示成 `\u4e0b\u8fb9\u754c` | `ids` 用英文 |
| **9** | **`addopts` 里加了 `-q`** | 命令行的 `-v` 失效 | 想清楚 `addopts` 会叠加 |
| **10** | **测试只覆盖中间值、只断言基类** | 测试通过，但抓不住边界和类型错误 | 用改错版本检验 |

**第 1-4 条的共同点是「测试没跑，但你以为它跑了」。** 养成习惯：每次跑完 pytest，看一眼收集数量对不对。

---

# 四、本章小结

```text
手写测试的四个问题：忘了调用 / 第一个失败就停 / 测异常要六行 / 没有汇总
        ↓
pytest：自动发现、逐条报告、汇总
   ├─ ⚠️ collected 0 items → 退出码 5
   └─ 发现规则：test_*.py / *_test.py；函数以 test 开头；Test 类无 __init__
        └─ ⚠️ testing_data 会被收集
        ↓
失败报告：assert 两边的值 + where 来源
        ↓
parametrize：每组参数一条独立测试，全部问题一次报出
        ↓
pytest.raises：没抛 → DID NOT RAISE；抛错类型 → 原样抛出
   └─ ⚠️ match 是正则 → re.escape
        ↓
⚠️ -q 和 -v 互相抵消
        ↓
⚠️ 测试通过 ≠ 测试有用 → 用改错版本（变异测试）检验
```

一句话总结：**测试框架解决的是「测试有没有跑」的问题，解决不了「测试有没有用」的问题。** 后者只能靠你自己：故意把代码改错，看测试能不能发现。

## M2 回顾

| 章 | 解决了什么问题 |
|---|---|
| 2.1 | 手动测试 → `assert`；**`-O` 会删掉 `assert`**；故意改错验证测试 |
| 2.2 | 自己抛异常；**`except` 顺序**；自定义异常；手写异常测试 |
| 2.3 | `assert` → `pytest`；**`collected 0 items`**；参数化；**变异测试** |

## 下一个模块

M3 讲工程结构。第一章 [**3.1 模块、包与 `import` 机制**](03_01_模块包与import机制.md) 会回答本章留下的一个问题：为什么 `if __name__ == "__main__":` 里的代码在 pytest 下不执行？以及为什么课程一直要求你用 `python -m m02_testing.xxx` 而不是 `python m02_testing/xxx.py`。

---

# 五、自测

1. 手写测试有哪四个根本问题？
2. 学习记录第 10 天的测试文件为什么在 pytest 下 `collected 0 items`？直接用 `python` 运行它会怎样？
3. pytest 一个测试都没收集到时，退出码是多少？为什么说这个设计是对的？
4. pytest 默认的文件、函数、类的发现规则分别是什么？
5. `testing_data()` 会被 pytest 收集吗？`Test_upper()` 呢？为什么？
6. 有 `__init__` 的测试类会怎样？
7. `pytest checks.py` 会收集 `checks.py` 里的 `test_` 函数吗？`pytest .` 呢？
8. 失败报告里的 `+  where 50 = parse_guess('50')` 是什么意思？
9. 循环里写 `assert` 和用 `parametrize`，在有多个用例失败时有什么区别？
10. `ids` 为什么不要用中文？
11. `pytest.raises` 在三种情况下分别怎样：抛了预期异常、没抛异常、抛了别的异常？
12. `match="必须在 [1, 100] 之间"` 为什么匹配不上「数字必须在 [1, 100] 之间」？怎么改？
13. `match` 要求消息完全相等吗？什么时候不该用 `match`？
14. `-q` 和 `-v` 同时出现会怎样？为什么课程删掉了 `addopts = "-q"`？
15. `pytest.skip` 适合用在什么场景？不该用在什么场景？
16. 「测试通过」和「测试有用」有什么区别？什么是变异测试？
17. 只测 `parse_guess("42")` 和 `pytest.raises(ValueError)` 的测试，为什么抓不住那 4 个改错版本？

<details>
<summary>参考答案</summary>

1. **忘了调用测试函数就不跑**且没有提示；**第一个 `assert` 失败后面的就不执行**；**测异常要写六行**且漏了 `else` 就是假测试；**没有汇总**。
2. 断言写在 `if __name__ == "__main__":` 里，而 pytest 是**导入**测试文件，导入时 `__name__` 不是 `"__main__"`，整个块被跳过；再加上文件里**没有 `test_` 开头的函数**。直接用 `python` 运行会打印「所有测试通过」，退出码 0——看起来一切正常。
3. **5**。设计是对的，因为「什么都没测」不该被当成成功，CI 看到非 0 退出码会判定失败。对比 `sys.exit()` 少做了事却返回 0。
4. 文件：`test_*.py` 或 `*_test.py`；函数：**以 `test` 开头**；类：以 `Test` 开头、**没有 `__init__`**，类里的方法同样以 `test` 开头。
5. `testing_data()` **会**被收集，因为规则是「以 `test` 开头」，不是「以 `test_` 开头」。`Test_upper()` **不会**，因为大小写敏感，`Test` 不是 `test`。
6. 整个类**被跳过**，pytest 给出一条 `PytestCollectionWarning: cannot collect test class ... because it has a __init__ constructor`。
7. `pytest checks.py` **会**——显式写出的文件不受命名规则限制。`pytest .` **不会**——pytest 自己去目录里找文件时才用命名规则，`checks.py` 不符合。
8. 断言左边的那个 50 **是调用 `parse_guess('50')` 得到的**。pytest 的断言重写不仅显示两边的值，还显示值的来源。
9. 循环里的 `assert` 在**第一个失败后整个测试函数就结束了**，后面的用例根本没被检查，你一次只能看到一个问题；`parametrize` 把每组参数变成**一条独立的测试**，所有失败一次全部报出。
10. 因为 pytest 默认会把非 ASCII 字符的 id **转义成 `\u4e0b\u8fb9\u754c` 这种编码**，反而更难读。
11. 抛了预期异常（或其子类）→ **通过**；没抛异常 → **失败**，报 `DID NOT RAISE`；抛了别的类型 → **失败**，那个异常原样抛出。
12. 因为 `match` 是**正则表达式**，`[1, 100]` 在正则里是「`1`、逗号、空格、`0` 中的**任意一个**字符」，只能匹配一个字符。改成 `match=re.escape("必须在 [1, 100] 之间")`。
13. **不要求**，它用的是搜索，只要消息里**包含**匹配的内容就行。不该用在**第三方库或 Python 内置异常**上——它们的消息可能随版本改变（比如 3.13 的 `max([])`），只对自己定义的消息用 `match`。
14. **互相抵消**，回到默认的详细程度——它们是同一个计数器的加和减。课程删掉 `addopts = "-q"` 是因为它会和命令行的 `-v` 叠加，让课程里所有 `pytest ... -v` 的命令都看不到每条测试的名字。
15. 适合「这条测试现在不该跑」的场景：功能还没写完、只在某个系统上有意义、依赖的服务不可用。**不该用来掩盖失败的测试**——那和 `except: pass` 是一回事。
16. 「通过」只说明测试在**当前代码**上不报错；「有用」是说当代码**出了 bug 时测试能发现**。变异测试就是故意把被测代码改错（每次改一处），看测试能不能发现：能发现叫「杀死」变异体，发现不了叫「存活」，存活的变异体指出了测试的盲区。
17. 只测 `42` 这个中间值，**两个边界改错（1 和 100）都碰不到**；只断言 `ValueError`，而 `GuessFormatError` 也是 `ValueError`，所以**异常类型改错**抓不住；**没有检查消息**，所以消息改错也抓不住。

</details>
