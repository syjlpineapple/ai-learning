---
kind: lesson
outline: [2, 2]
time: 40 分钟
uses: [测试覆盖, 测试隔离, Path.write_text, 类型注解不做运行时检查, except Exception 的危害, 链式比较]
record:
  - text: 当时的代码 Day12/
    link: https://github.com/syjlpineapple/ai-learning/tree/main/dailypractice/Day12
---

# Day 12：测试覆盖与异常粒度

昨天的测试最后全过了。但回头想想：「顶层是字典」那个 bug 是测试发现的吗？不是，是代码审查看出来的，因为测试里压根没有这种情况。

这说明一件事：**测试通过，只代表被测到的那些情况是对的。** 今天不写新功能，把 `load_history()` 该测的情况补齐。

## 一、测试覆盖：把六种情况都摆出来

先列清单，再写测试：

| 场景 | 文件内容 | 预期 |
|---|---|---|
| 1. 正常读取 | `[10, 20, 30]` | `[10, 20, 30]` |
| 2. 文件不存在 | 不创建文件 | `[]` |
| 3. JSON 格式错误 | `hello` | `[]` |
| 4. 顶层结构错误 | `{"guess": 10}` | `[]` |
| 5. 元素类型错误 | `[10, "abc", 30]` | `[]` |
| 6. 数字越界 | `[10, 101]` | `[]` |

每一行对应 `load_history()` 里的一条路。表里少一行，那条路就没人检查。

## 二、测试隔离：临时目录，自己造坏数据

测试不能碰真实的 `history.json`，也不能留下垃圾文件。`tempfile.TemporaryDirectory()` 两件事都管了：建一个独立目录，离开 `with` 就整个删掉。

后五种情况的数据，用 `Path.write_text()` 直接写进文件，而不是调 `save_history()`。原因很简单：`save_history()` 只会写出合法的 JSON，它造不出 `hello` 这种坏文件。**要测读取函数怎么对付坏数据，就绕过正常的写入，自己把坏数据摆到它面前。**

你那天问过一个问题：连着写好几次再读，前面的内容是被读取清掉的吗？不是。读不改文件，每次 `write_text()` 都会覆盖原来的内容：

```python
p.write_text("hello", encoding="utf-8")
print(load_lazy(p))
print(p.read_text(encoding="utf-8"))
```

```text
[]
hello
```

`load_history()` 返回 `[]` 只说明「没拿到合法数据」，文件还在那儿。

## 三、类型注解不检查运行时

函数写了 `-> list[int]`，Python 会保证它返回整数列表吗？看这个「偷懒版」：

```python
def load_lazy(filename) -> list[int]:
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []
```

文件内容是 `{"guess": 10}` 时：

```python
history = load_lazy(p)
print(type(history).__name__, history)
history.append(20)
```

```text
dict {'guess': 10}
AttributeError: 'dict' object has no attribute 'append'
```

返回了字典，Python 一声不吭；等到调用方 `append` 的时候才炸。报错的地方离出问题的地方很远，排查时很容易找错方向。

**类型注解是写给人和编辑器看的，运行时不做检查。** 从文件、网络、用户那里来的数据，只能自己写判断去检查。

同理，编辑器提示「应为类型 'str'，但实际为 'Path'」，也只是类型检查器在说「标注和用法对不上」。`open()` 本来就接受 `Path`，程序照样能跑。想让两边一致，可以把参数标成 `filename: str | Path`，意思是两种都行。

## 四、`except Exception` 为什么不行

上面那个偷懒版看着简单，问题有两个。

第一，`json.load()` 只管语法。`["abc", 101]` 是合法 JSON，它照单全收：

```python
p.write_text('["abc", 101]', encoding="utf-8")
print(load_lazy(p))
```

```text
['abc', 101]
```

第二，`except Exception` 把完全不同的情况揉成了同一个 `[]`：文件不存在（正常，第一次玩）、JSON 坏了（数据出事了）、没有读权限（环境问题），甚至你自己代码里拼错变量名引起的 `NameError`。前几种调用方分不清，最后一种更糟：程序自己的 bug 被悄悄吞掉，不报错，只是结果不对。

记住：**只捕获你预料到、而且知道该怎么处理的异常。** 预料之外的，让它抛出来。

## 五、今天的作业

1. 补齐 `test_history.py`，覆盖第一节表里的六种场景。要求：用 `TemporaryDirectory()`；坏数据用 `write_text()` 造；每个场景都要有 `assert`；全部通过后打印 `所有测试通过！`。
2. 回答两个问题：
   - 为什么上面的 `except Exception: return []` 看着简单，却不适合企业项目？
   - 文件内容是 `["abc", 101]` 时，这个版本返回什么？为什么？

## 六、小测

**1.** 函数标注了 `-> list[int]`，实际 `return {"a": 1}`，会怎样？

- A. 函数返回时 Python 报 `TypeError`
- B. 正常返回字典，直到有人把它当列表用才出错
- C. 自动转成列表

**2.** 为什么构造「JSON 格式错误」的测试数据要用 `write_text("hello")`，而不是 `save_history()`？

- A. `write_text` 更快
- B. `save_history()` 写不出不合法的 JSON
- C. `save_history()` 会清空临时目录

**3.** `assert result == [10, 20, 30] == []` 在 `result` 是 `[]` 时结果是什么？

- A. 通过
- B. 失败
- C. 语法错误

<details>
<summary>答案</summary>

1. B。类型注解不做运行时检查。
2. B。它只会写出合法的 JSON，要测坏数据就得自己写。
3. B。这是链式比较，等于 `result == [10, 20, 30] and [10, 20, 30] == []`，后半截永远是 `False`。下面讲评里就是这一行。

</details>

## 讲评（10-26）

两道思考题你答得都在点上。第一题说「错误分类不明确，调用方不能根据异常做调整」，正是第一个危害。第二题你判断 `json.load` 不会报错、会正常返回，也对。被追问「拿到字典后 `append` 会怎样」时你答了「也能成功」，这里错了：字典没有 `append`，上面第三节就是实际结果。

作业第一次交的时候有两个小问题。

一是参数顺序。你写的是 `save_history(str(filename), [10, 20, 30])`，而昨天的定义是 `save_history(history, filename)`，文件名和列表传反了。后来你干脆把 `history.py` 的签名改成了 `save_history(filename, data)`，让文件名在前，这个顺序更顺手，只是要知道它和 Day 11 的版本不兼容了。

二是这一行：

```python
assert load_history(not_exist) == [10, 20, 30] == []
```

Python 把它当成链式比较，实测：

```python
result = []
print(result == [10, 20, 30] == [])
print(result == [10, 20, 30] and [10, 20, 30] == [])
```

```text
False
False
```

两种写法结果一样，后半截 `[10, 20, 30] == []` 永远不成立。`1 <= x <= 100` 是链式比较的好用法，用在 `==` 上几乎都是写错了。这里只要 `assert load_history(str(not_exist)) == []`。

剩下四个场景是你让 GPT 补的，六个场景最后都齐了，测试也全过。

### 回头再看：`open()` 少了 `encoding`

这一版 `history.py` 的读取写成了 `with open(filename) as f:`，`encoding="utf-8"` 丢了。当天 GPT 在审查里提了一句「读写编码保持一致」，但没说后果有多重。整理时实测了一下：用 UTF-8 写一个带中文的历史文件（模拟被人手改过），再用 Day 12 的 `load_history()` 读：

```text
UnicodeDecodeError: 'gbk' codec can't decode byte 0xad in position 4: illegal multibyte sequence
```

中文 Windows 默认按 GBK 读，读 UTF-8 的中文就出错。而这个函数只接了 `FileNotFoundError` 和 `JSONDecodeError`，`UnicodeDecodeError` 一路往上抛，程序直接崩溃。六个测试为什么都没发现？因为测试数据全是英文和数字，用哪种编码读都一样。Day 11 那版带着 `encoding="utf-8"`，同样的文件会正常走到校验，返回 `[]`。

> 注意：如果运行时设了环境变量 `PYTHONUTF8=1`（仓库 README 为了解决控制台乱码推荐过），默认编码会变成 UTF-8，这个 bug 就被盖住了，同样的文件读出来是 `[]`。所以别指望环境，`encoding="utf-8"` 读写两头都写上。

还有一处：文件最后一行直接写了 `test_history()`，没放进 `if __name__ == "__main__":`。别的文件一 `import` 它，测试就跑起来了，这是 Day 10 讲过的事。

## 加练

[不信任读进来的数据](加练/day12_不信任读进来的数据.md)：存档的结构更复杂（每局一条记录、有好几个字段），练逐层校验、`type` 和 `isinstance` 的取舍，以及校验失败时抛出自己的异常。
