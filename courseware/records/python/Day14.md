# Day 14 · 错误语义落地、异常继承与运算符优先级

> **学习日** 2026-10-27（10:38 - 11:35，5 轮对话）
> **对应代码** [`dailypractice/Day14/`](../../../dailypractice/Day14/)（`history.py` / `test_history.py`）
> **原始对话** `courseware/_raw/markdown/03_Python每日练习出题.md`（对话里称「Day 14」）

> `history.py` 第四遍，也是 A 线基础阶段的收尾。
> Day11 读写与校验 → Day12 测试覆盖 → Day13 日志 → **Day14 错误语义**。

## 本节掌握

- 把 Day13 讨论的错误语义真正实现出来
- **`json.JSONDecodeError` 是 `ValueError` 的子类**——这件事影响捕获和测试
- 裸 `raise` 重新抛出当前异常；`raise 异常类` 和 `raise 异常实例` 的区别
- **`|` 的运算符优先级高于比较运算符**（本节最阴的 bug）
- 链式比较写反会导致条件永远不成立
- `logger.warning()` 和 `raise` 的职责分工
- 测试精度：只验证异常类型还不够

这一节有四个 bug，其中两个让范围校验**完全失效**而测试照样通过。

---

# 第一部分 · 知识讲解

## 1. 错误语义的落地

Day13 确定了规则，Day14 把它实现出来：

| 情况 | 行为 | 理由 |
|---|---|---|
| 文件不存在 | 记 WARNING，返回 `[]` | 首次运行，正常状态 |
| JSON 语法错误 | 抛 `json.JSONDecodeError` | 文件损坏，不能伪装成空记录 |
| 顶层不是列表 | 抛 `ValueError` | 语法合法但结构不对 |
| 元素不是整数 | 抛 `ValueError` | 数据类型不对 |
| 数字不在 1~100 | 抛 `ValueError` | 违反业务规则 |
| 数据合法 | 返回列表 | 正常 |

和 Day11-13 的最大区别：**不再把所有失败都压成 `[]`**。调用方现在能区分「没有历史记录」和「历史记录坏了」。

## 2. `JSONDecodeError` 是 `ValueError` 的子类

这是本节必须知道的事实。实测：

```python
>>> issubclass(json.JSONDecodeError, ValueError)
True
>>> [c.__name__ for c in json.JSONDecodeError.__mro__]
['JSONDecodeError', 'ValueError', 'Exception', 'BaseException', 'object']
```

两个直接后果：

**后果一：`except ValueError` 会连 JSON 语法错误一起抓住。**

```python
try:
    history = load_history("history.json")
except ValueError:
    print("数据有问题")     # 分不清是语法坏了还是业务规则不符
```

**后果二：捕获顺序有讲究。** 要分别处理就必须把子类放前面：

```python
try:
    history = load_history("history.json")
except json.JSONDecodeError:      # 子类在前
    print("文件损坏了")
except ValueError:                # 父类在后
    print("数据不符合要求")
```

顺序颠倒的话，`except ValueError` 会先匹配上，`except json.JSONDecodeError` 永远不会执行——而且 Python **不会**警告你这一点。

> 一般规律：**`except` 子句按书写顺序匹配，第一个匹配上的就执行。** 所以具体的异常要写在前面，宽泛的写在后面。这也是为什么 `except Exception` 一定要放最后（如果非要写的话）。
>
> 这同时说明用 `ValueError` 表示业务校验错误是个将就的方案。更干净的做法见本节「现在回头看」。

## 3. 重新抛出异常：裸 `raise`

第一版写了这样一行：

```python
except json.JSONDecodeError:
    logger.error("JSON 不正确")
    raise json.JSONDecodeError      # ← 错的
```

`raise json.JSONDecodeError` 抛的是**异常类本身**，而不是异常实例。Python 会尝试自动构造实例（相当于 `json.JSONDecodeError()`），但这个类的构造函数需要三个参数（`msg`、`doc`、`pos`），于是引发一个新的 `TypeError`——**原始的 JSON 解析错误反而丢了**。

正确写法是裸 `raise`：

```python
except json.JSONDecodeError:
    logger.error("JSON 不正确")
    raise                           # 重新抛出当前正在处理的那个异常
```

裸 `raise` 把捕获到的异常原样抛出去，**保留原始的错误消息和完整 traceback**。

三种写法的区别：

| 写法 | 效果 |
|---|---|
| `raise` | 原样重抛当前异常，保留 traceback（**在 `except` 块里才能用**） |
| `raise ValueError("消息")` | 抛一个新异常实例 |
| `raise ValueError` | 抛异常类，Python 自动构造无参实例；构造需要参数的类会出错 |

> 这一节其实还有个更简单的选择：**内层的 `try/except` 可以整个删掉**。如果除了记一条日志没有别的处理，不如让 `json.load()` 的异常自然向上传播——少一层嵌套，少一个出错的机会。Day14 最终代码就是这么做的。

## 4. 运算符优先级：`|` 不是「或」

这是本节最值得记住的坑。两版范围校验都写错了，而且**错得等价**。

### 第一版

```python
if 100 < item < 1:
```

这是**链式比较**，等价于 `100 < item and item < 1`，要求 `item` 同时大于 100 且小于 1——**永远不成立**。这个条件等于没写。

### 第二版

```python
if 100 < item | item < 1:
```

想用 `|` 表达「或」，但 `|` 是**按位或**运算符，而且**它的优先级高于比较运算符**。所以这行实际的计算顺序是：

```python
100 < (item | item) < 1
```

而 `item | item` 恒等于 `item`（任何数和自己按位或都是自己），所以这行等价于：

```python
100 < item < 1
```

**和第一版完全一样，还是永远不成立。** 实测：

| `item` | `100 < item < 1` | `100 < item \| item < 1` | `100 < item or item < 1` | `not 1 <= item <= 100` |
|---:|---|---|---|---|
| 0 | False | False | **True** | **True** |
| 1 | False | False | False | False |
| 50 | False | False | False | False |
| 100 | False | False | False | False |
| 101 | False | False | **True** | **True** |
| 10000 | False | False | **True** | **True** |

前两列全是 False——**范围校验形同虚设，`[0]` 和 `[10000]` 都能通过**。而测试里那条「数值越界应该抛异常」的断言，在修对之前是过不了的，所以这个 bug 被测试抓住了。

### 为什么会想用 `|`

`|` 和 `&` 在很多语言里确实用于位运算，而 Python 里**逻辑运算只用 `and`、`or`、`not` 这三个英文单词**。

| 符号 | Python 含义 | 优先级 |
|---|---|---|
| `and` / `or` / `not` | 逻辑运算 | **低于**比较运算符 |
| `&` / `\|` / `^` / `~` | 按位运算 | **高于**比较运算符 |

优先级的差异正是陷阱所在：

```python
a < b and c < d          # (a < b) and (c < d)   ← 符合直觉
a < b | c < d            # a < (b | c) < d       ← 不符合直觉
```

> 实用建议：**写范围判断就用 `not 1 <= item <= 100`。** 它只有一个比较链、没有优先级问题，而且正面描述了合法区间（Day06 的教训）。`100 < item or item < 1` 虽然正确，但要读两遍才能确认边界没错。

## 5. `logger.warning()` 与 `raise` 的分工

| 机制 | 做什么 | 影响控制流吗 | 谁看得到 |
|---|---|---|---|
| `logger.warning()` | 留一条记录 | **不影响**，程序继续 | 开发者（事后看日志） |
| `raise` | 中断当前函数，把问题交给调用方 | **影响**，未被捕获则一路上抛 | 调用方（运行时） |

**两者不互斥。** 值得记录的错误可以先写日志再抛异常：

```python
if type(data) is not list:
    logger.error("类型错误")          # 给开发者留痕
    raise ValueError("类型错误")       # 让调用方知道
```

但要注意**不要在多个层级重复记录同一个异常**。常见的做法是：底层只抛不记，最外层统一捕获并记录一次；或者底层记一次，上层只处理不再记。否则一个错误在日志里出现五遍，排查时很干扰。

## 6. 测试精度：验证类型还不够

原来的异常测试：

```python
try:
    load_history(str(temp_path))
except ValueError:
    pass
else:
    raise AssertionError("应该抛异常")
```

这个写法是对的（有 `else` 分支，不会变成假测试），但精度不足：**它只确认「抛了 ValueError」，没确认「是因为我想测的那个原因抛的」**。

三条业务校验都抛 `ValueError`，所以这个测试在「顶层不是列表」「元素类型错误」「数字越界」任何一种情况下都会通过——哪怕代码把三个分支的判断条件写混了，测试也发现不了。

于是改成同时验证错误消息：

```python
except ValueError as e:
    assert str(e) == "类型错误"
```

精度提高了，但引入了新问题（见下面「现在回头看」）。

---

# 第二部分 · 当天的练习

## 一、题目

按 Day13 定的规则改 `load_history()`，并写六类测试。额外回答三个问题：

1. 为什么文件不存在返回 `[]`，JSON 格式错误却抛异常？
2. `logger.warning()` 和 `raise ValueError()` 的职责分别是什么？
3. 为什么预期异常没发生时，必须主动让测试失败？

## 二、四个 bug

### Bug 1：`raise json.JSONDecodeError`

抛的是类不是实例，构造需要参数，结果引发 `TypeError` 并丢掉原始异常。见知识讲解第 3 节。

### Bug 2：`if 100 < item < 1:`

链式比较写反，条件永远不成立。见知识讲解第 4 节。

### Bug 3：`raise ValueError("<UNK>")`

占位符忘了替换就提交了。调用方拿到 `<UNK>` 完全不知道发生了什么。

> 这个占位符至今还留在对话记录里——它正是整理素材时在 14 个会话中扫到的那三个 `<UNK>` 之一。

### Bug 4：`if 100 < item | item < 1:`

想修 Bug 2，结果用了按位或，**改完和没改一样**。见知识讲解第 4 节的实测表。

> 两次修复都没修对范围校验，第三次用 `or` 才成功。这类 bug 的共同点是：**代码看起来在做某件事，实际什么都没做，而且不报错。** 唯一能抓住它的是针对边界值的测试。

## 三、三个问题的回答

当时的回答都对：

> 1、不存在就是没读到，返回空，格式错误是有值，但是有问题，抛异常告诉调用方检查数据
> 2、warning 是记录日志，raise 是抛出异常，让调用方知道问题
> 3、预期异常没发生，也说明测试不符合预期，说明测试失败。需要让测试失败。

第一条抓住了关键区别：**「没读到」和「读到了但是坏的」是两种不同的状态**，不该用同一个返回值表示。

第三条对应的是前面反复出现的「假测试」问题——`try/except` 少了 `else` 分支，预期异常没发生时测试会静默通过（Day07、Day10、Day11 各踩过一次）。

## 四、最终代码

`history.py`：

```python
import json
import logging

logger = logging.getLogger(__name__)


def save_history(filename: str, data: list[int]) -> None:
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def load_history(filename: str) -> list[int]:
    try:
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
        if type(data) != list:
            logger.error("类型错误")
            raise ValueError("类型错误")
        for item in data:
            if type(item) != int:
                logger.error("元素类型错误")
                raise ValueError("元素类型错误")
            if 100 < item or item < 1:
                logger.error("元素需要是1~100的整数")
                raise ValueError("元素需要是1~100的整数")
        return data
    except FileNotFoundError:
        logger.warning("文件不存在")
        return []
```

结构上比 Day11 清爽很多：内层 `try` 删掉了，JSON 语法错误自然向上抛；只保留 `FileNotFoundError` 一个捕获，因为只有它需要「返回空列表」的特殊待遇。

`test_history.py` 六类场景齐全，而且 JSON 语法错误那条用的是 `except json.JSONDecodeError`（不是 `except ValueError`）——这一点很重要，因为后者会因为继承关系把语法错误和业务错误混为一谈。

## 五、现在回头看

### 一、测试和中文文案焊死了

```python
except ValueError as e:
    assert str(e) == "类型错误"
```

提高精度的代价是：**业务代码的提示文案变成了测试的契约**。把 `raise ValueError("类型错误")` 改成「数据结构错误」，三个测试立刻全断——而代码的行为一点没变。

更稳的做法是定义自己的异常类，按**类型**断言：

```python
class HistoryError(ValueError):
    """历史记录相关错误的基类。"""

class HistoryStructureError(HistoryError):
    """顶层结构不是列表。"""

class HistoryItemTypeError(HistoryError):
    """元素不是整数。"""

class HistoryRangeError(HistoryError):
    """数字超出 1~100。"""
```

```python
# 业务代码
raise HistoryStructureError("历史记录顶层必须是列表")

# 测试
with pytest.raises(HistoryStructureError):
    load_history(str(temp_path))
```

好处有三个：

- 文案随便改，测试不受影响
- 调用方能按类型分别处理，不用比较字符串
- 继承自 `ValueError` 保持了向后兼容（原来 `except ValueError` 的代码照样能接住）

> 这条也记在仓库根目录 `README.md` 的待办里。

### 二、用 `ValueError` 导致语法错误和业务错误混在一起

因为 `JSONDecodeError` 也是 `ValueError`，调用方写 `except ValueError` 时会同时接住两类错误。而且这里有个更隐蔽的风险：

```python
temp_path.write_text('{"a":1}', encoding="utf-8")
try:
    load_history(str(temp_path))
except ValueError as e:
    assert str(e) == "类型错误"        # 如果抛的是 JSONDecodeError，这里会断言失败
```

断言失败时报的是「字符串不相等」，但真正的原因可能是「JSON 根本没解析成功」——**错误信息会把排查方向带偏**。上面的自定义异常类能同时解决这个问题。

### 三、`type(data) != list` 相比 Day13 退步了

Day13 用的是 `type(ls) is not list`，Day14 退回了 `!=`。对类型对象的比较应该用 `is`：类型是单例对象，`is` 比较身份更准确，也不会被自定义的 `__eq__` 干扰。

注意**不能**换成 `isinstance`：元素检查那里必须拒绝 `True`（`bool` 是 `int` 的子类），详见 Day11 知识讲解第 6 节。

### 四、`indent=4`，前三遍都是 `indent=2`

不影响正确性，但同一个项目里格式参数应该统一。这类不一致通常是复制粘贴时顺手改的，日积月累会让文件格式五花八门。

### 五、范围判断建议改写

```python
if 100 < item or item < 1:          # 正确，但要读两遍确认边界
if not 1 <= item <= 100:            # 推荐：正面描述合法区间
```

## 六、复习自测

1. `json.JSONDecodeError` 和 `ValueError` 是什么关系？这会造成什么影响？
2. `except ValueError` 写在 `except json.JSONDecodeError` 前面会怎样？Python 会报错吗？
3. `raise`、`raise ValueError("x")`、`raise ValueError` 三者的区别？
4. `if 100 < item < 1:` 对 `item = 0` 的结果是什么？为什么？
5. `100 < item | item < 1` 实际上在算什么？为什么和 `or` 不等价？
6. Python 里的逻辑或是 `|` 还是 `or`？两者优先级有什么不同？
7. `logger.warning()` 会中断程序吗？它和 `raise` 的分工是什么？
8. 只断言 `except ValueError: pass` 精度不够，为什么？
9. 改成 `assert str(e) == "类型错误"` 引入了什么新问题？更好的做法是什么？

<details>
<summary>参考答案</summary>

1. `JSONDecodeError` 是 `ValueError` 的**子类**。影响是 `except ValueError` 会把 JSON 语法错误也捕获进来，无法区分「文件损坏」和「数据不符合业务规则」。
2. `except ValueError` 会先匹配上，`except json.JSONDecodeError` 永远不执行。Python **不会**报错或警告，所以这是个静默的逻辑错误。具体异常必须写在宽泛异常前面。
3. 裸 `raise` 原样重抛当前正在处理的异常，保留原始 traceback（只能在 `except` 块里用）；`raise ValueError("x")` 抛一个新的异常实例；`raise ValueError` 抛异常类，Python 会尝试自动构造无参实例，对于构造需要参数的类（如 `JSONDecodeError`）会引发 `TypeError`。
4. `False`。这是链式比较，等价于 `100 < 0 and 0 < 1`，第一个条件就不成立。这个判断对任何值都是 `False`，等于没写。
5. 实际算的是 `100 < (item | item) < 1`，因为 `|` 优先级高于比较运算符。而 `item | item` 恒等于 `item`，所以等价于 `100 < item < 1`——永远为假。
6. 逻辑或是 `or`。`or`/`and`/`not` 的优先级**低于**比较运算符，所以 `a < b or c < d` 符合直觉；`|`/`&` 是按位运算，优先级**高于**比较运算符，所以 `a < b | c < d` 会先算 `b | c`。
7. 不会中断。`logger.warning()` 只留一条记录给开发者事后排查，程序继续执行；`raise` 中断当前函数并把问题交给调用方。两者不互斥，但要避免在多个层级重复记录同一个异常。
8. 因为三条业务校验都抛 `ValueError`，这个断言在任何一种校验失败时都会通过——即使代码把三个分支的判断条件写混了也发现不了。
9. 新问题是业务代码的提示文案变成了测试契约，改一个字测试就断，而代码行为并没有变。更好的做法是定义自定义异常类（如 `HistoryStructureError`），按异常**类型**断言，与文案解耦。

</details>
