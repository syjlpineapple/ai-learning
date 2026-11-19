---
kind: lesson
outline: [2, 2]
time: 40 分钟
uses: [logging, 日志级别, getLogger(__name__), 模块记录、入口配置, 返回值的歧义]
record:
  - text: 当时的代码 Day13/
    link: https://github.com/syjlpineapple/ai-learning/tree/main/dailypractice/Day13
---

# Day 13：日志与返回值的语义

现在的 `load_history()` 有六条路会返回 `[]`。某天它真的返回了 `[]`，你想知道为什么，只能去翻代码、加 `print`。

今天用 `logging` 给每条路留个记号。做完以后你会发现一个更根本的问题：日志能告诉**你**发生了什么，却告诉不了**调用这个函数的代码**。

## 一、用 logging 代替 print

`print` 写死了「打到屏幕上」。`logging` 只管「记一条什么级别的消息」，显示不显示、显示到哪、什么格式，交给配置决定。

五个级别，从低到高：

| 级别 | 什么时候用 |
|---|---|
| `DEBUG` | 排查问题时才看的细节 |
| `INFO` | 正常流程的关键节点，比如「开始读取历史记录」 |
| `WARNING` | 不正常，但程序还能继续，比如「文件不存在，用空记录」 |
| `ERROR` | 某个操作失败了 |
| `CRITICAL` | 严重到程序没法继续 |

级别是个门槛：配成 `INFO`，`INFO` 及以上都输出，`DEBUG` 被挡掉。今天的用法是正常节点记 `INFO`，各种读取失败记 `WARNING`，因为失败了程序还能拿空列表继续跑。

## 二、`getLogger(__name__)`：模块只管记

每个模块开头固定写一行：

```python
logger = logging.getLogger(__name__)
```

`__name__` 就是 Day 10 学的那个变量，被导入时它是模块的完整路径，所以日志会自动带上「这条是谁记的」。

配置交给程序入口，而且只配一次：

```python
logging.basicConfig(level=logging.INFO)
```

为什么不让每个模块自己配？项目里有 `history.py`、`api_client.py` 好几个模块，各配各的就会打架；而且 `basicConfig()` 只有第一次调用生效，后面的悄悄失效，最终效果取决于谁先被导入。记住这条分工：**模块负责记录日志，应用入口负责配置日志。**

## 三、没配置的时候会怎样

这是你今天自己撞上的问题，所以实际跑一下看清楚。用你 Day 13 的 `history.py`，依次读：不存在的文件、`[10, 20, 30]`、`hello`、`[10, 101]`。

没有调用 `basicConfig()`：

```text
== 文件不存在
历史记录文件不存在
[]
== [10, 20, 30]
[10, 20, 30]
== hello
JSON 格式错误
[]
== [10, 101]
历史记录数字超出范围
[]
```

调用 `logging.basicConfig(level=logging.INFO)` 以后：

```text
== 文件不存在
WARNING:dailypractice.Day13.history:历史记录文件不存在
[]
== [10, 20, 30]
INFO:dailypractice.Day13.history:开始读取历史记录
[10, 20, 30]
== hello
INFO:dailypractice.Day13.history:开始读取历史记录
WARNING:dailypractice.Day13.history:JSON 格式错误
[]
== [10, 101]
INFO:dailypractice.Day13.history:开始读取历史记录
WARNING:dailypractice.Day13.history:历史记录数字超出范围
[]
```

对比两段，有两点要看清楚：

- 没配置时，**WARNING 还是会出来**，只是光秃秃一句话，没有级别和模块名。这是 Python 的兜底：什么都没配时，WARNING 及以上直接打到错误输出，免得警告一声不响。
- 没配置时，**INFO 一条都没有**。默认门槛是 WARNING。

这说明不能用「日志有没有打出来」去判断代码有没有走到那一行。WARNING 出来了、INFO 没出来，很容易误以为「开始读取」那行没执行。

## 四、日志救不了调用方

记日志只是给开发者留痕，它不改变函数的返回值。看看现在调用方拿到的东西：

| 实际情况 | 日志 | 调用方拿到 |
|---|---|---|
| 文件不存在 | WARNING 文件不存在 | `[]` |
| JSON 坏了 | WARNING JSON 格式错误 | `[]` |
| 顶层不是列表 | WARNING 数据结构错误 | `[]` |
| 元素不是整数 | WARNING 包含非整数 | `[]` |
| 数字越界 | WARNING 超出范围 | `[]` |
| 文件里本来就是 `[]` | 没有 WARNING | `[]` |

于是调用方只能这样写：

```python
history = load_history("history.json")
if history == []:
    print("没有历史记录")   # 文件也许是坏的，这句话可能在撒谎
```

**一个返回值表示好几种意思，调用方就没法做出正确的决定。** 解决办法有三种：

| 方案 | 做法 | 适合 |
|---|---|---|
| A | 返回空值 + 记日志（现在的做法） | 读不到也无所谓的数据 |
| B | 该报错的情况抛异常 | 错误必须有人处理的场景 |
| C | 同时返回结果和错误，比如 `history, error = ...` | 错误是常规分支的场景 |

没有哪种永远最好，要看「读不到」在业务上意味着什么。

## 五、今天的作业

在 `history.py` 里引入 `logging`：

1. 正常读取时记一条 `INFO`
2. 文件不存在、JSON 格式错误时各记一条 `WARNING`，并继续返回 `[]`
3. 不用 `except Exception`，保留原来的校验
4. 昨天的六个测试照样要过

再回答两个问题：

- A. 文件不存在时已经记了 `WARNING`，还需要 `print("文件不存在")` 吗？
- B. `logger.warning()` 和 `raise ValueError()` 有什么区别？能互相替代吗？

## 六、小测

**1.** 级别配成 `INFO`，下面哪条不会输出？

- A. `logger.debug(...)`
- B. `logger.warning(...)`
- C. `logger.error(...)`

**2.** 把 `basicConfig()` 写进 `history.py` 的 `if __name__ == "__main__":` 里，测试文件 `import history` 后跑测试，这行会执行吗？

- A. 会
- B. 不会

**3.** 函数里记了 `logger.warning("文件不存在")` 再 `return []`，调用方能知道文件不存在吗？

- A. 能，日志会传给调用方
- B. 不能，调用方只拿到 `[]`

<details>
<summary>答案</summary>

1. A。门槛是 INFO，DEBUG 比它低。
2. B。被导入时 `__name__` 是模块路径，不是 `"__main__"`。
3. B。日志是给人看的，程序只能拿到返回值或者异常。

</details>

## 讲评（10-26）

你第一次交的其实还是 Day 12 的代码，GPT 顺手指出了读文件少了 `encoding="utf-8"`。第二次加上了日志，`getLogger(__name__)` 和两条 `WARNING` 都放对了位置。GPT 给的修改版做了三处调整：补回 `encoding`；把类型和范围校验挪出了 JSON 解析的 `try`，让那个 `try` 只管语法错误；`basicConfig()` 从模块顶层挪进 `if __name__ == "__main__":`。

挪完你马上发现：「这样调整位置后，执行测试就不生效了」。这个发现很有价值，原因就是第三节和小测第 2 题：测试是导入模块，那一行根本没执行。你把 Day 10 的知识用到了一个新场景里。对学习项目来说，在测试文件顶部配一次 `basicConfig` 就够了。

接着那道进阶题：拿到 `[]` 的调用方，能分清「没有历史」和「数据非法」吗？你答「调用处是不知道的」，一句话说中。再让你在三种规则里选，你选了「文件不存在返回 `[]`，JSON 格式错误抛异常」。理由在两种情况的业务含义不同：文件不存在是第一次玩，正常；文件在却读不出来，是出事了，不该装作「没有记录」。明天就按这条规则改代码。

两个小地方：

- `logger.info("开始读取历史记录")` 写在 `open()` 之后，文件不存在时这条不会记，直接跳到 WARNING。不算 bug，但日志的文字要和位置对得上，它现在的意思其实是「文件已打开，开始解析」。
- 日志没带上是哪个文件，比如 `logger.warning("历史记录文件不存在: %s", filename)`。同一个函数被不同路径调用时，不带参数的日志没法定位。

## 加练

[用日志代替 print](加练/day13_用日志代替print.md)：写一个「宽容」的读取函数，坏的那一局跳过、其他照常用，跳过了什么都记进日志；再单独写入口函数配置日志输出到哪里。练的就是今天的「模块记录、入口配置」。
