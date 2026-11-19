---
kind: lesson
outline: [2, 2]
time: 45 分钟
uses: [with open, encoding, json.dump 与 json.load, bool 是 int 的子类, 逐层校验, tempfile]
record:
  - text: 当时的代码 Day11/
    link: https://github.com/syjlpineapple/ai-learning/tree/main/dailypractice/Day11
---

# Day 11：文件读写与 JSON

到昨天为止，猜数字的所有数据都放在内存里：猜过哪些数、猜了几次，程序一关就全没了。

今天让程序「记住」东西：把猜过的数字存进文件，下次启动再读出来。存的格式用 JSON。以后调大模型 API，请求和返回也都是 JSON，今天打的底子后面天天要用。

## 一、JSON 长什么样

JSON 是一种文本格式，长得和 Python 的字典、列表几乎一样：

```json
{"name": "张三", "guesses": [23, 50, 42], "won": true}
```

读进 Python 以后，它们一一对应：

| JSON | Python |
|---|---|
| `{}` 对象 | `dict` |
| `[]` 数组 | `list` |
| 字符串、数字 | `str`、`int` / `float` |
| `true` / `false` / `null` | `True` / `False` / `None` |

```python
print(json.loads('[1, true, null, "a", 2.5]'))
```

```text
[1, True, None, 'a', 2.5]
```

## 二、四个方法：带 s 的处理字符串

| 方法 | 方向 |
|---|---|
| `json.dumps(data)` | Python 对象 → JSON **字符串** |
| `json.loads(text)` | JSON **字符串** → Python 对象 |
| `json.dump(data, f)` | Python 对象 → 写进**文件** |
| `json.load(f)` | 从**文件**读 → Python 对象 |

记法只有一句：带 `s` 的是 string，不带的是 file。

写文件时常加两个参数，看一眼效果就明白：

```python
player = {"name": "张三", "guesses": [23, 50, 42], "won": True}
print(json.dumps(player))
print(json.dumps(player, ensure_ascii=False))
print(json.dumps([10, 20, 30], indent=2))
```

```text
{"name": "\u5f20\u4e09", "guesses": [23, 50, 42], "won": true}
{"name": "张三", "guesses": [23, 50, 42], "won": true}
[
  10,
  20,
  30
]
```

不加 `ensure_ascii=False`，中文会变成 `\u5f20\u4e09` 这样的转义码。两种都是合法 JSON，读回来都是「张三」，区别只是人能不能直接看懂文件。`indent=2` 让内容换行缩进，给人看的文件加上它。

## 三、`with open`：打开、用完、自动关

```python
with open(filename, "w", encoding="utf-8") as f:
    json.dump(history, f, ensure_ascii=False, indent=2)
```

`with` 保证离开这个代码块时文件一定被关上，中途抛了异常也一样。不关文件，写的内容可能还留在缓冲区里，没真正落到磁盘上。

第二个参数是打开模式：

| 模式 | 意思 | 文件已存在时 |
|---|---|---|
| `"r"` | 读 | 从头读；文件不存在就抛 `FileNotFoundError` |
| `"w"` | 写 | **先清空** |
| `"a"` | 追加 | 接着末尾写 |

`"w"` 一打开就清空，哪怕你什么都没写：

```python
p.write_text("旧内容", encoding="utf-8")
with open(p, "w", encoding="utf-8") as f:
    pass
print(repr(p.read_text(encoding="utf-8")))
```

```text
''
```

存历史记录每次写完整列表，用 `"w"` 正合适；想往日志后面续写就得用 `"a"`。

最后是 `encoding="utf-8"`：**读和写都要写上。** 不写的话，Python 用系统默认编码，中文 Windows 上通常是 GBK。明天你会亲眼看到少写这一个参数的后果。

## 四、读进来的数据不能直接信

读历史文件可能遇到三类问题：

| 情况 | 会发生什么 |
|---|---|
| 文件不存在 | `open()` 抛 `FileNotFoundError` |
| 文件在，但不是合法 JSON（比如内容是 `hello`） | `json.load()` 抛 `json.JSONDecodeError` |
| 是合法 JSON，但不是你要的（`{"guess": 10}`、`[10, "abc"]`、`[101]`） | **什么都不抛**，只能自己检查 |

第三类最容易漏。还有一个坑藏在里面：Python 的 `True` 其实是整数 1。

```python
print(isinstance(True, int), type(True) is int, True + True)
```

```text
True False 2
```

所以 `[10, true]` 用 `isinstance(i, int)` 检查会放进来。要「恰好是 int」，得用 `type(i) is int`。

检查的顺序是**从外往里**：先确认最外层是列表，再看列表里的每个元素。外层都不对就去遍历里面，程序会直接崩，下面的讲评里就有这个例子。

记住今天这句话：**外部数据不能因为来自自己的文件，就默认它一定正确。** 文件可能被手改过、被别的程序写坏，以后的 API 返回、模型输出也是一样。

## 五、今天的作业

新建 `history.py`，实现两个函数：

```python
def save_history(history: list[int], filename: str) -> None: ...
def load_history(filename: str) -> list[int]: ...
```

`load_history()` 的约定：文件合法就返回数字列表；文件不存在、JSON 损坏、顶层不是列表、元素不是整数、数字不在 1～100，**一律返回 `[]`，不让程序崩溃**。

再写 `test_history.py`，用 `tempfile.TemporaryDirectory()` 建临时目录放测试文件，不要碰真实的 `history.json`。至少测：正常读写、文件不存在、内容损坏、`[10, "abc", 200]`。

思考题：

1. 为什么保存时要用 `with open(...)`？
2. 如果把任意 JSON 内容直接当成历史记录，会出什么问题？
3. 为什么「文件不存在」和「内容损坏」是两种不同的错误？

## 六、小测

**1.** 想把一个字典变成 JSON 字符串打印出来看看，用哪个？

- A. `json.dump`
- B. `json.dumps`
- C. `json.loads`

**2.** `open("history.json", "w")` 打开一个已经有内容的文件，然后一个字都不写就关掉，文件里还剩什么？

- A. 原来的内容
- B. 什么都没有了
- C. 报错

**3.** 文件内容是 `[10, true, 30]`，下面哪个检查能把 `true` 拦住？

- A. `isinstance(i, int)`
- B. `type(i) is int`
- C. 两个都能

<details>
<summary>答案</summary>

1. B。带 `s` 的处理字符串，`dump` 是写进文件的。
2. B。`"w"` 模式一打开就清空。
3. B。`bool` 是 `int` 的子类，`isinstance(True, int)` 是 `True`。

</details>

## 讲评（10-23）

那天你交了好几版，一路是被测试和代码审查推着往前走的。

**第一版**直接遍历读进来的数据，没先看最外层是什么。文件内容是 `{"guess": 10}` 时，遍历字典拿到的是键：

```python
for i in {"guess": 10}:
    print(repr(i))
```

```text
'guess'
```

字符串过不了你的类型检查，于是抛出 `TypeError: 类型错误`。这个异常没人接，程序就崩了，和「不要让程序直接崩溃」的要求正好相反。改法是先加一句 `if type(ls) != list: return []`，校验失败也统一 `return []`，不再 `raise`。

**第二版**的测试报了 `AssertionError`：存的是 `[10, 20, 30]`，读回来是 `[]`。你没急着乱改，而是先把文件路径和返回值打印出来，确认文件写对了、是读取这边出的问题。最后定位到这一行：

```python
if not type(i) != int:
    return []
```

多了一个 `not`。代入 `i = 10` 算一遍：`type(10) != int` 是 `False`，前面再加 `not` 就成了 `True`：

```python
i = 10
print(not type(i) != int)
```

```text
True
```

合法的整数全被当成非法了。看到 `not ... !=` 这种双重否定，就停下来代入一个具体值手算。这也是你写的 `assert` 第一次真正抓到 bug。

**测试**那边有两处要记住：

- 「文件不存在」一开始写成了 `try: load_history(...) except FileNotFoundError: pass`。`load_history()` 自己已经把这个异常接住并返回 `[]` 了，`except` 永远进不去，而且没有任何断言，函数返回什么这段都「通过」。应该直接断言 `load_history(...) == []`：测试写的是需求，需求是「返回空列表」。
- `assert load_history("error.json") == []` 用的是相对路径。从哪个目录启动程序，它就去哪个目录找 `error.json`，测到的可能是「文件不存在」，也可能是你放在 Day11 目录里那个写坏的文件。要测坏数据，就在临时目录里用 `write_text("hello")` 自己造一个。

最终的 `load_history()` 把六种情况都处理对了，实测：

```text
[10, 20, 30]       -> [10, 20, 30]
hello              -> []
{"guess": 10}      -> []
[10, "abc", 30]    -> []
[10, 101]          -> []
[10, true]         -> []
不存在           -> []
```

最后那道「为什么不跳过坏的元素、保留好的」，你答的是：如果错误会影响整体，就该返回 `[]`，这样才知道数据有问题。这个判断很好。不过也看出一个新问题：七种情况里有六种都返回 `[]`，调用的人分不清「还没玩过」和「文件坏了」。这个问题会在 Day 13 正面解决。

## 加练

- [排行榜存盘](加练/day11_排行榜存盘.md)：把 `{名字: 次数}` 存进一个普通文本文件，练 `open` 的几种模式、`encoding` 和 `pathlib`。
- [JSON 存档](加练/day11_JSON存档.md)：每局游戏存一条完整的 JSON 记录，练 `dumps` / `loads` 和「JSON 的键只能是字符串」这个细节。
