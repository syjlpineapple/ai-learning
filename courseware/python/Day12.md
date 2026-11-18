# Day 12 · 测试覆盖、类型注解的边界与异常粒度

> **学习日** 2026-10-26（09:17 - 10:51，6 轮对话）
> **对应代码** [`dailypractice/Day12/`](../../dailypractice/Day12/)（`history.py` / `test_history.py`）
> **原始对话** `courseware/_raw/markdown/03_Python每日练习出题.md`（对话里称「Day 12」）

> 这是 `history.py` 重写的第二遍。四遍的侧重分别是：
> Day11 读写与校验 → **Day12 测试覆盖** → Day13 日志 → Day14 分层校验与错误语义。

## 本节掌握

- 测试覆盖与测试隔离两个概念
- `str | Path` 联合类型；`Path` 能直接传给 `open()`
- **类型注解不做运行时校验**——`-> list[int]` 不保证返回的是整数列表
- 为什么 `except Exception` 在工程代码里是坏做法
- `json.load()` 只负责解析，不负责业务校验
- Python 的**链式比较**：`a == b == c` 不是你以为的意思
- 读文件不会清空文件；`write_text()` 才会覆盖

---

# 第一部分 · 知识讲解

## 1. 测试覆盖与测试隔离

**测试覆盖**（coverage）指测试跑到了多少种情况。Day11 的测试只覆盖了 4 种，今天补到 6 种：

| 场景 | 构造数据 | 验证什么 |
|---|---|---|
| 正常读取 | `[10, 20, 30]` | 基本功能 |
| 文件不存在 | 不创建文件 | `FileNotFoundError` 被处理 |
| JSON 格式错误 | `hello` | `JSONDecodeError` 被处理 |
| 顶层结构错误 | `{"guess": 10}` | 拒绝字典 |
| 元素类型错误 | `[10, "abc", 30]` | 拒绝非整数元素 |
| 数字越界 | `[10, 101]` | 拒绝范围外的数 |

关键认识：**测试通过不代表功能都正确，只代表「被测到的那些情况」正确。** Day11 的测试全过，但顶层是字典的情况压根没测——那个 bug 是靠代码审查发现的，不是测试。

**测试隔离**（isolation）指测试之间、测试与真实数据之间互不影响。三条具体要求：

- 不碰真实文件（用临时目录）
- 不依赖执行顺序（第 3 个测试不能依赖第 2 个留下的状态）
- 测完自动清理（不留垃圾文件）

`tempfile.TemporaryDirectory()` 一次满足这三条：它在系统临时区建独立目录，离开 `with` 块后整个删除。

## 2. 路径：`str` 还是 `Path`

编辑器报「应为类型 'str'，但实际为 'Path'」，是因为函数标注了 `filename: str`，而 `Path(temp_dir) / "history.json"` 得到的是 `Path` 对象。

两种解法：

```python
# 方法一：调用时转成字符串
save_history([10, 20, 30], str(filename))

# 方法二：改函数签名，两种都接受（更推荐）
def save_history(history: list[int], filename: str | Path) -> None: ...
```

`str | Path` 是 Python 3.10+ 的**联合类型**写法，意思是「这两种类型都行」。更早的版本要写 `Union[str, Path]`（需 `from typing import Union`）。

**但要分清两件事：** 编辑器的类型提示和程序能否运行是两回事。`open()` 本身完全支持 `Path` 对象，所以直接传 `Path` 运行起来**不会报错**——报警的只是类型检查器，它在说「你的标注和实际用法不一致」。

> `pathlib.Path` 是现代 Python 处理路径的推荐方式。`Path(a) / b` 这种用斜杠拼接路径的写法，比 `os.path.join(a, b)` 直观，而且自动处理不同操作系统的分隔符差异。

## 3. 类型注解不等于运行时校验

这是今天最重要的概念。

```python
def load_history(filename: str) -> list[int]:
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)      # 文件内容是 {"guess": 10} 时，返回的是 dict
    except Exception:
        return []
```

函数标注的返回类型是 `list[int]`，但实际返回了 `dict`——**Python 不会报错**。类型注解是写给人和静态检查工具（mypy、pyright）看的，运行时完全不做检查。

后果要到用的时候才爆：

```python
history = load_history("history.json")   # 实际是 {"guess": 10}
history.append(20)
# AttributeError: 'dict' object has no attribute 'append'
```

报错点和出问题的地方隔了很远，排查时容易找错方向。

> 结论：**从外部来的数据（文件、API、用户输入、模型输出）必须主动校验实际类型和内容，不能依赖类型注解。** 这也是 Day11 要逐层检查顶层结构和每个元素的根本理由。
>
> 想要运行时校验，得自己写判断，或者用 Pydantic 这类库（它会在构造对象时真的检查类型）。

## 4. `json.load()` 的边界：解析 ≠ 校验

`json.load()` 的职责只有一件：把 JSON 文本转成 Python 对象。**它不关心转出来的东西符不符合你的业务要求。**

| 文件内容 | `json.load()` 返回 | 报错吗 |
|---|---|---|
| `[10, 20, 30]` | `list` | 不报 |
| `["abc", 101]` | `list` | **不报** |
| `{"guess": 10}` | `dict` | **不报** |
| `"hello"`（带引号） | `str` | **不报** |
| `123` | `int` | **不报** |
| `null` | `None` | **不报** |
| `hello`（不带引号） | —— | 抛 `JSONDecodeError` |

只有**语法**不合法才会抛异常。`["abc", 101]` 是完全合法的 JSON，解析一定成功——但它不是合法的猜测历史。

所以数据校验要分两层：

1. **语法层**：能不能解析成 JSON（`json.load()` 负责，失败抛 `JSONDecodeError`）
2. **业务层**：解析出来的东西是不是我要的（**只能自己写**）

## 5. 为什么不能 `except Exception`

```python
except Exception:
    return []
```

这一行会把下面这些完全不同的情况统统变成 `[]`：

| 真实情况 | 应有的反应 |
|---|---|
| 文件不存在 | 正常，这是第一次运行 |
| JSON 语法损坏 | 数据坏了，可能要告警或备份 |
| 没有读取权限 | 环境配置问题，要让人知道 |
| 代码本身有 bug（比如拼错变量名导致 `NameError`） | **必须暴露出来修** |

两个危害：

**一、调用方无法判断 `[]` 的含义。** 是「还没有历史」还是「读取失败了」？两者的后续处理完全不同。

**二、把程序自己的 bug 伪装成了正常结果。** 这是更严重的。`except Exception` 会连 `NameError`、`TypeError` 这类代码错误一起吞掉，程序不崩溃、不报错，只是行为悄悄变得不对。这种 bug 极难发现。

> 原则：**只捕获你预料到、并且知道该怎么处理的异常。** 预料之外的异常应该让它往上抛——崩溃比静默地错下去好。

## 6. Python 的链式比较

```python
assert load_history(not_exist) == [10, 20, 30] == []
```

这行**不是**「判断结果等于其中之一」，Python 把它当**链式比较**处理，等价于：

```python
assert load_history(not_exist) == [10, 20, 30] and [10, 20, 30] == []
```

后半截 `[10, 20, 30] == []` 永远为假，所以整个断言必然失败。

链式比较本身是 Python 的好特性，前面写过的 `1 <= x <= 100` 就是它，等价于 `1 <= x and x <= 100`。但用在 `==` 上几乎都是写错了——因为「等于 A 或者等于 B」应该写成：

```python
assert result in ([10, 20, 30], [])
```

## 7. 读文件不会清空文件

当时的疑问：测试里连续 `write_text()` 再读取，前面的内容是被读取操作清掉的吗？

**不是。读取操作不修改文件。**

| 操作 | 对文件的影响 |
|---|---|
| `read_text()` / `json.load()` | 只读，不动文件 |
| `write_text()` | 写入，**默认覆盖**原内容 |
| `open(f, "w")` | 打开即清空 |
| `open(f, "a")` | 追加到末尾 |

测试里文件内容不断变化，是因为每次 `write_text()` 都覆盖了一遍，与读取无关。可以自己验证：

```python
filename.write_text("hello", encoding="utf-8")
print(load_history(str(filename)))              # []     ← 校验不通过
print(filename.read_text(encoding="utf-8"))     # hello  ← 文件内容还在
```

**`load_history()` 返回 `[]` 只说明「没拿到合法数据」，不代表文件被清空了。**

## 8. 为什么用 `write_text()` 而不是 `save_history()` 构造测试数据

六个测试里，只有第一个用 `save_history()`，后面五个都用 `write_text()` 直接写文件。

原因：**要测的是「读取函数面对坏数据时的行为」，而 `save_history()` 写不出坏数据。** 它只会写出格式正确的 JSON——没法用它造出 `hello` 这种语法损坏的内容。

> 这是测试里的常见手法：**绕过正常的写入路径，直接构造被测函数需要面对的输入。** 后面 Day 21 学 Mock 时，手法变了（替换掉整个网络请求），目的是一样的。

---

# 第二部分 · 当天的练习

## 一、题目

补齐 `test_history.py`，覆盖上面表格里的 6 种场景。要求用 `tempfile.TemporaryDirectory()` 隔离、用 `Path.write_text()` 构造错误数据、每个场景都要有有效的 `assert`。

另外回答两个思考题：为什么 `except Exception: return []` 不适合企业应用？文件内容是 `["abc", 101]` 时它会返回什么？

## 二、两个坑

### 坑 1：参数顺序传反了

```python
save_history(str(filename), [10, 20, 30])
```

而 Day11 的函数定义是 `save_history(history, filename)`，所以这样传实际上是「把文件名当历史记录、把列表当文件名」。

> 这类错误靠类型注解能提前发现——`filename: str` 收到 `list` 时，编辑器会直接标红。前提是**注解写对了**。
>
> 后来 Day12 的 `history.py` 把签名改成了 `save_history(filename, data)`，让文件名在前。这个顺序更符合习惯（先说操作哪个文件），但要注意**它和 Day11 的签名不兼容**——同名函数换了参数顺序，如果有旧代码调用就会出错，而且因为两个参数类型不同（`str` 和 `list`），出错方式会很诡异。

### 坑 2：链式比较写成了断言

```python
assert load_history(not_exist) == [10, 20, 30] == []
```

见知识讲解第 6 节。正确写法：

```python
assert load_history(str(not_exist)) == []
```

## 三、最终代码

`test_history.py`：

```python
import tempfile
from pathlib import Path

from dailypractice.Day12.history import load_history
from dailypractice.Day12.history import save_history


def test_history():
    with tempfile.TemporaryDirectory() as tmpdir:
        filename = Path(tmpdir) / "history.json"

        # 测试 1：正常保存和读取
        save_history(str(filename), [10, 20, 30])
        assert load_history(str(filename)) == [10, 20, 30]

        # 测试 2：文件不存在
        not_exist = Path(tmpdir) / "not_exist.json"
        assert load_history(str(not_exist)) == []

        # 测试 3：JSON 格式错误
        filename.write_text("hello", encoding="utf-8")
        assert load_history(str(filename)) == []

        # 测试 4：JSON 顶层结构不是列表
        filename.write_text('{"guess": 10}', encoding="utf-8")
        assert load_history(str(filename)) == []

        # 测试 5：列表中包含非整数
        filename.write_text('[10, "abc", 30]', encoding="utf-8")
        assert load_history(str(filename)) == []

        # 测试 6：数字超出 1～100 的范围
        filename.write_text("[10, 101]", encoding="utf-8")
        assert load_history(str(filename)) == []


test_history()
```

六个场景全部覆盖，比 Day11 的测试完整得多。所有测试都在同一个临时目录里完成，退出 `with` 后自动清理。

## 四、现在回头看

### 一、`load_history()` 丢了 `encoding="utf-8"`

```python
# Day11
with open(filename, "r", encoding="utf-8") as f:

# Day12 —— encoding 没了
with open(filename) as f:
```

这是个**退步**，而且是隐藏的：六个测试的数据全是 ASCII 字符，用系统默认编码也能读出来，所以测试全过。

但这是真 bug，不是风格问题。实测（Windows，locale 首选编码 `cp936`，Python 3.13.2）：

```python
# 用 UTF-8 写入含中文的 JSON，模拟历史文件被手改过
target.write_text(json.dumps(["中文备注", 10], ensure_ascii=False), encoding="utf-8")

load_history_day11(target)   # []  ← 正常走到校验，因为有字符串元素而被拒绝
load_history_day12(target)   # UnicodeDecodeError: 'gbk' codec can't decode byte 0xad
```

**Day12 版本直接崩溃。** 因为它只捕获了 `FileNotFoundError` 和 `JSONDecodeError`，
`UnicodeDecodeError` 不在其中，会一路向上抛。

根因是**写读不对称**：写入端用 `encoding="utf-8"` 加 `ensure_ascii=False`（所以中文以 UTF-8 字节落盘），
读取端却用系统默认编码（中文 Windows 上是 GBK）。这是编码问题最典型的成因。

> 所以涉及文本文件的 `open()` 一律显式写 `encoding="utf-8"`，读写两端都要写。
> 注意：如果你跑脚本时设了 `PYTHONUTF8=1`（仓库 README 里为了解决控制台乱码推荐过），
> 这个 bug 会被掩盖——环境变量让默认编码变成了 UTF-8。**这类「在我机器上好着呢」的问题，
> 根源往往就是某个环境变量。**

### 二、类型注解退化了

```python
# Day11
def save_history(history: list[int], filename: str) -> None:
def load_history(filename: str) -> list[int]:

# Day12
def save_history(filename: str, data: list):          # 少了 -> None，list 没写元素类型
def load_history(filename: str) -> list:              # list 没写元素类型
```

`list` 和 `list[int]` 的区别见 Day06。这里既然函数明确只接受整数列表，就该标 `list[int]`。

### 三、`test_history()` 在模块顶层被调用

最后一行直接 `test_history()`，没有 `if __name__ == "__main__":` 保护。后果是用 pytest 跑时**测试会执行两遍**：

1. pytest 导入这个模块时，顶层那行调用执行一次
2. pytest 发现 `test_history` 函数，再执行一次

测试是幂等的，所以结果不受影响，但这是个坏习惯：导入一个模块不该产生副作用（Day10 的核心教训）。正确做法是去掉顶层调用，交给 pytest 发现——或者加上入口保护。

### 四、六个断言挤在一个测试函数里

任何一条失败，后面的都不会执行，报错信息也只说「第几行断言失败」。拆成六个独立的 `test_` 函数更好：一次能看到全部失败项，函数名本身就是场景说明。这正是 Day 21 学 pytest 之后能改进的地方。

## 五、复习自测

1. 「测试通过」能说明功能都正确吗？
2. `tempfile.TemporaryDirectory()` 满足了测试隔离的哪几条要求？
3. 把 `Path` 对象传给标注了 `filename: str` 的函数，运行时会报错吗？
4. `-> list[int]` 能保证函数不返回字典吗？
5. `except Exception: return []` 有哪两个危害？
6. 文件内容是 `["abc", 101]` 时，`json.load()` 会抛异常吗？返回什么？
7. `assert x == [1, 2] == []` 实际在判断什么？
8. 连续 `write_text()` 再读取，文件内容是被读取操作清掉的吗？
9. 为什么构造损坏数据要用 `write_text()` 而不是 `save_history()`？

<details>
<summary>参考答案</summary>

1. 不能。只能说明**被测到的那些场景**正确。Day11 的测试全过，但「顶层是字典」的场景根本没测到。
2. 三条都满足：独立临时目录（不碰真实数据）、每个测试用自己的文件（不依赖执行顺序）、退出 `with` 自动删除（不留垃圾）。
3. 不会。`open()` 原生支持 `Path` 对象，报警的只是编辑器的类型检查器，它在提示标注和实际用法不一致。
4. 不能。类型注解不做运行时检查，返回 `dict` 也不报错。错误要等到调用方执行 `.append()` 之类的操作时才暴露成 `AttributeError`。
5. 一是调用方无法区分 `[]` 代表「没有数据」还是「读取失败」；二是把程序自身的 bug（`NameError`、`TypeError` 等）也吞掉，让错误静默发生。
6. 不会抛异常，正常返回列表 `["abc", 101]`。`json.load()` 只检查 JSON 语法，不检查业务规则。
7. 链式比较，等价于 `x == [1, 2] and [1, 2] == []`。后半截永远为假，所以断言必然失败。
8. 不是。读取不修改文件。内容变化是每次 `write_text()` 覆盖导致的，`load_history()` 返回 `[]` 只说明校验没通过。
9. 因为 `save_history()` 只能写出格式正确的 JSON，造不出 `hello` 这种语法损坏的内容。测试需要直接构造被测函数要面对的输入。

</details>
