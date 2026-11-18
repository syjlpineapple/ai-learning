# Day 09 · 异常分类、异常链与测试异常

> **学习日** 2026-10-21（10:02 - 10:36，5 轮迭代）
> **对应代码** [`dailypractice/Day9.py`](../../dailypractice/Day9.py)
> **原始对话** `courseware/_raw/markdown/03_Python每日练习出题.md`（对话里称「第九天」）

> `dailypractice/` 下没有 `Day8.py`，编号本身是断的。对话里的「第八天」就是上一节 Day07。

## 本节掌握

- 区分**格式错误**和**业务规则错误**
- **不要捕获自己准备抛出的异常**（本节最大的坑）
- `try` 的范围要尽量小，只包住真正会出错的那一行
- `raise ... from None` 隐藏异常链
- 用 `try / except / else` 结构测试「应该抛异常」的情况
- 校验函数不负责打印，由调用方决定怎么回应错误

这一节改了五版，是 A 线迭代次数最多的一天。

---

# 第一部分 · 知识讲解

## 1. `raise`：主动抛出异常

Day03 学的是**捕获**别人抛的异常，本节学**自己抛**。

```python
raise ValueError("数字必须在 1~100")
```

什么时候需要主动抛：**当前函数发现输入不合法、但它不知道该怎么处理时。**

```python
def parse_guess(user_input: str) -> int:
    num = int(user_input)
    if not 1 <= num <= 100:
        raise ValueError("数字必须在 1~100")      # 校验失败，交给调用方
    return num
```

这个函数的职责只是「解析并校验」。至于校验失败后要提示用户、要重试、还是要退出，**只有调用方知道**——所以把问题抛给它。

### 三种 `raise` 写法

| 写法 | 含义 | 用在哪 |
|---|---|---|
| `raise ValueError("消息")` | 抛一个新异常实例 | 主动报错 |
| `raise` | 原样重抛**当前正在处理**的异常 | 只能在 `except` 块内 |
| `raise ValueError` | 抛异常类，Python 自动构造无参实例 | **不推荐** |

第三种的问题：如果那个异常类的构造函数需要参数（比如 `json.JSONDecodeError` 要三个），会引发新的 `TypeError`，**把原始错误弄丢了**。

裸 `raise` 很重要：

```python
except ValueError:
    logger.error("解析失败")
    raise                  # 记录后原样抛出，保留完整 traceback
```

它比 `raise e` 好——`raise e` 会把当前这一行作为新的抛出点，原始出错位置的信息可能变得不完整。

> **整理课程时的更正**：在 Python 3 里实测，`raise e` 并不会丢掉原始出错位置，
> traceback 只是多了一层「`raise e` 这一行」。推荐裸 `raise` 的理由是意图更清楚、少一层噪音，
> 而不是「会丢信息」（那是 Python 2 的行为）。详见课程 [2.2 章第 6 节](../course/python-engineering/02_02_异常体系与raise.md)。

## 2. 内置异常的层次结构

Python 的异常是**类**，而且有继承关系。简化的结构：

```text
BaseException
├── SystemExit               sys.exit() 触发
├── KeyboardInterrupt        用户按 Ctrl+C
└── Exception                ← 几乎所有「错误」的基类
    ├── ArithmeticError
    │   └── ZeroDivisionError
    ├── LookupError
    │   ├── IndexError
    │   └── KeyError
    ├── OSError
    │   └── FileNotFoundError
    ├── TypeError
    ├ ── ValueError
    │   └── UnicodeDecodeError
    ├── AttributeError
    └── NameError
```

两个实用结论：

**一、`except Exception` 不会捕获 `KeyboardInterrupt` 和 `SystemExit`。** 这是故意的设计——它们继承自 `BaseException` 而非 `Exception`，所以即使写了 `except Exception` 兜底，用户还能用 Ctrl+C 中断程序。而裸 `except:` 会把它们也抓住，这就是不该用裸 `except` 的原因。

**二、捕获父类会连带捕获所有子类。**

```python
except OSError:          # FileNotFoundError 也会被抓住
except LookupError:      # IndexError、KeyError 都会被抓住
```

## 3. 捕获顺序：子类必须在父类前面

这是本节最需要记住的规则，也是后面几节反复出错的地方。

```python
try:
    ...
except FileNotFoundError:    # 具体的在前
    print("文件不存在")
except OSError:              # 宽泛的在后
    print("其他 IO 错误")
```

**`except` 子句按书写顺序匹配，第一个匹配上的就执行，后面的全部跳过。**

所以顺序颠倒的话：

```python
except OSError:              # 父类在前，会先匹配上
    print("其他 IO 错误")
except FileNotFoundError:    # ← 永远不会执行，是死代码
    print("文件不存在")
```

**Python 对此不报错、不警告。** 这个分支就那么静默地失效了。

> 检查方法：排 `except` 顺序时画一下继承关系。遇到不确定的，用 `Exception.__mro__` 看继承链：
>
> ```python
> FileNotFoundError.__mro__
> # (FileNotFoundError, OSError, Exception, BaseException, object)
> ```
>
> 这个坑在 Day14、Day15、Day16 会连续造成三次真实的 bug，到 Day17 才被改对。现在打好基础。

## 4. 异常链：`from` 的三种形态

在 `except` 块里抛新异常时，Python 会记录两个异常之间的关系：

```python
try:
    int("abc")
except ValueError:
    raise RuntimeError("解析配置失败")
```

traceback 会同时显示两个异常，中间一句：

```text
During handling of the above exception, another exception occurred
（在处理上述异常时，又发生了另一个异常）
```

这个自动记录的关系存在 `__context__` 属性里。

### `raise ... from e`：明确声明因果

```python
except ValueError as e:
    raise RuntimeError("解析配置失败") from e
```

traceback 变成：

```text
The above exception was the direct cause of the following exception
（上述异常是下面异常的直接原因）
```

区别在语义：`__context__` 是「碰巧在处理 A 时发生了 B」，`__cause__`（`from e` 设置的）是「**B 就是由 A 引起的**」。后者表达更准确，排查时信息更有用。

### `raise ... from None`：隐藏上下文

```python
except ValueError:
    raise ValueError("输入格式错误，请输入整数") from None
```

告诉 Python **不要在 traceback 里显示原始异常**。输出只剩自己定义的那条消息。

用途是：底层库的异常消息对用户没有意义（比如 `invalid literal for int() with base 10: 'abc'`），只想展示自己的提示。

三个容易误解的点：

| 误解 | 事实 |
|---|---|
| `from None` 会让程序不报错 | **不会**，它只影响展示方式，异常照样抛 |
| `from None` 能隐藏敏感信息 | **不能**当安全机制用，真要脱敏得靠日志分级 |
| 任何地方都能写 `from None` | 只在 `except` 块内的 `raise` 上有意义——外面没有「当前异常」可隐藏 |

## 5. 自定义异常类

内置异常不够用时，可以自己定义：

```python
class GuessError(ValueError):
    """猜数字相关错误的基类。"""

class GuessFormatError(GuessError):
    """输入不是整数。"""

class GuessRangeError(GuessError):
    """数字超出 1~100。"""
```

**定义一个异常类只需要继承，连函数体都不用写**（文档字符串就够）。

为什么要自定义：

```python
# 用消息文本区分 —— 脆弱
except ValueError as e:
    if "格式" in str(e):       # 改一个字就失效
        ...

# 用类型区分 —— 稳定
except GuessFormatError:
    ...
except GuessRangeError:
    ...
```

**异常的类型是稳定的契约，消息文本是给人看的、随时可能改。** 让调用方依赖类型而不是文案。

继承自 `ValueError` 还有个好处：**向后兼容**。原来写 `except ValueError` 的代码照样能接住新异常。

> 这个问题在 Day14 会实际暴露——那边的测试写了 `assert str(e) == "类型错误"`，把测试和中文文案焊死了，改一个字测试就断。

## 6. 异常的传播机制

异常抛出后，Python 会**沿调用栈逐层向上**寻找能处理它的 `except`：

```python
def a():
    raise ValueError("出错")

def b():
    a()              # 不处理，继续上抛

def main():
    try:
        b()
    except ValueError:
        print("在 main 里处理了")       # ← 在这里被接住
```

一路到最外层都没人接，程序终止并打印 traceback。

**traceback 要从下往上读**：最下面是异常本身和最直接的出错位置，往上是调用它的各层。

```text
Traceback (most recent call last):
  File "main.py", line 10, in <module>     ← 最外层
    main()
  File "main.py", line 7, in main          ← 中间层
    b()
  File "main.py", line 2, in a             ← 实际出错的地方
    raise ValueError("出错")
ValueError: 出错                            ← 异常类型和消息
```

## 7. 什么时候抛、什么时候处理

判断标准只有一句：**这个函数知道该怎么办吗？**

| 情况 | 做法 |
|---|---|
| 知道怎么处理（有明确对策） | 捕获并处理掉 |
| 不知道怎么处理 | 往上抛，交给调用方 |
| 预料之外的异常 | 不要捕获，让它暴露 |

```python
# 知道怎么办：文件不存在就用空记录（首次运行很正常）
except FileNotFoundError:
    return []

# 不知道怎么办：校验失败，交给调用方决定
if not 1 <= num <= 100:
    raise ValueError("数字必须在 1~100")
```

**不要为了「让程序不报错」而捕获异常。** 静默吞掉异常会让 bug 变成「行为莫名不对」，比直接崩溃难排查得多。

## 8. 测试「应该抛异常」的情况

Day07 的 `assert` 只能测返回值。但 `parse_guess("abc")` 根本不返回值，它抛异常——这种怎么测？

```python
try:
    parse_guess("abc")
except ValueError:
    pass                                      # 抛了，符合预期
else:
    raise AssertionError("预期出现 ValueError")   # 没抛，测试失败
```

逻辑是反过来的：

- 抛了异常 → 进 `except` → `pass` → 测试通过
- 没抛异常 → 进 `else` → 主动抛 `AssertionError` → 测试失败

这里的 `else` 是 `try` 语句的 `else` 分支（Day03 讲过），含义是「`try` 块没有发生异常时执行」。

**`else` 这一支绝不能省。** 少了它，被测函数即使一声不响地返回了值，测试也会「通过」——又是一个假测试（Day07 讲的）。

> Day21 学了 pytest 之后，这六行可以压缩成两行：
>
> ```python
> with pytest.raises(ValueError):
>     parse_guess("abc")
> ```
>
> 但先用原生写法理解一遍逻辑是值得的，否则 `pytest.raises` 只是个记不住的咒语。

---

# 第二部分 · 当天的练习

## 一、题目

把输入校验独立成函数：

```python
def parse_guess(user_input: str) -> int:
    ...
```

| 输入 | 预期 |
|---|---|
| `"42"` `"1"` `"100"` | 返回对应整数 |
| `"abc"` | 抛 `ValueError` |
| `"0"` `"101"` | 抛 `ValueError` |

要求：函数内不用 `input()` 和 `print()`；`q` 要在调用 `parse_guess()` **之前**处理，因为它是退出指令，不是数字。

## 二、第一版：异常被自己吃掉了

```python
def parse_guess(user_input: str) -> int:
    try:
        int_num = int(user_input)
        if not 1 <= int_num <= 100:
            raise ValueError("数字必须在 1～100")     # ← 自己抛的
        return int_num
    except ValueError:                                # ← 又被自己抓住
        raise ValueError("输入格式错误")               # ← 包装成了错误的消息
```

### 坑 1：捕获了自己准备向上传递的异常

两种错误都是 `ValueError`：

- `int("abc")` 失败，Python 抛 `ValueError`
- 范围不合法，代码自己 `raise ValueError`

而 `except ValueError` 不分青红皂白全抓住，统一改写成「输入格式错误」。

**结果是输入 `"101"` 会提示「输入格式错误」**——但 101 的格式完全正确，它是范围不对。错误信息把人引向错误的方向，这比不给提示更糟。

根本原因是 `raise` 写在了 `try` 块**内部**，所以它抛出的异常会被同一个 `try` 的 `except` 接住。

### 坑 2：调用了函数但没接收返回值

```python
parse_guess(input_num)        # 校验通过了，但转换后的整数丢了
```

应该是：

```python
guess = parse_guess(input_num)    # guess 是整数，可以交给 check_num()
```

函数的返回值不接就等于白算一遍。

## 三、第二版：去掉多余的 try

```python
def parse_guess(user_input: str) -> int:
    int_num = int(user_input)

    if not 1 <= int_num <= 100:
        raise ValueError("数字必须在 1～100")

    return int_num
```

把 `try/except` 整个删掉，两类错误各自向上传播：

- `"abc"` → `int()` 自己抛 `ValueError`
- `"101"` → 代码主动抛 `ValueError("数字必须在 1～100")`
- `"50"` → 正常返回 `50`

调用处统一捕获：

```python
try:
    guess = parse_guess(input_num)
    print("输入有效，数字是：", guess)
except ValueError as e:
    print(e)
```

这一版的设计是对的，但有个体验问题：输入 `"abc"` 时打印出来的是 Python 原生的英文消息（类似 `invalid literal for int() with base 10: 'abc'`），而不是中文提示。

## 四、第三版：只包住真正危险的那一行

```python
def parse_guess(user_input: str) -> int:
    try:
        int_num = int(user_input)              # try 只包这一行
    except ValueError:
        raise ValueError("输入格式错误，请输入整数") from None

    if not 1 <= int_num <= 100:                # 范围检查在 try 外面
        raise ValueError("数字必须在 1～100")

    return int_num
```

两个关键改动：

**一、`try` 只包住 `int()` 转换。** 范围检查移到了 `try` 外面，所以它抛出的异常不会被这个 `except` 接住。这就是坑 1 的正解——**不是不能捕获 `ValueError`，而是不能把自己 `raise` 的那一行放在 `try` 里面。**

**二、异常范围最小化本身就是原则。** `try` 包得越大，越容易误捕获别处的同类异常，把真 bug 伪装成「用户输入错误」。Day 06 那个「`try` 包住整个游戏主体」的问题，在这里得到了正式处理。

现在两种错误信息各就各位：

| 输入 | 提示 |
|---|---|
| `abc` | 输入格式错误，请输入整数 |
| `101` | 数字必须在 1～100 |

## 五、`raise ... from None` 是什么

这是当时专门追问的一个点。

### 不加 `from None`

在 `except` 块里 `raise` 新异常时，Python 认为「新异常是在处理旧异常的过程中产生的」，默认保留两者的关联。traceback 会把原始异常和新异常**一起**打印出来，中间加一句 `During handling of the above exception, another exception occurred`（在处理上述异常时，又发生了另一个异常）。

对用户来说，底层那段 `invalid literal for int()` 是噪音。

### 加了 `from None`

```python
raise ValueError("输入格式错误，请输入整数") from None
```

告诉 Python：**traceback 里不要显示原始异常的上下文。** 输出只剩自己定义的那条消息。

### 三种写法的区别

| 写法 | 含义 |
|---|---|
| `raise X` | 抛出异常 |
| `raise X from e` | 明确声明「X 是由 e 引起的」，traceback 显示 `The above exception was the direct cause of...` |
| `raise X from None` | 抛出 X，并隐藏原始异常的上下文显示 |

### 两个容易误解的点

**`from None` 不会让程序不报错。** 它只影响异常的**展示方式**，不吞异常、不让程序继续执行。调用处该捕获还得捕获。

**`from None` 不是安全机制。** 它只是让终端输出干净些，不能用来「隐藏敏感信息」——真要记录诊断信息，应该用 `logger.exception()` 写日志（Day 13 会学）。生产环境的做法通常是：**对用户显示简洁消息，同时把完整 traceback 写进日志。**

## 六、测试「应该抛异常」的情况

前一节的 `assert` 只能测「返回值对不对」。但 `parse_guess("abc")` 根本不返回值，它抛异常——这种怎么测？

```python
try:
    parse_guess("abc")
except ValueError:
    pass                                      # 抛了，符合预期
else:
    raise AssertionError("预期出现 ValueError")   # 没抛，测试失败
```

这里的 `else` 是 `try` 语句的 `else` 分支，含义是「**`try` 块没有发生异常时执行**」。

逻辑是反过来的：

- 抛了 `ValueError` → 进 `except` → `pass` → 测试通过
- 没抛异常 → 进 `else` → 主动抛 `AssertionError` → 测试失败

**`else` 这一支不能省。** 少了它，`parse_guess("abc")` 即使一声不响地返回了什么东西，测试也会「通过」——又是一个假测试。

> Day 21 学了 pytest 之后，这六行可以压缩成一行：
> ```python
> with pytest.raises(ValueError):
>     parse_guess("abc")
> ```
> 但先用原生写法理解一遍「测异常」的逻辑是值得的，否则 `pytest.raises` 只是个记不住的咒语。

## 七、最终代码

```python
def parse_guess(user_input: str) -> int:
    try:
        int_num = int(user_input)
    except ValueError:
        raise ValueError("输入格式错误，请输入整数") from None

    if not 1 <= int_num <= 100:
        raise ValueError("数字必须在 1～100")

    return int_num


def test_invalid_input() -> None:
    assert parse_guess("2") == 2
    assert parse_guess("50") == 50
    try:
        parse_guess("abc")
    except ValueError:
        pass
    else:
        raise AssertionError("预期出现 ValueError")

    try:
        parse_guess("0")
    except ValueError:
        pass
    else:
        raise AssertionError("预期出现 ValueError")

    try:
        parse_guess("1000")
    except ValueError:
        pass
    else:
        raise AssertionError("预期出现 ValueError")

test_invalid_input()
```

这一版末尾有 `test_invalid_input()` 调用，所以运行文件真的会执行测试（上一节的 `Day7.py` 漏了这一步）。

### 回头看还能改进的地方

**一、三段 `try/except/else` 几乎一模一样。** 这是 `pytest.mark.parametrize` 的典型场景，能压缩成一张参数表。

**二、用异常消息区分错误类型不够稳。** 现在两种错误都是 `ValueError`，调用方想分别处理就只能去比较消息文本：

```python
except ValueError as e:
    if "格式" in str(e):     # 脆弱：改一个字就失效
        ...
```

更稳的做法是定义自己的异常类：

```python
class GuessFormatError(ValueError): ...
class GuessRangeError(ValueError): ...
```

这样调用方按**类型**分支，和文案无关。这个问题在 Day 14 会以更明显的形式暴露——那边的测试直接写了 `assert str(e) == "类型错误"`，把测试和中文文案焊死了。

**三、`q` 的判断可以更宽容。** `if input_num.strip().lower() == "q"` 能同时接受 `Q`、`q` 和前后带空格的输入。

## 八、复习自测

1. 第一版为什么输入 `"101"` 会提示「输入格式错误」？
2. 「不要捕获自己准备抛出的异常」具体该怎么做到？
3. `try` 的范围为什么要尽量小？包太大有什么具体危害？
4. `raise X from None` 和 `raise X` 的区别是什么？它会让程序不报错吗？
5. `try/except/else` 测异常时，`else` 分支什么时候执行？少了它会怎样？
6. 两种错误都用 `ValueError` + 不同消息来区分，有什么问题？

<details>
<summary>参考答案</summary>

1. 因为 `raise ValueError("数字必须在 1～100")` 写在 `try` 块**内部**，被同一个 `try` 的 `except ValueError` 捕获，然后重新包装成了「输入格式错误」。
2. 把自己 `raise` 的那一行移到 `try` 块**外面**。本节的做法是 `try` 只包 `int()` 转换，范围检查放在其后。
3. 范围越大，越可能误捕获别处抛出的同类异常，把真正的 bug 伪装成「用户输入错误」而被静默处理掉，排查时极难定位。另外读代码的人得扫完整个 try 块才知道在防什么。
4. `from None` 隐藏原始异常的上下文显示，traceback 只显示新异常。它只改变展示方式，**不会**吞掉异常，程序照样会报错、照样需要调用方捕获。
5. `else` 在 `try` 块**没有发生异常**时执行。少了它，被测函数即使没抛异常（甚至正常返回了值），测试也会静默通过——变成一个永远不会失败的假测试。
6. 调用方想区分两种错误只能比较异常消息的文本，改一个字就失效。应该定义不同的异常类（如 `GuessFormatError`、`GuessRangeError`），让调用方按类型判断。

</details>
