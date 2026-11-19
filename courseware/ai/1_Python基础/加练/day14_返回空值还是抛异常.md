---
kind: problem
outline: [2, 2]
time: 40 分钟
uses: [返回值的语义歧义, 结果对象, EAFP, None 与哨兵值]
record:
  - text: Day13 三种错误处理设计
    link: https://github.com/syjlpineapple/ai-learning/blob/main/courseware/records/python/Day13.md
  - text: Day14 错误语义落地
    link: https://github.com/syjlpineapple/ai-learning/blob/main/courseware/records/python/Day14.md
---

# 第 5 题 · 该返回空值还是抛异常

第 4 题的 `load_games_lenient` 返回 `{}` 时，调用方分不清是哪种情况：

| 实际情况 | `load_games_lenient` 返回 |
|---|---|
| 还没有存档文件 | `{}` |
| 存档文件存在，里面一局都没有 | `{}` |
| 存档里的局全都坏了，都被跳过 | `{}` |

前两种可以放心开新游戏，第三种该提醒玩家「你的存档坏了」，而不是若无其事地从第 1 局开始，再在下次保存时把坏存档覆盖掉。Day13 当时就发现了这个问题，叫它「返回值的语义歧义」。

这一题让读取函数返回一个结果对象，把这几种情况分开，再在它上面写两个统计函数，练习「没有结果」该怎么表示。

## 题目

打开 [`code/m04_persistence/p05_result_exercise.py`](../../code/m04_persistence/p05_result_exercise.py)。`LoadResult` 已经定义好了：

```python
@dataclass(frozen=True)
class LoadResult:
    games: dict[int, Record] = field(default_factory=dict)
    skipped: dict[str, str] = field(default_factory=dict)   # 局号 → 为什么跳过
    found: bool = False                                     # 存档文件是否存在
```

实现四个函数：

| 函数 | 做什么 |
|---|---|
| `load_save(path)` | 读存档，返回 `LoadResult` |
| `describe(result)` | 给玩家看的一句话 |
| `best_attempts(result, player)` | 这个玩家赢的局里最少用了几次 |
| `leaderboard(result)` | 每个玩家一行 `(名字, 最好成绩)` |

**要求**

1. `load_save`：文件不存在返回 `LoadResult(found=False)`；整个文件坏了抛 `SaveFormatError`；坏的局跳过，原因记进 `skipped`。**其他读不了的情况（比如路径是一个目录）不要处理**，让异常原样抛出
2. `describe` 五种情况，返回值分别是：

   | 情况 | 返回 |
   |---|---|
   | 没有存档文件 | `还没有存档，从第 1 局开始` |
   | 存档里一局都没有 | `存档是空的` |
   | 全都读到了 | `读到 4 局` |
   | 跳过了一部分 | `读到 2 局，跳过 2 局（01、2）` |
   | 全都坏了 | `存档里的 2 局全都坏了（1、x），没有读到任何一局` |

3. `best_attempts`：没赢过（包括没玩过）返回 `None`
4. `leaderboard`：成绩好的在前，没赢过的排在最后，成绩相同按名字排

**验证**（在 `code/` 目录下）

```powershell
pytest tests/test_m04.py -k p05 -v
```

现在是 `17 passed, 13 skipped`，全部做完是 `30 passed`。

::: details 提示：要求 1，路径是目录时测试说返回了 found=False
`Path("某个目录").exists()` 是 `True`；接着 `open` 它会抛什么异常？你的 `except` 接住的是不是太宽了？只有一种异常才真正表示「还没有存档」。
:::

::: details 提示：要求 2，「存档是空的」和「全都坏了」都变成了「还没有存档」
你是不是只看了 `result.games` 空不空？`LoadResult` 里另外两个字段就是为了区分这几种情况才有的。
:::

::: details 提示：要求 4，None 没法排序
`None < 2` 会报 `TypeError`。排序的 `key` 可以返回一个元组：第一个元素先把「没赢过」和「赢过」分开。
:::

<Reveal>

## 讲评

### 参考答案

```python
def load_save(path: str | Path) -> LoadResult:
    path = Path(path)
    try:
        with open(path, encoding="utf-8-sig") as f:
            text = f.read()
    except FileNotFoundError:                        # 只有这一种算「没有存档」
        return LoadResult(found=False)

    try:
        raw = json.loads(text)
    except json.JSONDecodeError as e:
        raise SaveFormatError(f"{path.name} 不是合法的 JSON：{e}") from e
    if not isinstance(raw, dict):
        raise SaveFormatError(f"存档最外层必须是对象，实际是 {type(raw).__name__}")

    games: dict[int, Record] = {}
    skipped: dict[str, str] = {}
    for key, record in raw.items():
        if not is_game_id(key):
            skipped[key] = "局号必须是 1、2、3 这样的正整数"
            continue
        try:
            games[int(key)] = parse_record(key, record)
        except SaveFormatError as e:
            skipped[key] = str(e)
    return LoadResult(games=games, skipped=skipped, found=True)


def describe(result: LoadResult) -> str:
    if not result.found:
        return "还没有存档，从第 1 局开始"
    bad = "、".join(result.skipped)
    if not result.games and not result.skipped:
        return "存档是空的"
    if not result.games:
        return f"存档里的 {len(result.skipped)} 局全都坏了（{bad}），没有读到任何一局"
    if not result.skipped:
        return f"读到 {len(result.games)} 局"
    return f"读到 {len(result.games)} 局，跳过 {len(result.skipped)} 局（{bad}）"


def leaderboard(result: LoadResult) -> list[tuple[str, int | None]]:
    players = {str(g["player"]) for g in result.games.values()}
    board = [(p, best_attempts(result, p)) for p in players]
    return sorted(board, key=lambda row: (row[1] is None, row[1] or 0, row[0]))
```

`best_attempts` 的核心是最后一行 `return min(wins, default=None)`，完整代码见 [`p05_result_solution.py`](../../code/m04_persistence/p05_result_solution.py)。

### 坑 1：`exists()` 之后再 `open`，加上 `except OSError`

典型初稿是这样读文件的：

```python
if not path.exists():
    return LoadResult()
try:
    with open(path, encoding="utf-8-sig") as f:
        raw = json.load(f)
except OSError:
    return LoadResult()
```

路径是一个目录时（比如有人手滑建了一个叫 `games.json` 的文件夹），实测：

```text
exists()   →  True
is_file()  →  False
open()     →  PermissionError: [Errno 13] Permission denied: '...\games.json'
```

`exists()` 放行了，`open` 抛 `PermissionError`（Windows 上是这个；Linux 和 macOS 上是 `IsADirectoryError`，本机没有实测），它是 `OSError` 的子类，被 `except OSError` 接住，最后返回「还没有存档」。程序开开心心地开了新游戏，直到保存时才在另一个地方报错。

参考答案的写法是第 1.5 章的 EAFP：直接打开，只接住 `FileNotFoundError` 这一种。`exists()` 那一行可以删掉，它并不能保证接下来 `open` 一定成功。

### 坑 2：dataclass 对象永远是「真」

以前 `load_games` 返回字典时，调用方可能这样写：

```python
games = load_games(path)
if not games:
    print("还没有存档")
```

改成返回 `LoadResult` 以后，这行判断还能跑，但意思全变了：

```text
bool({})              →  False
bool(LoadResult())    →  True
```

dataclass 没有定义 `__bool__` 和 `__len__`，Python 把所有对象都当成真。`if not result:` 永远不成立，「还没有存档」这条提示再也不会出现，而且没有任何报错。**改函数的返回类型时，要把所有调用方都检查一遍**，尤其是那些拿返回值做真假判断的地方。mypy 会报出还把结果当字典用的地方（比如 `games.items()`），但 `if not result:` 在类型上完全合法，它不会提示。

另外两种常见的改法也会撞上类似的问题：

```text
返回 None 表示失败，调用方照旧 len(...)       →  TypeError: object of type 'NoneType' has no len()
改成返回 (games, error)，调用方忘了解包，len(...)  →  2（元组的长度），不报错
```

第一种至少会报错，只是报错的地方离原因很远。第二种最糟，算出一个错误的结果，程序接着往下跑。

### 坑 3：用 0 表示「没赢过」

初稿的 `best_attempts` 没赢过就返回 `0`，排行榜实测：

```text
[('王五', 0), ('张三', 2), ('李四', 2)]
```

一局没赢的王五排到了第一。`0` 次猜中是不可能的成绩，但它是一个合法的整数，参与排序、比较、求最小值时不会有任何提示。这种「用一个特殊的值表示没有结果」的做法叫**哨兵值**，`-1`、`0`、`""` 都是常见的哨兵。

`None` 就不一样：

```text
sorted({"张三": 3, "李四": None}, key=...)   →  TypeError: '<' not supported between instances of 'NoneType' and 'int'
```

它没法和数字比较，忘了处理就会立刻报错。这正是要用 `None` 的原因：它逼着调用方正视「没有结果」这种情况。类型注解 `int | None` 也把这件事写在了函数签名上，mypy 会检查调用方有没有处理 `None`。

`min(wins, default=None)` 一行就完成了：`wins` 为空时返回 `None`，不为空时返回最小值。第 1.9 章讲过，`min([])` 会抛 `ValueError`。

### 怎么选：返回值还是异常

| 情况 | 是不是「正常会发生的」 | 怎么表示 |
|---|---|---|
| 还没有存档 | 是，首次运行一定会遇到 | 返回值：`found=False` |
| 有几局坏了 | 是，存档能被手动编辑 | 返回值：`skipped` 里列出来 |
| 玩家没赢过 | 是 | 返回值：`None` |
| JSON 语法错误 | 不是，整个存档都没法用 | 抛 `SaveFormatError` |
| 路径是目录、没有权限 | 不是，而且这个函数也处理不了 | 不处理，异常原样往上抛 |

判断的依据是：**调用方是不是本来就该为这种情况准备一条分支。** 是的话，用返回值把它表示清楚（而且要和其他情况区分开）；不是的话，抛异常，让调用方没法装作没看见。Day13 当时的结论「文件不存在返回空、JSON 损坏抛异常」就是这条规则，这一题把它推到了「部分损坏」和「没有成绩」。

### 典型初稿会被哪些测试抓住

初稿：`exists()` 加 `except OSError`、`describe` 只看 `games` 空不空、没赢过返回 `0`：

```text
FAILED test_p05_unreadable_is_not_missing   路径是个目录，却返回了 LoadResult(... found=False)
FAILED test_p05_describe[empty]             '还没有存档，从第 1 局开始' == '存档是空的'
FAILED test_p05_describe[all_bad]           '还没有存档，从第 1 局开始' == '存档里的 2 局全都坏了...'
FAILED test_p05_best_attempts               没赢过要返回 None，不是 0
FAILED test_p05_leaderboard                 [('王五', 0), ('张三', 2), ('李四', 2)]
5 failed, 8 passed
```

## 复盘

::: tip 这题用到的
- **一个返回值只表示一种意思**。会混淆的几种情况，用结果对象（这里是 `LoadResult`）把它们分开
- **预期会发生的情况用返回值，不该发生的情况抛异常**；自己处理不了的异常，不要接
- **EAFP**：直接 `open`，只接 `FileNotFoundError`。`exists()` 不能保证接下来能打开
- **`except OSError` 太宽**：权限错误、路径是目录都会被说成「文件不存在」
- **「没有结果」用 `None`，不用 `0`、`-1` 这类哨兵值**。`None` 参与比较会立刻报错，`int | None` 把这件事写进了签名
- **`min(xs, default=None)`**、排序键用元组 `(x is None, x or 0, name)` 把 `None` 排到最后
- **改返回类型要检查所有调用方**：dataclass 对象永远为真，`if not result:` 会悄悄失效
:::

M4 到这里就结束了。猜数字的存档从一个文本文件，变成了带校验、带日志、能说清楚每种失败的 JSON 存档。下一个模块 M5 开始调用网络 API：它会遇到的失败比读文件多得多，比如超时、连不上、服务端出错、返回的不是 JSON，这一题的思路会反复用到。

## 自测

1. 为什么用 `exists()` 判断之后再 `open`，还要再加 `except FileNotFoundError` 之外的处理？参考答案为什么干脆不用 `exists()`？
2. `load_games` 从返回字典改成返回 `LoadResult` 以后，调用方原来的 `if not games: print("还没有存档")` 会怎样？
3. `best_attempts` 没赢过时返回 `0` 和返回 `None`，各会让排行榜出现什么结果？

<details>
<summary>参考答案</summary>

1. `exists()` 只说明这个路径存在，不说明它是文件、也不说明有权限读。路径是目录时 `exists()` 是 `True`，`open` 照样抛 `PermissionError`（Windows）。而且检查和打开之间文件也可能被删掉。所以直接打开、只接住 `FileNotFoundError` 更简单也更准确，`exists()` 那一步是多余的。
2. 不报错，但判断永远不成立。dataclass 没有 `__bool__` 和 `__len__`，对象永远为真，所以「还没有存档」再也不会打印。要改成 `if not result.found:`。
3. 返回 `0`：没赢过的玩家成绩是 0，排在最前面（实测王五排第一），而且没有任何提示。返回 `None`：直接拿去排序会抛 `TypeError`，逼着你在排序键里专门处理它，把没赢过的人排到最后。

</details>

</Reveal>
