---
kind: lesson
outline: [2, 2]
time: 45 分钟
uses: [返回空值还是抛异常, 异常继承, except 的顺序, 裸 raise, 运算符优先级, 自定义异常]
record:
  - text: 当时的代码 Day14/
    link: https://github.com/syjlpineapple/ai-learning/tree/main/dailypractice/Day14
---

# Day 14：错误语义与异常继承

昨天你定了规则：**文件不存在返回 `[]`，JSON 坏了抛异常。** 今天把它写进代码，这也是 Python 基础阶段的最后一课。

写的过程中会碰到三件事：异常之间有「父子关系」、重新抛异常有讲究、`|` 不是「或」。

## 一、新规则

| 情况 | 行为 | 理由 |
|---|---|---|
| 文件不存在 | 记 WARNING，返回 `[]` | 第一次玩，正常 |
| JSON 语法错误 | 抛 `json.JSONDecodeError` | 文件坏了，不能装作没有记录 |
| 顶层不是列表 | 抛 `ValueError` | 语法对，结构不对 |
| 元素不是整数 | 抛 `ValueError` | 类型不对 |
| 数字不在 1～100 | 抛 `ValueError` | 违反规则 |
| 数据合法 | 返回列表 | |

和前三天最大的不同：不再把所有失败都压成 `[]`。调用方终于能分清「没有记录」和「记录坏了」。

## 二、`JSONDecodeError` 是 `ValueError` 的子类

```python
print(issubclass(json.JSONDecodeError, ValueError))
print([c.__name__ for c in json.JSONDecodeError.__mro__])
```

```text
True
['JSONDecodeError', 'ValueError', 'Exception', 'BaseException', 'object']
```

`__mro__` 是这个类的「家谱」，从自己一路往上排到 `object`。`JSONDecodeError` 的父亲就是 `ValueError`。

这带来一个后果。`except` 是**从上往下**挨个比，第一个对得上的就执行，后面的不再看。父类写在前面，子类那条就永远轮不到：

```python
def classify(text):
    try:
        data = json.loads(text)
        if type(data) is not list:
            raise ValueError("类型错误")
        return data
    except ValueError:
        return "数据不符合要求"
    except json.JSONDecodeError:
        return "文件损坏了"

print(classify("ABBC"))
print(classify('{"a": 1}'))
```

```text
数据不符合要求
数据不符合要求
```

`"ABBC"` 明明是文件损坏，却也走进了 `except ValueError`。`except json.JSONDecodeError` 那两行成了**死代码**，而 Python 不报错，也不警告。

记住：**具体的异常写在前面，宽泛的写在后面。** 用到有继承关系的异常时，先查一下 `__mro__`。这个坑后面 Day 15、16 还会再踩，到 Day 17 才彻底改对。

## 三、重新抛出：用裸 `raise`

在 `except` 里记完日志，想把异常原样交出去，写法是一个光秃秃的 `raise`：

```python
try:
    json.loads("ABBC")
except json.JSONDecodeError:
    raise
```

```text
JSONDecodeError: Expecting value: line 1 column 1 (char 0)
```

如果写成 `raise json.JSONDecodeError`，抛的是「异常类」本身，Python 会试着帮你创建一个，但这个类创建时要三个参数：

```text
TypeError: JSONDecodeError.__init__() missing 3 required positional arguments: 'msg', 'doc', and 'pos'
```

原来那个 JSON 错误丢了，换成了一个莫名其妙的 `TypeError`。

更简单的做法：如果 `except` 里除了记日志没别的事，干脆不接，让 `json.load()` 的异常自己往上走。

## 四、`|` 不是「或」

想写「数字小于 1 或者大于 100」，Python 里的「或」是英文单词 `or`。`|` 是**按位或**，而且它的优先级比 `<` 还高。

所以 `100 < item | item < 1` 实际上先算 `item | item`，再做比较：

```text
100 < (item | item) < 1
```

一个数和自己按位或，还是它自己。于是这一行就等于 `100 < item < 1`，要求一个数同时大于 100 又小于 1，永远不成立。实测：

```text
  item | 100<item<1 | 100<item|item<1 | 100<item or item<1 | not 1<=item<=100
     0 | False      | False           | True               | True
     1 | False      | False           | False              | False
    50 | False      | False           | False              | False
   100 | False      | False           | False              | False
   101 | False      | False           | True               | True
 10000 | False      | False           | True               | True
```

前两列全是 `False`，范围检查等于没写。后两列才对。推荐最后一种 `not 1 <= item <= 100`：只有一条比较链，直接描述了合法的区间。

## 五、自定义异常

三条业务校验都抛 `ValueError`，调用方要分清是哪一种，只能比较错误文字。更好的办法是给它们各起一个名字：

```python
class HistoryError(ValueError):
    """历史记录相关错误的基类。"""

class HistoryStructureError(HistoryError):
    """顶层不是列表。"""

class HistoryItemError(HistoryError):
    """元素不是 1~100 的整数。"""
```

`class 名字(父类):` 就是继承。函数里按情况抛不同的类，调用方按类型接：

```python
def parse(text):
    data = json.loads(text)
    if type(data) is not list:
        raise HistoryStructureError("历史记录顶层必须是列表")
    for item in data:
        if type(item) is not int or not 1 <= item <= 100:
            raise HistoryItemError(f"非法元素：{item!r}")
    return data

for text in ["ABBC", '{"a": 1}', "[10, true]", "[10, 20]"]:
    try:
        print(text, "->", parse(text))
    except json.JSONDecodeError:
        print(text, "-> 文件损坏")
    except HistoryError as e:
        print(text, "->", type(e).__name__, e)
```

```text
ABBC -> 文件损坏
{"a": 1} -> HistoryStructureError 历史记录顶层必须是列表
[10, true] -> HistoryItemError 非法元素：True
[10, 20] -> [10, 20]
```

因为它们继承自 `ValueError`，原来写 `except ValueError` 的代码照样接得住。

## 六、今天的作业

1. 按第一节的规则改 `load_history()`：读文件写 `encoding="utf-8"`，用 `getLogger(__name__)`，不用 `except Exception`。
2. 写六类测试。抛异常的用这个模式，**预期的异常没出现，测试必须失败**：

   ```python
   try:
       load_history(str(filename))
   except ValueError:
       pass
   else:
       raise AssertionError("应该抛出 ValueError")
   ```

   第 3 类（JSON 格式错误）要检查 `json.JSONDecodeError`，不能只查 `ValueError`。
3. 回答：为什么文件不存在返回 `[]`，JSON 格式错误却抛异常？`logger.warning()` 和 `raise` 各管什么？为什么预期异常没发生时要主动让测试失败？

## 七、小测

**1.** 下面哪种写法会把原来的异常原样抛出去？

- A. `raise`
- B. `raise json.JSONDecodeError`
- C. `return None`

**2.** `if 100 < item | item < 1:` 对 `item = 0` 的结果是？

- A. `True`
- B. `False`

**3.** `except ValueError` 写在 `except json.JSONDecodeError` 前面，JSON 语法错误会进哪个分支？

- A. `ValueError` 那个
- B. `JSONDecodeError` 那个
- C. Python 会报错提示顺序不对

<details>
<summary>答案</summary>

1. A。B 会变成 `TypeError`，C 把异常吞掉了。
2. B。等于 `100 < 0 < 1`，第一步就不成立。
3. A。子类写在父类后面，永远轮不到，而且 Python 不提示。

</details>

## 讲评（10-27）

这一天你的代码里前后出了四个 bug，有意思的是其中两个让范围检查完全失效，代码却照样能跑。

**第一版**有三处：`raise json.JSONDecodeError`（第三节的 `TypeError`）；`raise ValueError("<UNK>")`，占位文字忘了换，调用方看到 `<UNK>` 什么也不知道；`if 100 < item < 1:`，链式比较写反了，永远不成立。

**第二版**删掉了内层的 `try`，让 JSON 错误自然往上抛，这一步很干净。范围检查改成了 `100 < item | item < 1`。GPT 指出 `|` 是按位或、不能表达「或者」，但没说它为什么恰好和上一版一样没用，原因就是第四节的优先级。拿这一版去跑你后来写的越界测试 `[10,10000,30]`，测试会报：

```text
AssertionError: 应该抛异常
```

第三次改成 `100 < item or item < 1` 才对。这类 bug 的共同点是：代码看起来在检查，实际什么都没查，也不报错。能抓住它的只有专门测边界值的测试。

**测试**六类场景全有，异常都用了 `try/except/else`，没有变成「假测试」。JSON 那条用的是 `except json.JSONDecodeError`，避开了第二节的坑。后来你又主动加了 `assert str(e) == "类型错误"`，检查「是不是因为我想测的那个原因抛的」，精度更高了。实测你最终的测试能跑通，打印 `测试通过！`。

不过这样也有代价：测试和提示文字绑在一起了。哪天把「类型错误」改成「数据结构错误」，代码行为没变，测试却全挂。第五节的自定义异常就是解法：按类型断言，文字随便改。

**三道问答题**都答对了。「不存在就是没读到，格式错误是有值但有问题」，这句话把两种情况的区别说透了。

## 加练

[该返回空值还是抛异常](加练/day14_返回空值还是抛异常.md)：让读取函数返回一个结果对象，把「没有存档」「存档是空的」「存档全坏了」三种情况分开，再练「没有结果」时该返回 `None` 还是抛异常。
