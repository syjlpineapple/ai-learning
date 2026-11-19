---
kind: problem
outline: [2, 2]
time: 45 分钟
uses: [bool 是 int 的子类, type 与 isinstance, 逐层校验, raise from]
record:
  - text: Day12 解析 ≠ 校验
    link: https://github.com/syjlpineapple/ai-learning/blob/main/courseware/records/python/Day12.md
  - text: Day14 | 的优先级
    link: https://github.com/syjlpineapple/ai-learning/blob/main/courseware/records/python/Day14.md
---

# 第 3 题 · 不信任读进来的数据

第 2 题的存档是一个普通的文本文件，谁都能用记事本打开改。`json.loads` 只管语法：`"won": 1`、`"history": "50, 42"` 都是合法的 JSON，它照单全收。这一题在读进来之后、用之前，把数据逐层检查一遍。

## 题目

打开 [`code/m04_persistence/p03_validate_exercise.py`](../../code/m04_persistence/p03_validate_exercise.py)，实现两个函数：

| 函数 | 做什么 |
|---|---|
| `parse_games(raw)` | 校验 `json.loads` 得到的对象。合法就返回 `{局号: 记录}`，不合法抛 `SaveFormatError` |
| `load_games(path)` | 读文件、解析 JSON、调 `parse_games`。文件不存在返回 `{}` |

`SaveFormatError` 已经定义好了，它继承 `ValueError`。

**要求**

1. **局号**只认 `"1"`、`"2"`、`"10"` 这种写法。`"01"`、`"0"`、全角的 `"１"` 都不合法
2. **每局记录**必须正好有 `player`、`target`、`history`、`won` 四个字段，少了不行，多了也不行
3. **字段的值**：
   - `player` 是非空字符串
   - `target` 是 1 到 100 的整数
   - `history` 是列表，里面每个都是 1 到 100 的整数
   - `won` 是 `true` 或 `false`
4. **字段之间对得上**：`won` 为真，当且仅当 `history` 最后一个数等于 `target`
5. **JSON 语法错误**也要变成 `SaveFormatError`，消息里写出文件名，并且保留原来的 `JSONDecodeError`

报错消息要能直接定位问题：写出第几局、哪个字段、实际的值。比如：

```text
第 2 局的 target：必须是 1-100 的整数，实际是 True
```

**验证**（在 `code/` 目录下）

```powershell
pytest tests/test_m04.py -k p03 -v
```

现在是 `30 passed, 24 skipped`，全部做完是 `54 passed`。

::: details 提示：要求 3，target 写成 true 却通过了
`isinstance(True, int)` 是什么？在 Python 交互模式里试一下。判断「是整数但不是布尔值」，有一种比 `isinstance` 更严格的写法。
:::

::: details 提示：要求 3，won 写成 1 却通过了
`1 in (True, False)` 的结果是什么？`in` 用 `==` 比较，而 `1 == True`。
:::

::: details 提示：要求 1，"01" 被当成了第 1 局
`int("01")` 是 1，`int("１")` 也是 1。把转换的结果再变回字符串，和原来的比一比。
:::

::: details 提示：要求 5，测试说原来的 JSONDecodeError 丢了
`raise 新异常 from e` 和 `from None` 的区别在第 2.2 章。另外检查一下你的 `try` 包住了几行。
:::

<Reveal>

## 讲评

### 参考答案

```python
def is_int(value: object) -> bool:
    return type(value) is int            # bool 是 int 的子类，必须排除


def is_game_id(key: object) -> bool:
    return (isinstance(key, str) and key.isascii() and key.isdecimal()
            and key == str(int(key)) and int(key) >= 1)


def parse_games(raw: object) -> dict[int, Record]:
    if not isinstance(raw, dict):
        raise SaveFormatError(f"存档最外层必须是对象，实际是 {type(raw).__name__}")
    games: dict[int, Record] = {}
    for key, record in raw.items():
        if not is_game_id(key):
            raise SaveFormatError(f"局号 {key!r} 不合法：必须是 1、2、3 这样的正整数")
        games[int(key)] = parse_record(key, record)
    return games


def load_games(path: str | Path) -> dict[int, Record]:
    path = Path(path)
    if not path.exists():
        return {}
    with open(path, encoding="utf-8-sig") as f:
        text = f.read()
    try:                                 # 只包住会抛 JSONDecodeError 的这一行
        raw = json.loads(text)
    except json.JSONDecodeError as e:
        raise SaveFormatError(f"{path.name} 不是合法的 JSON：{e}") from e
    return parse_games(raw)
```

`parse_record` 按「结构 → 字段类型 → 字段之间」的顺序检查一局记录，完整代码见 [`p03_validate_solution.py`](../../code/m04_persistence/p03_validate_solution.py)。它的骨架是：

```python
    if not isinstance(record, dict): ...           # 结构：是不是对象
    missing = [n for n in FIELDS if n not in record]
    extra = sorted(set(record) - set(FIELDS))      # 结构：字段齐不齐、有没有多余的
    if not (is_int(target) and LOW <= target <= HIGH): ...   # 类型和范围
    if type(won) is not bool: ...
    if won != (bool(history) and history[-1] == target): ... # 字段之间
```

### 坑 1：`bool` 是 `int` 的子类

```text
isinstance(True, int)     →  True
type(True) is int         →  False
1 <= True <= 100          →  True
isinstance(1, bool)       →  False
```

`"target": true` 用 `isinstance(target, int) and 1 <= target <= 100` 检查，两个条件都满足。这个存档读进来以后：

```text
GuessGame(True).guess(1)  →  '正确'
```

答案成了 1，猜 1 就算赢。mypy 也不会拦：`GuessGame` 的参数注解是 `int`，`bool` 是它的子类，类型上完全合法。

反方向没有这个问题：`isinstance(1, bool)` 是 `False`。所以检查 `won` 时用 `isinstance(won, bool)` 是对的，检查整数时才要用 `type(x) is int`。

### 坑 2：`won in (True, False)` 放过了 `1`

```text
1 in (True, False)        →  True
```

`in` 逐个用 `==` 比较，`1 == True` 成立。初稿用这种写法检查 `won`，`"won": 1` 顺利通过。

### 坑 3：`int()` 太宽容，不同的键变成同一局

```text
int("01"), int(" 1"), int("１")            →  (1, 1, 1)
{int(k): v for k, v in {"1": "a", "01": "b"}.items()}   →  {1: 'b'}
```

存档里同时有 `"1"` 和 `"01"` 的话，转成整数后后一个覆盖前一个，一局记录悄悄消失。参考答案用 `key == str(int(key))` 要求写法唯一；`isascii()` 排除全角数字，`"１".isdecimal()` 是 `True`，只靠它挡不住（第 1.2 章讲过 `isdigit` 和 `isdecimal` 的区别）。

### 坑 4：`try` 包大了，报错说的不是真正的原因

初稿的 `load_games`：

```python
try:
    with open(path, encoding="utf-8-sig") as f:
        return parse_games(json.load(f))
except ValueError:
    raise SaveFormatError(f"{path.name} 不是合法的 JSON") from None
```

拿一个 JSON 完全正确、只是 `target` 是 101 的存档去读：

```text
SaveFormatError : games.json 不是合法的 JSON
  __cause__   = None
  __context__ = SaveFormatError('第 1 局的 target 不合法：101')
```

两个问题叠在一起。`SaveFormatError` 也是 `ValueError`（`JSONDecodeError` 同样是），所以 `except ValueError` 把校验失败也接住了，改写成「不是合法的 JSON」。`from None` 又把真正的原因从报错输出里藏了起来。你会盯着一个格式完全正确的 JSON 文件找语法错误。

这就是第 1.5 章说的「`try` 包大了会伪装 bug」。参考答案只让 `try` 包住 `json.loads` 一行，只接 `JSONDecodeError`，用 `from e` 保留原因。

### 坑 5：Day14 那个 `|`

学习记录 Day14 的范围检查是这样写的：

```python
if 100 < item | item < 1:
    raise ValueError("数字范围要在1~100")
```

```text
  item   100 < item | item < 1    not 1 <= item <= 100
     0   False                    True
   101   False                    True
 10000   False                    True
```

`|` 是按位或，不是「或」，而且它的优先级比 `<` 高。这一行实际是 `100 < (item | item) < 1`，`item | item` 就是 `item`，于是变成「大于 100 且小于 1」，永远不成立，0 和 10000 都能通过。这一题的范围检查写 `LOW <= n <= HIGH`，一个比较链，不会有优先级问题。

同一条规则还有一个变体：想写「是 int 但不是 bool」，写成 `type(x) is not int | bool`，实测对 `1`、`True`、`"x"`、`None` 都是 `True`。它被解析成 `type(x) is not (int | bool)`，任何值的类型都不会「是」`int | bool` 这个联合对象本身。要排除 bool，写 `type(x) is int`。

### 典型初稿会被哪些测试抓住

初稿用 `isinstance(x, int)`、`won in (True, False)`、`int(key)`，不检查多余字段和字段之间的关系，`try` 包住整段：

```text
FAILED rejects_bad_save[key_leading_zero]      "01" 被当成第 1 局
FAILED rejects_bad_save[key_zero]
FAILED rejects_bad_save[key_fullwidth]
FAILED rejects_bad_save[typo_field]            多了一个 histroy 没发现
FAILED rejects_bad_save[target_true]           坑 1
FAILED rejects_bad_save[history_bool]          坑 1
FAILED rejects_bad_save[won_one]               坑 2
FAILED rejects_bad_save[won_wrong]             won 和 history 对不上
FAILED load_bad_json                           原来的 JSONDecodeError 丢了
FAILED load_validates                          坑 2
10 failed, 15 passed
```

## 复盘

::: tip 这题用到的
- **解析不等于校验**：`json.loads` 只保证语法正确，类型、范围、字段齐不齐都要自己检查（Day12 的结论）
- **逐层检查**：最外层结构 → 每局的字段齐不齐 → 每个字段的类型和范围 → 字段之间是否一致。外层不对就不要往里看
- **`bool` 是 `int` 的子类**：要整数时用 `type(x) is int`；要布尔值时 `isinstance(x, bool)` 就够了
- **`in` 用 `==` 比较**，`1 in (True, False)` 是 `True`
- **`int()` 能转的写法很多**，键这类要求唯一写法的地方，转完再变回字符串比一比
- **报错消息写清楚第几局、哪个字段、实际值**（`!r` 能区分 `1` 和 `True`、`"1"` 和 `1`）
- **`try` 只包会出那种错的那一行**，转换异常用 `from e`
:::

这一题里出了问题就抛异常。可是程序该怎么让人知道「存档坏了」？现在只能靠异常一路抛到最外面，打印一大段 traceback。下一题用 `logging` 代替 `print`，把「读了哪个文件、跳过了哪一局、为什么」记下来。

## 自测

1. `isinstance(True, int)`、`type(True) is int`、`isinstance(1, bool)` 分别是什么？检查「整数」和检查「布尔值」时各该用哪种写法？
2. 一个 JSON 语法完全正确的存档，为什么初稿的 `load_games` 会报「不是合法的 JSON」？要改哪两处？
3. Day14 的 `if 100 < item | item < 1:` 为什么拦不住 0 和 10000？

<details>
<summary>参考答案</summary>

1. 分别是 `True`、`False`、`False`。`bool` 是 `int` 的子类，所以检查整数要用 `type(x) is int` 排除布尔值；反过来整数不是 `bool`，检查布尔值用 `isinstance(x, bool)` 就行。
2. `SaveFormatError` 和 `JSONDecodeError` 都是 `ValueError` 的子类。`try` 包住了 `parse_games`，`except ValueError` 把校验失败也接住，改写成「不是合法的 JSON」；`from None` 又把真正的原因藏了起来。改法：`try` 只包住 `json.loads`、只接 `json.JSONDecodeError`；用 `from e` 代替 `from None`。
3. `|` 是按位或，优先级比 `<` 高，这一行实际是 `100 < (item | item) < 1`。`item | item` 等于 `item`，条件变成「大于 100 且小于 1」，对任何数都不成立。应该写 `not 1 <= item <= 100`。

</details>

</Reveal>
