---
kind: problem
outline: [2, 2]
time: 40 分钟
uses: [json.dumps 与 loads, ensure_ascii 和 indent, JSON 的键只能是字符串, utf-8-sig]
record:
  - text: Day11 JSON 四个方法
    link: https://github.com/syjlpineapple/ai-learning/blob/main/courseware/records/python/Day11.md
  - text: Day14 JSONDecodeError
    link: https://github.com/syjlpineapple/ai-learning/blob/main/courseware/records/python/Day14.md
---

# 第 2 题 · JSON 存档

第 1 题自己定的「名字,次数」格式，名字里一有逗号就得特殊处理，以后想多存一个字段也很麻烦。这题换成 JSON：每局游戏存一条完整记录，包括谁玩的、答案、猜过的数、赢没赢。

## 题目

打开 [`code/m04_persistence/p02_saves_exercise.py`](../../code/m04_persistence/p02_saves_exercise.py)，实现三个函数：

| 函数 | 做什么 |
|---|---|
| `save_games(path, games)` | 把 `{局号: 记录}` 写成 JSON，覆盖原文件 |
| `load_games(path)` | 读回 `{局号: 记录}`，文件不存在返回 `{}` |
| `add_game(path, player, game)` | 把一局 `GuessGame`（3.3 的 `rules.py`）追加进存档，返回新局号：已有最大局号加 1，空存档时是 1 |

一条记录长这样：

```json
{
  "1": {
    "player": "张三",
    "target": 42,
    "history": [50, 25, 42],
    "won": true
  }
}
```

**要求**

1. 文件能直接打开看懂：中文原样显示，有缩进
2. `load_games` 返回的局号是 `int`，和存进去的一样
3. 存档里已经有 1 到 9 局时，新的一局是 10，再下一局是 11
4. 记录里有存不进 JSON 的东西时，原存档不能被写坏
5. 能读开头带 BOM 的 UTF-8 文件；每一处打开文件都写 `encoding`

**验证**（在 `code/` 目录下）

```powershell
pytest tests/test_m04.py -k p02 -v
```

现在是 `10 passed, 8 skipped`，全部做完是 `18 passed`。

::: details 提示：要求 1，文件里是一串 \u5f20\u4e09
`json.dumps` 默认把非 ASCII 字符转义。有一个参数能关掉它，还有一个参数控制缩进。
:::

::: details 提示：要求 2，读回来的局号是 '1' 不是 1
JSON 对象的键只能是字符串，`json.dumps({1: "a"})` 会把 `1` 写成 `"1"`。读回来以后得自己转。
:::

::: details 提示：要求 4，测试说存档被写坏了
`json.dump(data, f)` 是一边转换一边往文件里写的。想想它在转换到一半的时候遇到一个 `set` 会怎样。第 1 题的办法这里同样适用。
:::

::: details 提示：要求 5，Unexpected UTF-8 BOM
有一种编码名字专门处理这件事：文件开头有 BOM 就跳过，没有也照常读。
:::

<Reveal>

## 讲评

### 参考答案

```python
def save_games(path: str | Path, games: dict[int, Record]) -> None:
    path = Path(path)
    text = json.dumps(games, ensure_ascii=False, indent=2)   # ① 先在内存里转换
    tmp = path.with_name(path.name + ".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(text)
    os.replace(tmp, path)


def load_games(path: str | Path) -> dict[int, Record]:
    path = Path(path)
    if not path.exists():
        return {}
    with open(path, encoding="utf-8-sig") as f:              # ② 有 BOM 就跳过
        raw = json.load(f)
    return {int(key): record for key, record in raw.items()} # ③ 键转回 int


def add_game(path: str | Path, player: str, game: GuessGame) -> int:
    games = load_games(path)
    game_id = max(games, default=0) + 1                      # ④ 空字典也不会报错
    games[game_id] = {
        "player": player,
        "target": game.target,
        "history": list(game.history),
        "won": game.won,
    }
    save_games(path, games)
    return game_id
```

④ 的 `default=0` 是第 1.9 章讲过的：`max([])` 会抛 `ValueError`，`max([], default=0)` 返回 `0`。

### 坑 1：JSON 的键只能是字符串

```text
json.loads(json.dumps({1: "a", 2: "b"}))       →  {'1': 'a', '2': 'b'}
往返之后 == 原来的字典                          →  False
json.dumps({True: 1, None: 2})                 →  '{"true": 1, "null": 2}'
json.dumps({(1, 2): "x"})                      →  TypeError: keys must be str, int, float, bool or None, not tuple
```

`int`、`float`、`bool`、`None` 作键时会被悄悄转成字符串，不报错。读回来不转的话，后面一连串问题：`games[1]` 报 `KeyError`，而且下面这个坑会让存档丢数据。

更隐蔽的一种：同时有 `1` 和 `"1"` 两个键时，写出的 JSON 里两个都在，读回来只剩一个。

```text
json.dumps({1: "a", "1": "b"})                 →  '{"1": "a", "1": "b"}'
json.loads('{"1": "a", "1": "b"}')             →  {'1': 'b'}
```

### 坑 2：字符串局号上取 max，第 10 局之后开始覆盖

用一份典型的初稿跑要求 3 的测试，它的写法是 `int(max(games)) + 1`，`games` 的键还是字符串：

```text
拿到的局号是 10 和 10。
```

存档里有 `"1"` 到 `"10"` 时，`max` 按**字典序**比较字符串（第 1.1 章的 `"9" > "10"`）：

```text
max(["9", "10", "2"])         →  '9'
max(map(int, ["9", "10"]))    →  10
```

于是第 11 局又被分到了局号 10，**把第 10 局覆盖掉了**。前 9 局一切正常，测试只测到 3 局的话根本发现不了。

### 坑 3：`json.dump` 写到一半出错，留下半截文件

```python
with open("games.json", "w", encoding="utf-8") as f:
    json.dump({"1": {"player": "李四"}, "2": {"tags": {1}}}, f, ensure_ascii=False)
```

```text
TypeError: Object of type set is not JSON serializable
文件里剩下：'{"1": {"player": "李四"}, "2": {"tags": '
再读它    ：JSONDecodeError: Expecting value: line 1 column 39 (char 38)
```

这比第 1 题的「文件被清空」更糟：清空了好歹 `load_games` 还能返回 `{}`，半截 JSON 连读都读不了，整个存档就废了。

学习记录 Day11、Day13、Day14 的 `save_history` 都是 `json.dump(data, f, ...)` 直接写原文件。当时存的是整数列表，不会遇到存不进去的类型，所以一直没出事。

### 坑 4：开头的 BOM

```text
json.loads("\ufeff{}")   →  JSONDecodeError: Unexpected UTF-8 BOM (decode using utf-8-sig)
```

BOM 是文件开头的三个字节 `EF BB BF`，用来标记「这是 UTF-8」。Python 的 `"utf-8"` 编码不会去掉它，`json` 看到它就报错。哪些程序会写出带 BOM 的文件？实测 Windows PowerShell 5.1 的 `Set-Content -Encoding UTF8` 就会：写出的前 3 个字节是 `b'\xef\xbb\xbf'`。用 `encoding="utf-8-sig"` 读，有 BOM 就跳过，没有也照常读。

报错信息很友好，直接告诉了你该用什么编码。

### 典型初稿会被哪些测试抓住

初稿的写法：`json.dump(games, f)` 直接写原文件、不写 `ensure_ascii`、读回来不转键、`int(max(games)) + 1`。

```text
FAILED test_p02_round_trip_keeps_int_keys    局号要是 int，读回来的是 ['1', '2']
FAILED test_p02_file_is_readable             文件里是 \u5f20\u4e09 这样的转义
FAILED test_p02_add_game                     读回来的键是字符串
FAILED test_p02_add_game_after_nine          拿到的局号是 10 和 10
FAILED test_p02_save_failure_keeps_old_file  存档被写坏了
FAILED test_p02_load_file_with_bom           Unexpected UTF-8 BOM
FAILED test_p02_encoding_is_explicit         （键是字符串，取 [1] 时 KeyError）
7 failed, 1 passed
```

## 复盘

::: tip 这题用到的
- **四个函数**：`dump`/`load` 对文件，`dumps`/`loads` 对字符串。要稳妥地写文件，先 `dumps` 成字符串，再写临时文件、替换
- **`ensure_ascii=False`** 中文原样写；**`indent=2`** 分行缩进。两个都只影响文件长什么样，不影响读回来的数据
- **类型不是一一对应的**：`tuple` 读回来是 `list`；`set` 存不进去；`True`/`None` 写成 `true`/`null`
- **对象的键只能是字符串**：`int` 键会被悄悄转成字符串，读回来要自己转。转之前别对它们取 `max` 或排序
- **`JSONDecodeError` 是 `ValueError` 的子类**（第 2.2 章），`except ValueError` 也会接住它
- **`encoding="utf-8-sig"`** 读文件时能容忍开头的 BOM
:::

现在 `load_games` 读到什么就返回什么。有人手动把 `"history": [50, 25]` 改成 `"history": "50, 25"`，或者把 `"won": true` 改成 `"won": 1`，程序要等到用这些数据时才会出错，而且出错的位置离原因很远。下一题处理这件事：**读进来的数据先校验，再使用。**

## 自测

1. `json.loads(json.dumps({1: "a", (1, 2): "b"}))` 会发生什么？
2. 存档里的局号是 `"1"` 到 `"10"` 的字符串时，`max(games)` 是多少？这会导致什么后果？
3. 为什么说 `json.dump(data, f)` 直接写原文件，比第 1 题的「`w` 模式清空文件」更危险？

<details>
<summary>参考答案</summary>

1. 报 `TypeError: keys must be str, int, float, bool or None, not tuple`，`dumps` 那一步就失败了。如果只有 `1` 这个键，不会报错，读回来是 `{'1': 'a'}`。
2. 是 `'9'`。字符串按字典序比较，`"9" > "10"`。新局号就成了 10，和已有的第 10 局重复，把它覆盖掉。
3. `json.dump` 是边转换边写的，转换到一半出错时，文件里留下的是半截 JSON，再读就是 `JSONDecodeError`，整个存档都读不出来；文件被清空的话，至少还能当作空存档继续用。

</details>

</Reveal>
