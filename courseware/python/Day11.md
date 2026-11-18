# Day 11 · 文件读写与 JSON 数据处理

> **学习日** 2026-10-23（13:31 - 14:31，8 轮对话）
> **对应代码** [`dailypractice/Day11/`](../../dailypractice/Day11/)（`history.py` / `test_history.py` / `error.json`）
> **原始对话** `courseware/_raw/markdown/03_Python每日练习出题.md`（对话里称「第十一天」）

## 本节掌握

- JSON 是什么，为什么 AI 应用离不开它
- `json.dump` / `load` / `dumps` / `loads` 四个方法的区别
- `ensure_ascii=False` 和 `indent=2` 的作用
- `with open(...)` 为什么能自动关闭文件
- JSON 与 Python 的类型对照，以及 **`bool` 是 `int` 的子类**这个坑
- 区分「文件不存在」和「内容损坏」两类错误
- 校验顺序：先验顶层结构，再验每个元素
- 用 `tempfile` 隔离测试，不污染真实数据

---

# 第一部分 · 知识讲解

## 1. JSON 是什么

JSON（JavaScript Object Notation）是一种文本格式的数据交换标准。它的地位是：**几乎所有 Web API 和 AI 接口都用它传数据**。

学它的直接理由：调用大模型 API 时，请求参数是 JSON，返回结果也是 JSON；程序的配置文件、保存的用户数据，大多也是 JSON。

一个 JSON 文本长这样：

```json
{
  "name": "Alice",
  "guesses": [23, 50, 42],
  "won": true
}
```

和 Python 的字典几乎一样，这不是巧合——JSON 的设计就是「结构化数据的最小公约数」，所以能和大多数语言的基本数据结构对应上。

## 2. Python 与 JSON 的类型对照

| JSON | Python |
|---|---|
| `object` `{}` | `dict` |
| `array` `[]` | `list` |
| `string` | `str` |
| `number`（整） | `int` |
| `number`（小数） | `float` |
| `true` / `false` | `True` / `False` |
| `null` | `None` |

注意两个方向都不是完全对等的：Python 的元组 `(1, 2)` 会被写成 JSON 数组 `[1, 2]`，读回来就变成列表了；Python 字典的键如果是整数，写成 JSON 会变成字符串。**JSON 不是 Python 对象的快照，只是数据的共同表示。**

## 3. 四个方法：dump / load / dumps / loads

这是最容易混的地方。记住规则：**带 `s` 的操作字符串（string），不带 `s` 的操作文件（file）。**

| 方法 | 方向 | 对象 |
|---|---|---|
| `json.dump(data, file)` | Python → JSON | 写进**文件** |
| `json.load(file)` | JSON → Python | 从**文件**读 |
| `json.dumps(data)` | Python → JSON | 返回**字符串** |
| `json.loads(text)` | JSON → Python | 从**字符串**读 |

所以写文件有两种等价写法：

```python
# 写法 A：直接写文件
with open(filename, "w", encoding="utf-8") as f:
    json.dump(history, f, ensure_ascii=False, indent=2)

# 写法 B：先转成字符串，再写文件
text = json.dumps(history, ensure_ascii=False, indent=2)
with open(filename, "w", encoding="utf-8") as f:
    f.write(text)
```

写法 A 更常用。写法 B 的价值是：拿到字符串后可以先打印出来看、或者发给 API，不一定非要落盘。

## 4. 两个常用参数

### `ensure_ascii=False`

默认是 `True`，此时非 ASCII 字符会被转成 Unicode 转义序列：

```python
json.dumps({"name": "张三"})
# '{"name": "\\u5f20\\u4e09"}'      ← 中文变成了转义码

json.dumps({"name": "张三"}, ensure_ascii=False)
# '{"name": "张三"}'                 ← 中文原样保留
```

两种都是合法 JSON，读回来都是「张三」。区别只在**人能不能直接看懂文件内容**。所以凡是人要看的 JSON 文件，都应该加 `ensure_ascii=False`。

### `indent=2`

不加 `indent` 时，JSON 全挤在一行；加了之后会换行并缩进指定的空格数：

```json
[
  10,
  20,
  30
]
```

代价是文件变大。所以**配置文件、要人读的数据加 `indent`；网络传输、日志不加**（省带宽和存储）。

## 5. `with open(...)` 与文件模式

```python
with open(filename, "w", encoding="utf-8") as f:
    ...
```

三个要点：

**一、`with` 保证文件被关闭。** 它是 Python 的上下文管理器语法：离开这个代码块时（无论是正常结束还是中途抛异常）都会自动调用 `f.close()`。不用 `with` 就得自己写 `try/finally`，一旦忘记关闭，数据可能留在缓冲区没写进磁盘，文件句柄也会泄漏。

**二、第二个参数是打开模式：**

| 模式 | 含义 | 文件不存在时 | 文件已存在时 |
|---|---|---|---|
| `"r"` | 只读 | 抛 `FileNotFoundError` | 从头读 |
| `"w"` | 写入 | 创建 | **清空原内容** |
| `"a"` | 追加 | 创建 | 从末尾续写 |
| `"x"` | 独占创建 | 创建 | 抛 `FileExistsError` |

`"w"` 会清空原文件，这点要当心——存历史记录时用 `"w"` 是对的（每次写完整列表），但如果想往日志里追加就必须用 `"a"`。

**三、`encoding="utf-8"` 不能省。** Windows 上 Python 默认用系统编码（常见是 GBK），写中文会乱码或报错。**所有涉及文本文件的 `open()` 都应该显式写 `encoding="utf-8"`。**

## 6. 重要的坑：`bool` 是 `int` 的子类

Python 里 `True` 和 `False` 实际上是整数 `1` 和 `0`：

```python
isinstance(True, int)   # True  ← 布尔值通过了整数检查
True + True             # 2
```

这意味着用 `isinstance(x, int)` 校验「必须是整数」时，**`True` 会被放进来**。而 JSON 里的 `true` 会变成 Python 的 `True`，所以这是真实会遇到的情况：

```json
[10, true, 30]
```

如果校验写成 `isinstance(i, int)`，这份数据会被当成合法的猜测记录，`true` 被当作数字 1 参与后续计算。

要排除布尔值，得用 `type()` 做精确比较：

```python
type(i) is not int      # True 会被拒绝，因为 type(True) 是 bool 而不是 int
```

| 写法 | `10` | `True` | 子类实例 |
|---|---|---|---|
| `isinstance(i, int)` | 通过 | **通过（问题所在）** | 通过 |
| `type(i) is int` | 通过 | 拒绝 | 拒绝 |

> 一般情况下 Python 推荐 `isinstance`（它支持继承，更灵活）。但「必须恰好是 int、不接受 bool」是少数应该用 `type() is` 的场景。
>
> 顺带修正仓库 `README.md` 待办里的一条：那里写着「Day12、Day14 用 `type(x) != list` 的地方该换成 `isinstance`」。
> 对 `list` 的检查这么改没问题；但**对 `int` 的检查不能改**——换成 `isinstance` 就会让 `True` 通过。

## 7. 两类错误要分开

读文件至少有两种独立的失败方式：

| 异常 | 什么情况 | 含义 |
|---|---|---|
| `FileNotFoundError` | 文件不存在 | 还没有数据，是**正常状态** |
| `json.JSONDecodeError` | 文件在，但内容不是合法 JSON | 数据**损坏了**，是异常状态 |

必须分开处理，因为它们的含义完全不同：第一次运行程序时没有历史文件，这很正常，返回空列表即好；而文件存在却解析失败，说明数据被破坏了，可能需要告警或备份。

还有第三类：**JSON 语法合法，但内容不符合业务要求**，比如顶层是字典而不是列表、列表里混了字符串、数字超出 1~100。这类不会抛异常，必须自己写校验。

> 今天最重要的一句话：**外部数据不能因为来自自己的文件就默认它一定正确。** 文件可能被手改过、被别的程序写坏、是上个版本的格式。这个习惯以后用在校验 API 响应和大模型输出上是一样的。

---

# 第二部分 · 当天的练习

## 一、题目

实现 `history.py`：

```python
def save_history(history: list[int], filename: str) -> None: ...
def load_history(filename: str) -> list[int]: ...
```

`load_history()` 的要求：

| 情况 | 预期 |
|---|---|
| 文件合法 | 返回数字列表 |
| 文件不存在 | 返回 `[]` |
| JSON 损坏 | 返回 `[]`，不崩溃 |
| 顶层不是列表 | 返回 `[]` |
| 元素不是整数 | 返回 `[]` |
| 数字不在 1~100 | 返回 `[]` |

再写 `test_history.py`，用 `tempfile` 隔离测试文件。

## 二、第一版：漏了顶层结构校验

```python
def load_history(filename: str) -> list[int]:
    try:
        with open(filename, "r", encoding="utf-8") as f:
            try:
                ls = json.load(f)
                for i in ls:                        # ← 直接就开始遍历
                    if not type(i) == int:
                        raise TypeError("类型错误")   # ← 抛异常而不是返回 []
                    if not 1 <= i <= 100:
                        raise ValueError("数字范围要在1~100")
            except json.decoder.JSONDecodeError:
                return []
        return ls
    except FileNotFoundError:
        return []
```

### 坑 1：没验证顶层是不是列表

文件内容是 `{"guess": 10}` 时，`ls` 是字典。`for i in ls:` 遍历字典拿到的是**键**，也就是字符串 `"guess"`，于是抛 `TypeError`——而这个异常没人捕获，程序直接崩。

文件内容是 `10` 时更直接：`for i in 10` 抛 `TypeError: 'int' object is not iterable`。

**正确顺序是先验外层容器，再验里面的元素：**

```python
if type(ls) is not list:
    return []
for i in ls:
    ...
```

> 规律：校验嵌套数据要**从外往里逐层确认**。跳过外层直接访问内层，是处理 JSON、API 响应时最常见的崩溃原因。

### 坑 2：校验失败时抛异常，但要求是返回 `[]`

题目要求「不要让程序直接崩溃」，而 `raise TypeError` 把问题丢给了调用方，调用方没准备接就崩了。

这里需要**明确约定**：`load_history()` 对所有「数据不可用」的情况统一返回 `[]`。
（注：这是本节的设计选择，不是唯一答案。Day 13、Day 14 会重新讨论「该返回空值还是该抛异常」，那时的结论不一样。）

## 三、第二版：逻辑反了的那个 `not`

改完顶层校验后，测试跑出 `AssertionError`——保存了 `[10, 20, 30]`，读回来却是 `[]`。

问题出在这一行：

```python
if not type(i) != int:
    return []
```

**多写了一个 `not`，判断整个反了。** 代入 `i = 10` 推一遍：

1. `type(10)` 是 `int`
2. `type(10) != int` → `False`
3. `not False` → `True`
4. 条件成立，`return []`

于是**合法的整数全部被判为非法**，而真正的字符串反而能通过。

改对：

```python
if type(i) is not int:
    return []
```

> 这个 bug 的价值在于它说明了两件事：
>
> **一、`not`、`!=`、`==` 混用极易出错。** 看到 `not x != y` 这种双重否定，停下来代入一个具体值手算一遍。能用 `is not` 直接表达的，就不要用 `not ... !=`。
>
> **二、测试真的会抓到 bug。** 这是 Day 07 写的第一个 `assert` 第一次发挥实际作用——如果只是手动跑一下游戏，这个错误很可能被当成「历史记录功能好像没生效」而忽略过去。

## 四、调试方法：先取证，再改代码

这个 bug 的定位过程值得单独记下来，因为它示范了一套通用方法。

遇到 `AssertionError` 时**没有**立刻去改 `load_history()`，而是先补充打印，缩小范围：

```python
save_history([10, 20, 30], str(filename))

print("文件路径：", filename)
print("文件是否存在：", filename.exists())
print("文件内容：", filename.read_text(encoding="utf-8"))

result = load_history(str(filename))
print("实际返回：", repr(result))
```

然后按输出分情况判断：

| 现象 | 指向的原因 |
|---|---|
| 返回 `[]` | `load_history()` 误判了数据 |
| 返回 `None` | 漏写了 `return ls` |
| 文件内容不对 | 问题在 `save_history()` |
| 文件内容对、返回 `[]` | 问题在校验逻辑 |

还有一招排查「改了代码却没生效」：

```python
import history
print("实际导入的模块：", history.__file__)
```

同名模块、`__pycache__` 缓存、改了 A 文件却在跑 B 文件，都能靠这一行排除。

> 两条原则：
> - **用 `repr()` 而不是 `str()` 打印可疑值。** `print([])` 和 `print("")` 看起来都是空白，`print(repr([]))` 和 `print(repr(""))` 一眼能分清。
> - **先缩小范围，再动手改。** 没有证据就改代码，改对了也不知道为什么对。

## 五、测试里的三个问题

第一版测试：

```python
def test_history():
    save_history([10, 20, 30], filename="history.json")
    assert load_history("history.json") == [10, 20, 30]
```

**问题一：直接操作真实的 `history.json`，可能覆盖真实数据。** 测试必须和真实数据隔离。

正确做法是用 `tempfile.TemporaryDirectory()`：

```python
with tempfile.TemporaryDirectory() as temp_dir:
    filename = Path(temp_dir) / "history.json"
    save_history([10, 20, 30], str(filename))
    assert load_history(str(filename)) == [10, 20, 30]
```

它在系统临时区建一个独立目录，离开 `with` 块自动整个删掉。好处是：测试之间互不干扰、不留垃圾、能并行跑。

**问题二：「文件不存在」的测试写成了捕获异常。**

```python
try:
    load_history(str(Path(temp_dir) / "not_exist.json"))
except FileNotFoundError:
    pass                       # ← 永远不会进这里
```

`load_history()` 内部已经捕获了 `FileNotFoundError` 并返回 `[]`，所以这个 `except` 永远不会触发。而没有 `else` 分支，所以**无论函数返回什么，这段测试都「通过」**——又是一个假测试（Day 07、Day 10 各遇到过一次）。

应该直接断言返回值：

```python
assert load_history(str(filename)) == []
```

**测试要断言「需求是什么」，而不是「实现碰巧怎么做」。** 需求是「文件不存在时返回空列表」，那就断言返回值。

**问题三：在 `with` 块外面用 `temp_dir`。**

```python
with tempfile.TemporaryDirectory() as temp_dir:
    ...
# 出了 with，目录已经被删除
assert load_history(str(Path(temp_dir) / "not_exist.json")) == []
```

变量 `temp_dir` 还在（它只是个字符串），但它指向的目录已经没了。这里结果恰好正确——因为测的就是「文件不存在」——但属于歪打正着，语义是错的。

> `Day11/` 目录里还留着一个 `error.json`，内容是 `[1,2,]` 加一行 `234`（故意写坏的 JSON）。那是早期版本用真实文件测损坏数据时留下的，后来改用 `tempfile` + `write_text("hello")` 之后它就成了残留文件。

## 六、最终代码

`history.py`：

```python
import json


def save_history(history: list[int], filename: str) -> None:
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


def load_history(filename: str) -> list[int]:
    try:
        with open(filename, "r", encoding="utf-8") as f:
            try:
                ls = json.load(f)
                if type(ls) != list:
                    return []
                for i in ls:
                    if type(i) != int:
                        return []
                    if not 1 <= i <= 100:
                        return []
            except json.decoder.JSONDecodeError:
                return []
        return ls
    except FileNotFoundError:
        return []
```

`test_history.py` 覆盖了四种情况：正常读写、文件不存在、内容是 `hello`、列表含 `"abc"`。

### 回头看还能改的地方

- **`type(ls) != list` 建议写成 `type(ls) is not list`。** 对类型对象的比较，`is` 比 `==` 更准确（`==` 可能被类的 `__eq__` 干扰），而且语义更清楚。元素检查同理。
- **缺两个测试场景**：顶层是字典 `{"guess": 10}`、数字越界 `[1, 101]`。这两条当时被指出来了，最终代码里仍然没补。
- **`load_history` 返回 `[]` 表达了两种完全不同的情况**：「还没有历史」和「数据坏了」。调用方分不清。Day 13 加日志、Day 14 分层校验就是在解决这件事。
- **测试函数里有 `print()`。** 调试时有用，留在最终版本里会干扰测试输出。

## 七、复习自测

1. `json.dump` 和 `json.dumps` 的区别是什么？
2. `ensure_ascii=False` 不加会怎样？数据会出错吗？
3. `open(filename, "w")` 对一个已存在的文件做了什么？想追加内容该用什么模式？
4. 为什么 Windows 上 `open()` 一定要写 `encoding="utf-8"`？
5. `isinstance(True, int)` 是什么结果？校验「必须是整数」该怎么写？
6. 文件内容是 `{"guess": 10}` 时，`for i in ls:` 会发生什么？
7. `if not type(i) != int:` 对于 `i = 10` 的结果是什么？
8. 用 `try/except FileNotFoundError` 测试「文件不存在」为什么是个假测试？
9. `tempfile.TemporaryDirectory()` 解决了什么问题？

<details>
<summary>参考答案</summary>

1. `dump` 把数据写进**文件对象**，`dumps` 返回 **JSON 字符串**。带 `s` 的操作字符串，不带的操作文件。`load` / `loads` 同理。
2. 中文会被转成 `\u5f20\u4e09` 这样的 Unicode 转义序列。数据不会错，读回来还是中文，只是文件内容人看不懂。
3. 清空原文件的全部内容（截断为 0 字节）再写入。想追加要用 `"a"` 模式。
4. 因为 Python 在 Windows 上默认使用系统编码（通常是 GBK），读写中文会乱码或抛 `UnicodeDecodeError`。
5. 结果是 `True`——`bool` 是 `int` 的子类。要排除布尔值必须用 `type(i) is int`。
6. 遍历字典得到的是**键**（字符串 `"guess"`），类型检查会失败。第一版里这会抛出未被捕获的 `TypeError` 导致程序崩溃。
7. `type(10) != int` 是 `False`，`not False` 是 `True`——条件成立，于是合法整数被判为非法，函数返回 `[]`。
8. 因为 `load_history()` 内部已经捕获了 `FileNotFoundError` 并返回 `[]`，`except` 分支永远不会执行；又没有 `else` 分支，所以函数返回任何值这个测试都会通过。
9. 测试文件和真实数据隔离。它创建独立的临时目录，离开 `with` 块后自动删除整个目录，测试之间不互相干扰、不留垃圾文件。

</details>
