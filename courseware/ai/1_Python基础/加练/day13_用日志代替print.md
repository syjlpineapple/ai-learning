---
kind: problem
outline: [2, 2]
time: 45 分钟
uses: [getLogger(__name__), 模块记录、入口配置, "%s 参数", basicConfig 的 force, FileHandler 的 encoding]
record:
  - text: Day13 日志
    link: https://github.com/syjlpineapple/ai-learning/blob/main/courseware/records/python/Day13.md
---

# 第 4 题 · 用日志代替 print

第 3 题的 `load_games` 很严格：100 局里有 1 局被改坏，整个存档就读不出来了。玩家更希望的是坏的那一局丢掉、其他照常能用，但同时得留下记录：跳过了哪一局、为什么。

这种「给排查问题的人看」的信息不该 `print`。这一题写一个宽容的读取函数，用 `logging` 记下过程，再在入口处配置日志往哪里输出。

## 题目

两个文件：

| 文件 | 写什么 |
|---|---|
| [`p04_load_exercise.py`](../../code/m04_persistence/p04_load_exercise.py) | 业务模块：`load_games_lenient(path)`，**只记录日志** |
| [`p04_entry_exercise.py`](../../code/m04_persistence/p04_entry_exercise.py) | 入口：`setup_logging(level, logfile)`，**只配置日志** |

校验规则直接用第 3 题参考答案里的 `is_game_id` 和 `parse_record`，已经导入好了。

**要求**

1. 业务模块里创建一个模块级的 `logger`，名字是模块的完整路径。模块里不能出现 `print`、`basicConfig`、`addHandler`、`setLevel`
2. 坏的局跳过，每跳过一局记一条 `WARNING`，写出局号和原因
3. 记日志时，变量通过参数交给 `logging`，不要先用 f-string 拼好
4. 读完记一条 `INFO` 汇总：`读取 games.json：2 局，跳过 2 局`；文件不存在时只记一条 `INFO`。整个文件坏了（JSON 语法错误、最外层不是对象）照样抛 `SaveFormatError`
5. `setup_logging(level, logfile=None)`：输出到标准错误，格式用文件里给的 `CONSOLE_FORMAT`；`logfile` 不为空时同时写进这个文件（UTF-8，格式 `FILE_FORMAT`）；**调两次时第二次的级别生效，每条日志也只出现一次**

**验证**（在 `code/` 目录下）

```powershell
pytest tests/test_m04.py -k p04 -v
```

现在是 `21 passed, 11 skipped`，全部做完是 `32 passed`。

做完可以跑一下参考答案的入口，看看日志长什么样：

```powershell
python -m m04_persistence.p04_entry_solution 你的存档.json DEBUG
```

::: details 提示：要求 3，测试说日志是先拼好再传进去的
`logger.warning(f"跳过第 {key} 局")` 和 `logger.warning("跳过第 %s 局", key)`，前者传进去的是一个已经拼好的字符串，后者把模板和参数分开交给 `logging`。测试检查的是日志记录的 `args` 是不是空的。
:::

::: details 提示：要求 5，第二次 setup_logging 不生效
`logging.basicConfig` 只在根 logger 还没有 handler 时才做事，第二次调用会静默地什么都不做。它有一个参数专门解决这件事。
:::

::: details 提示：要求 5，同一条日志出现了两次
每次调用都往根 logger 上 `addHandler`，调两次就有两个 handler，每条日志都会被两个 handler 各输出一遍。
:::

<Reveal>

## 讲评

### 参考答案

业务模块：

```python
logger = logging.getLogger(__name__)


def load_games_lenient(path: str | Path) -> dict[int, Record]:
    path = Path(path)
    if not path.exists():
        logger.info("存档 %s 不存在，从空存档开始", path.name)
        return {}
    with open(path, encoding="utf-8-sig") as f:
        text = f.read()
    try:
        raw = json.loads(text)
    except json.JSONDecodeError as e:
        raise SaveFormatError(f"{path.name} 不是合法的 JSON：{e}") from e
    if not isinstance(raw, dict):
        raise SaveFormatError(f"存档最外层必须是对象，实际是 {type(raw).__name__}")

    games: dict[int, Record] = {}
    skipped = 0
    for key, record in raw.items():
        if not is_game_id(key):
            logger.warning("跳过局号 %r：必须是 1、2、3 这样的正整数", key)
            skipped += 1
            continue
        try:
            games[int(key)] = parse_record(key, record)
        except SaveFormatError as e:
            logger.warning("跳过第 %s 局：%s", key, e)
            skipped += 1

    logger.info("读取 %s：%d 局，跳过 %d 局", path.name, len(games), skipped)
    return games
```

入口：

```python
def setup_logging(level: str = "INFO", logfile: str | Path | None = None) -> None:
    console = logging.StreamHandler(sys.stderr)
    console.setFormatter(logging.Formatter(CONSOLE_FORMAT))
    handlers: list[logging.Handler] = [console]
    if logfile is not None:
        file_handler = logging.FileHandler(logfile, encoding="utf-8")
        file_handler.setFormatter(logging.Formatter(FILE_FORMAT))
        handlers.append(file_handler)
    logging.basicConfig(level=level, handlers=handlers, force=True)
```

JSON 语法错误的分支只抛异常、不记日志。调用方接住以后会记（参考答案的 `main` 里用了 `log.exception`），这里再记一遍，同一个错误就出现两条。

### 坑 1：`basicConfig` 第二次调用什么都不做

```python
logging.basicConfig(level=logging.WARNING, format="第一次 %(message)s")
logging.basicConfig(level=logging.DEBUG,   format="第二次 %(message)s")
log.info("info")
log.warning("warning")
logging.basicConfig(level=logging.DEBUG, format="force %(message)s", force=True)
log.info("之后")
```

```text
第一次 warning
force 之后
```

第二次调用没有报错，也没有生效：级别还是 WARNING，格式还是「第一次」。`basicConfig` 的规则是「根 logger 已经有 handler 就直接返回」。`force=True`（Python 3.8+）会先关掉、移除已有的 handler，再按这次的参数配置。

同一个原因让它**在 pytest 里也是无效的**。pytest 运行时已经往根 logger 上装了自己的 handler（实测有 4 个：`_LiveLoggingNullHandler`、`_FileHandler` 和两个 `LogCaptureHandler`），你在测试或被测模块里写的 `basicConfig(level=INFO)` 一行都不起作用。所以测试里看日志要用 `caplog`，不要靠 `basicConfig`。

### 坑 2：自己 `addHandler`，调两次就输出两遍

```python
for _ in range(2):
    logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))
logging.getLogger().setLevel(logging.INFO)
logging.getLogger("x").info("读取存档")
```

```text
读取存档
读取存档
```

一条日志会交给根 logger 上的每一个 handler。典型初稿的 `setup_logging` 每次调用都 `addHandler`，测试调两次就出现了重复。程序里如果有两个地方都「顺手配置一下日志」，日志就会成对出现。

### 坑 3：参数个数写错，不报错，只打一段 Logging error

```python
logger.warning("第 %s 局：%s", 3)        # 两个 %s，只给了一个参数
print("程序还在跑")
```

```text
--- Logging error ---
Traceback (most recent call last):
  ...
TypeError: not enough arguments for format string
Call stack:
  File "<string>", line 4, in <module>
Message: '第 %s 局：%s'
Arguments: (3,)
程序还在跑
```

`logging` 故意不让格式化错误抛出来：日志写错了，不该让业务崩掉。代价是这条日志丢了，而且只在真的输出时才会发现。级别被过滤掉的那些，写错了也看不到任何提示。

### 坑 4：f-string 在过滤之前就已经求值了

```python
log.setLevel(logging.WARNING)
log.debug(f"调试 {e}")     # e.__str__ 被调用了 1 次
log.debug("调试 %s", e)    # 还是 1 次，没有再调用
```

f-string 是在调用 `debug` 之前、Python 计算参数的时候就拼好的，`debug` 拿到的已经是成品，这条日志会不会被输出都一样。`%s` 的写法把模板和参数分开交给 `logging`，被过滤掉的日志根本不会去格式化。Day13 讲过这一点，这里是实测。

参数分开传还有一个好处：日志记录里保留着原始的参数（`record.args`），日志收集系统可以按「同一个模板」把消息归类。要求 3 的测试检查的就是 `args` 是否为空。

### 坑 5：`FileHandler` 也要写 encoding

```text
logging.FileHandler("a.log")        →  EncodingWarning: 'encoding' argument not specified
不写 encoding、关掉 UTF-8 模式写「欧阳修文」  →  文件里是 GBK 字节 b'\xc5\xb7\xd1\xf4...'
```

第 1 题的结论在这里同样成立。`logging.basicConfig(filename=...)` 也一样，它内部创建的就是 `FileHandler`，同样有 `encoding` 参数。

### 坑 6：`logger.exception` 要写在 `except` 里

```python
logging.getLogger("x").exception("出错了")    # 不在 except 块里
```

```text
ERROR 出错了
NoneType: None
```

`exception` 等于 `error` 加上「当前正在处理的异常」的 traceback。不在 `except` 里时没有当前异常，于是多了一行莫名其妙的 `NoneType: None`。

### 典型初稿会被哪些测试抓住

初稿：`getLogger("history")` 写死名字、模块顶层 `basicConfig`、局号不对时 `print`、日志全用 f-string；`setup_logging` 每次都 `addHandler`，`FileHandler` 不写 encoding。

```text
FAILED test_p04_module_logger                现在的名字是 'history'
FAILED test_p04_module_does_not_configure_or_print   出现了 ['basicConfig', 'print']
FAILED test_p04_skips_bad_games              跳过了 2 局，应该有 2 条 WARNING，实际 1 条
FAILED test_p04_uses_lazy_args               没有找到 logger 'm04_persistence.p04_load_exercise' 记的日志
FAILED test_p04_summary                      实际的 INFO：[]
FAILED test_p04_missing_file
FAILED test_p04_whole_file_bad_still_raises  （两条）抛的是 JSONDecodeError 和
                                             AttributeError: 'list' object has no attribute 'items'
FAILED test_p04_no_print                     标准输出里出现了 '局号不对：01\n'
FAILED test_p04_setup_twice                  同一条日志出现了多次
FAILED test_p04_setup_logfile                FileHandler 没写 encoding
11 failed, 1 passed
```

注意 `test_p04_summary` 里的 `实际的 INFO：[]`。初稿明明在模块顶层写了 `basicConfig(level=logging.INFO)`，INFO 却一条都没有。在 pytest 里实测，根 logger 的级别是 `WARNING`，`"history"` 这个 logger 的有效级别也是 `WARNING`。两个原因叠在一起：模块被导入时 pytest 已经在根 logger 上装了 handler，那行 `basicConfig` 不起作用（坑 1）；测试只把 `m04_persistence.p04_load_exercise` 这个 logger 调到了 DEBUG，名字写死成 `"history"` 的 logger 不受影响。

## 复盘

::: tip 这题用到的
- **`logger = logging.getLogger(__name__)`** 写在模块顶层。名字带着包的层级，入口可以按包、按模块分别调级别
- **模块记录，入口配置**：业务模块只调 `logger.info/warning/...`；级别、格式、输出目标只在入口配置一次
- **`basicConfig` 只在第一次生效**，重新配置要 `force=True`；在 pytest 里它不起作用，看日志用 `caplog`
- **一个 handler 输出一遍**：重复 `addHandler` 会让日志重复
- **参数交给 logging**：`logger.warning("跳过第 %s 局：%s", key, e)`。被过滤时不格式化；参数个数写错不会崩，但这条日志会丢
- **`FileHandler(..., encoding="utf-8")`**
- **`logger.exception` 只在 `except` 里用**，它会带上 traceback
- **给人看的结果用 `print`，排查用的过程用日志**；日志输出到标准错误，不和程序的结果混在一起
:::

现在存档有三种「读取失败」：文件不存在返回 `{}`、某一局坏了跳过、整个文件坏了抛异常。调用方能分清这三种情况吗？如果 `load_games_lenient` 返回了 `{}`，是没有存档，还是所有局都坏了？下一题专门讨论：什么时候该返回空值，什么时候该抛异常。

## 自测

1. 程序里两个地方各调了一次 `logging.basicConfig(level=...)`，最终是哪个级别？想让第二次生效要怎么写？
2. `logger.warning(f"跳过第 {key} 局")` 和 `logger.warning("跳过第 %s 局", key)` 有哪两点不同？
3. 被测模块顶层写了 `basicConfig(level=logging.INFO)`，为什么 pytest 里还是看不到它的 INFO 日志？测试里该怎么拿到日志？

<details>
<summary>参考答案</summary>

1. 第一次调用的级别。`basicConfig` 发现根 logger 已经有 handler，就静默地什么都不做。要让第二次生效，传 `force=True`。
2. 一是 f-string 在调用前就拼好了，哪怕这条日志被级别过滤掉也会求值；`%s` 的写法被过滤时不会格式化。二是后者在日志记录里保留了模板和参数（`record.args`），日志系统能按模板归类，测试也能检查参数。
3. pytest 运行时已经往根 logger 上装了自己的 handler，`basicConfig` 发现已经有 handler，什么都不做；根 logger 还是默认的 WARNING 级别。测试里用 `caplog` fixture，并用 `caplog.set_level(logging.DEBUG, logger="模块名")` 把要看的 logger 调低。

</details>

</Reveal>
