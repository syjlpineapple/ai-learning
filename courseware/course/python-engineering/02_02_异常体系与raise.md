# 2.2 异常体系与 `raise`

> **前置** 2.1 `assert` 与自动化测试
> **时长** 约 90 分钟（讲解 40 + 练习 50）
> **配套代码** [`code/m02_testing/ch02_02_*.py`](code/m02_testing/)

## 学习目标

学完这一章，你应该能够：

1. 用 `raise` 主动抛出异常，说清 `raise X("消息")`、`raise`、`raise X` 三种写法的区别
2. 用 `__mro__` 查出任意一个异常类的继承链
3. **排出正确的 `except` 顺序，并解释顺序错了为什么不报错**
4. **认出「自己 `raise` 的异常被自己的 `except` 接住」这个错误**
5. 说清 `raise ... from e` 和 `raise ... from None` 对 traceback 的影响
6. 定义自己的异常类，让调用方按**类型**而不是按**消息文本**区分错误
7. 不用 `pytest`，手写一个「测试某段代码应该抛异常」的检查，并说明为什么 `else` 那一段不能省

## 为什么需要这一章

第 1.5 章的 `parse_int` 失败时返回 `None`：

```python
guess = parse_int(raw)
if guess is None:
    print("不是整数")
```

这够用，直到你想区分**两种**错误：

| 输入 | 想显示 |
|---|---|
| `abc` | 「'abc' 不是整数」 |
| `101` | 「101 不在 1-100 之间」 |

`None` 只能表示「失败了」，说不清**为什么**失败。而且校验函数不该自己 `print`——第 1.6 章说过，它应该把问题交给调用方，由调用方决定怎么显示。

**能同时携带「失败了」和「为什么失败」两样信息、并且强迫调用方处理的东西，就是异常。** 第 1.5 章学的是接住别人抛的异常，这一章学自己抛。

还有一个更重要的理由：**`except` 的顺序**。学习记录里这个问题连续出了三天错，而 Python 从头到尾没有报过一次错。

---

# 一、概念与原理

## 1. `raise`：主动抛出异常

```python
def parse_guess(raw: str) -> int:
    n = int(raw)
    if not 1 <= n <= 100:
        raise ValueError(f"{n} 不在 1-100 之间")     # 校验失败，交给调用方
    return n
```

**什么时候该抛**：当前函数发现了问题，但**它不知道该怎么处理**。`parse_guess` 的职责只是「解析并校验」。校验失败之后要提示用户、要重试、还是要退出——只有调用方知道。

### 三种写法

| 写法 | 含义 | 什么时候用 |
|---|---|---|
| `raise ValueError("消息")` | 抛一个新的异常**实例** | 主动报错 |
| `raise` | 原样重抛**当前正在处理**的异常 | 只能在 `except` 块里用 |
| `raise ValueError` | 抛异常**类**，Python 替你构造一个无参实例 | **不推荐** |

第三种的问题：

```text
2. raise 一个类而不是实例
   TypeError: JSONDecodeError.__init__() missing 3 required positional arguments: 'msg', 'doc', and 'pos'
```

`json.JSONDecodeError` 的构造函数需要三个参数，Python 构造它时失败了，**抛出来的变成了 `TypeError`**。你想报的那个错误丢了。

**养成习惯：`raise` 后面永远跟一个带括号的实例。**

## 2. 内置异常的层次结构

异常是**类**，类之间有继承关系：

```text
BaseException
├── SystemExit                  sys.exit()
├── KeyboardInterrupt           Ctrl+C
└── Exception                   ← 几乎所有「错误」的基类
    ├── ArithmeticError
    │   └── ZeroDivisionError
    ├── LookupError
    │   ├── IndexError
    │   └── KeyError
    ├── OSError
    │   ├── FileNotFoundError
    │   ├── PermissionError
    │   └── TimeoutError
    ├── ValueError
    │   └── UnicodeError
    │       └── UnicodeDecodeError
    ├── TypeError
    └── ImportError
        └── ModuleNotFoundError
```

**捕获父类会连带捕获所有子类：**

```python
except OSError:         # FileNotFoundError、PermissionError、TimeoutError 都会被接住
except LookupError:     # IndexError、KeyError 都会被接住
```

### 用 `__mro__` 查继承链

不确定一个异常的父类是谁时，不要猜：

```text
1. 继承链（__mro__）
   builtins.FileNotFoundError
      FileNotFoundError → OSError → Exception → BaseException → object
   builtins.KeyError
      KeyError → LookupError → Exception → BaseException → object
   builtins.UnicodeDecodeError
      UnicodeDecodeError → UnicodeError → ValueError → Exception → BaseException → object
   json.decoder.JSONDecodeError
      JSONDecodeError → ValueError → Exception → BaseException → object
   requests.exceptions.JSONDecodeError
      JSONDecodeError → InvalidJSONError → RequestException → OSError → JSONDecodeError → ValueError → Exception → BaseException → object
```

`__mro__` 是 Method Resolution Order（方法解析顺序），列出了这个类和它所有的祖先。

**看最后一行**：`requests` 库的 `JSONDecodeError` **同时**是 `RequestException`（网络请求的错误）和 `ValueError`（值的错误）。它有两条继承路线。这一行是下一节那个真实 bug 的根源。

## 3. ⚠️ `except` 的顺序：子类必须在父类前面

**`except` 子句按书写顺序逐个匹配，第一个匹配上的执行，后面的全部跳过。**

```python
try:
    ...
except FileNotFoundError:     # ✓ 具体的在前
    ...
except OSError:               # ✓ 宽泛的在后
    ...
```

顺序反过来：

```python
try:
    ...
except OSError:               # 父类在前，FileNotFoundError 也会先被它接住
    ...
except FileNotFoundError:     # ← 永远不会执行
    ...
```

**第二个分支变成了死代码。** 第 1.2 章讲过 `elif` 从宽到窄排会产生死代码，这里是同一回事。

### 一个真实的 bug

学习记录第 15、16 天调用 HTTP 接口时，代码的结构是这样的（简化后）：

```python
try:
    response = requests.get(url, timeout=5)
    data = response.json()
except requests.exceptions.RequestException:
    return "请求失败"
except ValueError:
    return "响应格式不对"
```

想法很合理：网络出问题报「请求失败」，返回的不是 JSON 报「响应格式不对」。

配套示例复现了服务器返回一个 HTML 页面（不是 JSON）的情况：

```text
3. except 顺序写反，后面的分支永远进不去
   顺序写反 → '请求失败'   ← 明明是响应格式不对
   顺序改对 → '响应格式不对'
```

**`response.json()` 解析失败时抛的是 `requests.exceptions.JSONDecodeError`，它同时是 `RequestException` 和 `ValueError`**（上一节的继承链）。写在前面的 `except RequestException` 先匹配上了，`except ValueError` 永远进不去。

后果：**服务器返回的格式不对，日志却记成了「请求失败」**。排查的人会去查网络、查超时、查 DNS——全是错误的方向。这个 bug 在学习记录里从第 14 天延续到第 16 天，第 17 天才被发现并修正。

### 为什么这么难发现

**Python 不报错，也不警告。** 我还专门试了课程用的工具：

| 工具 | 能发现吗 |
|---|---|
| Python 解释器 | ✗ |
| `ruff check`（课程配置的规则集） | ✗ |
| `mypy`（即使开了 `--warn-unreachable`） | ✗ |

配套测试 `test_ch02_02_except_order_not_flagged_by_tools` 每次都会重新验证这一点。

> `pylint` 有一条专门的规则 `bad-except-order`，可以检查内置异常之间的顺序。
> 本课程没有安装 pylint，这一条我没有实测。而且即使有它，像 `requests` 这种「第三方库的异常同时继承两个类」的情况，静态工具很难全部覆盖。

### 能做的只有两件事

**一、写 `except` 时画一下继承关系。** 遇到不熟悉的异常，查 `__mro__`。

**二、给每个 `except` 分支写一条测试。** 让测试真的触发那个异常，断言走进了正确的分支。死代码分支的测试一定会失败——这是唯一可靠的检查方法。练习 3 就是这样做的。

## 4. ⚠️ 不要捕获自己准备抛出的异常

学习记录第 9 天的第一版：

```python
def parse_guess(user_input: str) -> int:
    try:
        n = int(user_input)
        if not 1 <= n <= 100:
            raise ValueError("数字必须在 1～100")     # ← 自己抛的
        return n
    except ValueError:                                # ← 又被自己接住了
        raise ValueError("输入格式错误") from None
```

```text
6. 捕获了自己准备抛出的异常
   parse_wrong('abc') → 输入格式错误
   parse_wrong('101') → 输入格式错误
   ↑ 101 的格式完全正确，提示却说「格式错误」
```

**`raise` 写在了 `try` 块的里面**，所以它抛出的 `ValueError` 被同一个 `try` 的 `except ValueError` 接住，改写成了「格式错误」。

修法不是「不捕获 `ValueError`」，而是**把自己 `raise` 的那一行移到 `try` 外面**：

```python
def parse_guess(user_input: str) -> int:
    try:
        n = int(user_input)                 # try 只包这一行
    except ValueError:
        raise ValueError("输入格式错误") from None

    if not 1 <= n <= 100:                   # 范围检查在 try 外面
        raise ValueError("数字必须在 1～100")
    return n
```

这就是第 1.5 章「`try` 只包住你准备处理的那种失败」的又一个实例。

## 5. 异常链：`from` 的三种形态

在 `except` 块里抛一个新异常时，Python 会记录两个异常之间的关系：

```text
4. 三种异常链
   不写 from    显示原始 ValueError: True   连接句: During handling of the above exception, another exception occurred:
   from e     显示原始 ValueError: True   连接句: The above exception was the direct cause of the following exception:
   from None  显示原始 ValueError: False  连接句: （无）
```

| 写法 | traceback 里的连接句 | 含义 |
|---|---|---|
| `raise X` | **During handling of the above exception, another exception occurred** | 「处理 A 的时候**碰巧**又出了 B」 |
| `raise X from e` | **The above exception was the direct cause of the following exception** | 「B **就是由** A 引起的」 |
| `raise X from None` | 不显示原始异常 | 「A 对读者没有意义，别显示了」 |

### 什么时候用哪个

**`from e`**：你在把一个底层异常翻译成更高层的含义，而且底层信息对排查有用。

```python
except ValueError as e:
    raise ConfigError(f"配置项 TIMEOUT 不是数字") from e
```

traceback 会同时显示「`int()` 解析失败」和「配置项错误」，并明确说前者是后者的原因。

**`from None`**：底层的消息对读者是噪音。

```python
except ValueError:
    raise GuessFormatError(f"{raw!r} 不是整数") from None
```

用户不需要看到 `invalid literal for int() with base 10`。

**不写**：大多数时候应该避免。「碰巧又出了一个错」的语义通常不是你想表达的——它暗示 `except` 块本身有 bug。

### 这三种写法在异常对象上的区别

```python
try:
    int('abc')
except ValueError as e:
    raise RuntimeError('x')  # 换成 from e / from None 对比
```

| 写法 | `__cause__` | `__context__` | `__suppress_context__` |
|---|---|---|---|
| `raise X` | `None` | `ValueError` | `False` |
| `raise X from e` | `ValueError` | `ValueError` | `True` |
| `raise X from None` | `None` | `ValueError` | `True` |

注意最后一行：**`from None` 并没有删掉原始异常**，`__context__` 里还记着它，只是 `__suppress_context__ = True` 让 traceback 不显示它。

### 两个常见误解

| 误解 | 事实 |
|---|---|
| `from None` 会让程序不报错 | **不会**，它只改变 traceback 的显示，异常照样抛 |
| `from None` 能隐藏敏感信息 | **不能**当安全机制用，原始异常还在 `__context__` 里 |

## 6. 重抛：裸 `raise` 和 `raise e`

```python
except ValueError:
    logger.error("解析失败")
    raise                    # 记录之后原样抛出
```

学习记录里说「`raise e` 会让原始出错位置的信息变得不完整」。**我实测了一下，在 Python 3 里这个说法不准确：**

```text
5. 裸 raise 和 raise e 的 traceback
   裸 raise  的 traceback 有 3 层，包含原始出错行: True
   raise e   的 traceback 有 4 层，包含原始出错行: True
   ↑ raise e 多了一层「raise e 这一行」，原始信息并没有丢
```

两种写法都保留了原始的出错位置。`raise e` 只是**多了一层**——把 `raise e` 这一行也记进了 traceback。

> 在 Python 2 里 `raise e` 确实会丢掉原始 traceback，这个说法可能是从那时候流传下来的。

**仍然推荐裸 `raise`**，理由变成了：

- 意图更清楚：「我不处理，原样交出去」
- traceback 少一层噪音
- 不需要 `as e`，少一个变量

## 7. 自定义异常类

```python
class GuessError(ValueError):
    """猜测输入不合法。"""

class GuessFormatError(GuessError):
    """输入不是整数。"""

class GuessRangeError(GuessError):
    """数字超出范围。"""
```

**定义一个异常类只需要继承，连函数体都不用写**——文档字符串就够了。

### 为什么要自定义：按类型区分，不按消息区分

```python
# ✗ 用消息文本区分 —— 改一个字就失效
except ValueError as e:
    if "格式" in str(e):
        ...

# ✓ 用类型区分 —— 稳定
except GuessFormatError:
    print("请输入整数")
except GuessRangeError:
    print("请输入 1-100 之间的数")
```

**异常的类型是给程序看的契约，消息是给人看的文案。** 文案随时可能改（翻译、措辞调整），类型不会。第 1.9 章还看到过：连 Python 自己的 `max([])` 都在 3.13 改了措辞。

### 为什么继承 `ValueError`

**向后兼容。** 原来写 `except ValueError` 的调用方，不改一行代码就能接住新的 `GuessFormatError`。

层次也要设计：

```python
except GuessError as e:         # 两种都接住，统一处理
    say(f"{e}，这次不算")
```

调用方可以选择细分处理（接子类），也可以统一处理（接基类）。

### 给异常加上数据

```python
class GuessRangeError(GuessError):
    def __init__(self, value: int, low: int, high: int) -> None:
        super().__init__(f"{value} 不在 {low}-{high} 之间")
        self.value = value
        self.low = low
        self.high = high
```

调用方拿到异常后，可以用 `e.value`、`e.low` 取出具体的数据，不需要从消息里解析。`super().__init__(...)` 是在调用父类的构造方法设置消息——类和继承在第 3.2 章细讲，现在照着写就行。

## 8. 什么时候抛、什么时候处理

判断标准只有一句：**这个函数知道该怎么办吗？**

| 情况 | 做法 | 例子 |
|---|---|---|
| 知道怎么处理 | 捕获并处理 | 文件不存在 → 首次运行，返回空记录 |
| 不知道怎么处理 | **抛出去** | 校验失败 → 交给调用方决定 |
| 预料之外的异常 | **不要捕获** | 让它暴露出来 |

**不要为了「让程序不报错」而捕获异常。** 静默吞掉的异常会把 bug 变成「行为莫名不对」，比直接崩溃难查得多。

异常抛出后会**沿着调用链逐层向上**，直到被某一层的 `except` 接住，或者到最外层都没人接、程序终止并打印 traceback。这正是「抛出去」的意思：不处理，交给上一层。

## 9. 不用框架，测试「应该抛异常」

第 2.1 章的 `assert` 只能测返回值。但 `parse_guess("abc")` 不返回值，它抛异常。这种怎么测？

```python
try:
    parse_guess("abc")
except GuessFormatError:
    pass                                              # 抛了，符合预期
else:
    raise AssertionError("预期 GuessFormatError")      # 没抛，测试失败
```

逻辑是反过来的：抛了 → 通过；没抛 → 失败。

### ⚠️ `else` 那一段不能省

```text
7. 手写「测异常」时漏了 else
   没写 else：上面这段静默结束了 —— 测试「通过」，但被测函数根本没抛异常
   写了 else：AssertionError: 预期出现 ValueError
```

示例里的 `never_raises` 根本不抛异常。没有 `else` 的版本**一声不响地「通过」了**——这是第 2.1 章说的假测试的又一种形态。

> 练习 4 要你把这个结构封装成一个函数 `expect_raises`。下一章的 `pytest.raises` 做的就是同一件事，
> 手写一遍之后，它就不是咒语了。

## 10. 第十版猜数字

```python
def parse_guess(raw: str, low: int = 1, high: int = 100) -> int:
    try:
        n = int(raw)
    except ValueError:
        raise GuessFormatError(f"{raw!r} 不是整数") from None
    if not low <= n <= high:
        raise GuessRangeError(n, low, high)
    return n
```

```python
try:
    guess = parse_guess(raw)
except GuessError as e:
    say(f"   {e}，这次不算")
    continue
```

```powershell
python -m m02_testing.ch02_02_example play
```

和第 1.5 章的 `parse_int` 比：

| | `parse_int`（1.5） | `parse_guess`（2.2） |
|---|---|---|
| 失败时 | 返回 `None` | 抛异常 |
| 能说清为什么失败吗 | ✗ | ✓，两种类型 + 消息 |
| 调用方忘了处理会怎样 | `None` 混进后续计算 | 程序报错，立刻发现 |
| 范围检查 | 在调用方 | 在函数里 |

**两种设计都有道理**，第 4.5 章「错误语义设计」会专门讨论什么时候该返回 `None`、什么时候该抛异常。

---

# 二、动手练习

打开 `ch02_02_exercise.py`。

## 练习 1（基础）· 先猜继承关系

```python
PREDICTIONS = {
    "issubclass(FileNotFoundError, OSError)": None,
    "issubclass(KeyError, LookupError)": None,
    "issubclass(IndexError, KeyError)": None,
    "issubclass(KeyboardInterrupt, Exception)": None,
    "issubclass(SystemExit, BaseException)": None,
    "issubclass(UnicodeDecodeError, ValueError)": None,
    "issubclass(ZeroDivisionError, ArithmeticError)": None,
    "issubclass(TimeoutError, OSError)": None,
    "issubclass(ModuleNotFoundError, ImportError)": None,
    "issubclass(bool, int)": None,
    "issubclass(ValueError, TypeError)": None,
}
```

## 练习 2（基础）· 自定义异常

1. 把三个占位类改成正确的继承关系
2. 写 `parse_guess(raw, low, high)`：格式错误抛 `GuessFormatError`（用 `from None`），范围错误抛 `GuessRangeError`

**`try` 只包住 `int(raw)`。** 测试会检查 `parse_guess("101")` 抛的是 `GuessRangeError` 而不是 `GuessFormatError`——如果你犯了第 4 节的错误，测试会直接告诉你。

## 练习 3（基础）· 修好 `except` 的顺序

```python
describe_failure_buggy(open_missing_file)    # → "其他 IO 错误"   ✗ 应该是「文件不存在」
```

先说出哪个分支是死代码，再写 `describe_failure`。测试会分别触发 `FileNotFoundError`、`PermissionError`、`ValueError` 和「没有异常」四种情况，**每个分支都要被走到**——这就是第 3 节说的「给每个 `except` 分支写一条测试」。

## 练习 4（进阶）· 手写一个 `pytest.raises`

```python
err = expect_raises(GuessRangeError, parse_guess, "101")    # 返回异常对象
expect_raises(ValueError, parse_guess, "42")               # → AssertionError
expect_raises(ValueError, raise_key_error)                 # → KeyError 原样抛出
```

三种情况，对应 `try / except / else` 的三段。

## 怎么验证

```powershell
pytest tests/test_m02.py -k ch02_02 -v
```

---

# 三、常见错误

| # | 错误 | 表现 | 怎么避免 |
|---|---|---|---|
| **1** | **`except` 父类写在子类前面** | 子类分支是死代码；**Python、ruff、mypy 都不提示** | 子类在前；每个分支写一条测试 |
| **2** | **自己 `raise` 的那一行在 `try` 里面** | 被自己的 `except` 接住、改写成错误的消息 | 把 `raise` 移到 `try` 外面 |
| **3** | **`raise` 一个需要参数的异常类** | 变成 `TypeError`，原始意图丢失 | `raise` 后面永远跟实例 |
| **4** | **按消息文本区分错误** | 改一个字就失效 | 自定义异常，按类型区分 |
| **5** | **以为 `from None` 会吞掉异常** | 以为不用处理了 | 它只改变显示 |
| **6** | **手写异常测试漏了 `else`** | 被测函数不抛异常，测试照样「通过」 | `else: raise AssertionError(...)` |
| **7** | **为了不报错而捕获异常** | bug 变成「行为莫名不对」 | 不知道怎么处理就别接 |

**第 1 条是整门课最该记住的一条。** 它在学习记录里造成了连续三天的真实 bug，后果是日志把错误原因记错了，排查方向完全跑偏。附录 A 有完整的复现过程。

---

# 四、本章小结

```text
raise X("消息")：主动抛出；不知道怎么处理时交给调用方
   └─ 永远抛实例，不抛类
        ↓
异常是类，有继承关系；用 __mro__ 查
   └─ requests 的 JSONDecodeError 同时是 RequestException 和 ValueError
        ↓
⚠️ except 按顺序匹配：子类必须在前
   └─ 顺序错了 → 死代码 → Python / ruff / mypy 都不提示 → 只有测试能发现
        ↓
⚠️ 自己 raise 的那行放在 try 外面
        ↓
异常链：不写（碰巧）/ from e（因果）/ from None（隐藏）
        ↓
裸 raise 重抛；raise e 在 Python 3 里不丢信息，只是多一层
        ↓
自定义异常：按类型区分，不按消息；继承 ValueError 保持兼容
        ↓
手写异常测试：try / except / else，else 不能省
```

一句话总结：**异常的类型是契约，顺序是逻辑，消息只是文案。** 前两者错了，程序照样运行，只是走错了路。

## 下一章

[2.3 从 `assert` 到 `pytest`](02_03_从assert到pytest.md) —— 到现在为止，测试都是手写的：自己调用测试函数、自己写 `try / except / else`。下一章换成 `pytest`。它会解决手写测试的几个根本问题，也会带来几个新坑——其中一个是学习记录里真实发生过的：**测试文件存在，pytest 却输出 `collected 0 items`**。

---

# 五、自测

1. 什么时候该主动 `raise`？
2. `raise ValueError("x")`、`raise`、`raise ValueError` 三种写法有什么区别？为什么不推荐第三种？
3. `except LookupError` 能接住 `KeyError` 吗？`except KeyError` 能接住 `IndexError` 吗？
4. 怎么查一个异常类的所有父类？
5. `except` 子句按什么规则匹配？父类写在子类前面会怎样？
6. 学习记录里的 `except RequestException` / `except ValueError` 为什么让 `ValueError` 分支成了死代码？后果是什么？
7. 有哪些工具能发现 `except` 顺序问题？可靠的检查方法是什么？
8. 第 9 天的第一版 `parse_guess` 为什么把 `101` 报成「输入格式错误」？怎么改？
9. 不写 `from`、`from e`、`from None` 三种写法的 traceback 有什么区别？
10. `from None` 之后，原始异常还在吗？在哪里？
11. 裸 `raise` 和 `raise e` 在 Python 3 里有什么区别？为什么仍然推荐裸 `raise`？
12. 为什么要自定义异常类？为什么让它继承 `ValueError`？
13. 怎么让异常携带「哪个数超出了范围」这样的数据？
14. 判断「抛还是处理」的标准是什么？
15. 手写「测试应该抛异常」时，`else` 那一段的作用是什么？少了会怎样？

<details>
<summary>参考答案</summary>

1. 当前函数**发现了问题，但不知道该怎么处理**的时候。比如校验函数发现输入不合法，至于要提示、重试还是退出，只有调用方知道。
2. `raise ValueError("x")` 抛一个新实例；`raise` 在 `except` 块里原样重抛当前异常；`raise ValueError` 抛异常类、让 Python 替你构造一个无参实例。不推荐第三种是因为**构造函数需要参数时会失败**，抛出来的变成了 `TypeError`（比如 `json.JSONDecodeError` 需要三个参数），原来想报的错误丢了。
3. `except LookupError` **能**接住 `KeyError`（父类接住子类）；`except KeyError` **不能**接住 `IndexError`（两者是兄弟，都是 `LookupError` 的子类）。
4. 看它的 **`__mro__`** 属性，比如 `FileNotFoundError.__mro__`。
5. **按书写顺序逐个匹配，第一个匹配上的执行，后面的全部跳过。** 父类写在前面，子类的分支永远轮不到，成了死代码。
6. 因为 `requests.exceptions.JSONDecodeError` **同时继承了 `RequestException` 和 `ValueError`**，写在前面的 `except RequestException` 先匹配上了。后果是：服务器返回的格式不对，**日志却记成了「请求失败」**，排查方向被引到网络问题上。
7. Python 解释器、课程配置的 `ruff`、`mypy`（包括 `--warn-unreachable`）**都不会提示**（实测）。`pylint` 有 `bad-except-order` 规则但本课程未实测。**可靠的检查方法是给每个 `except` 分支写一条测试**，让测试真的触发对应的异常——死代码分支的测试一定会失败。
8. 因为范围检查的 `raise ValueError(...)` **写在了 `try` 块里面**，被同一个 `try` 的 `except ValueError` 接住，改写成了「输入格式错误」。修法是把范围检查移到 `try` 外面，`try` 只包 `int()` 那一行。
9. 不写 `from`：显示原始异常，连接句是「During handling of the above exception, another exception occurred」（碰巧又出错）；`from e`：显示原始异常，连接句是「The above exception was the direct cause...」（因果关系）；`from None`：**不显示**原始异常。
10. **还在**，记在新异常的 `__context__` 属性里。`from None` 只是把 `__suppress_context__` 设成 `True`，让 traceback 不显示它。所以它不能当安全机制用。
11. 实测两者**都保留了原始出错位置**，`raise e` 只是在 traceback 里**多了一层**（`raise e` 这一行）。仍然推荐裸 `raise`：意图更清楚（原样交出去）、traceback 少一层噪音、不需要 `as e`。
12. 为了让调用方**按类型区分错误**，而不是比较消息文本——类型是稳定的契约，消息是随时可能改的文案。继承 `ValueError` 是为了**向后兼容**：原来写 `except ValueError` 的代码不用改就能接住。
13. 在异常类里写 `__init__`，调用 `super().__init__(消息)` 设置消息，再把数据存成属性：`self.value = value`。调用方用 `e.value` 取，不需要解析消息。
14. **这个函数知道该怎么办吗？** 知道就处理，不知道就抛出去，预料之外的就不要捕获。
15. `else` 在**被测代码没有抛异常时**执行，主动抛 `AssertionError` 让测试失败。少了它，被测函数即使根本不抛异常，测试也会静默「通过」——是一个永远不会失败的假测试。

</details>
