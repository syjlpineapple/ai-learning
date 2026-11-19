---
kind: lesson
outline: [2, 2]
time: 45 分钟
uses: [嵌套模型, model_validate_json, field_validator, TypeAdapter, ValidationError 的位置信息]
---

# Day 24：pydantic 进阶，重写 Day 14 的读历史记录

先翻出你 Day 14 写的 `load_history`，数一数里面有几个 `if`：

```python
if type(data) != list:
    raise ValueError("类型错误")
for item in data:
    if type(item) != int:
        raise ValueError("元素类型错误")
    if 100 < item or item < 1:
        raise ValueError("元素需要是1~100的整数")
```

三个检查，还都是你一个一个想出来的。如果文件里第 37 个数写错了，报错只会说「元素需要是1~100的整数」，你得自己去找是哪一个。

今天用昨天学的 pydantic 把这件事重做一遍。你会看到两点不同：**检查规则少写很多，报错能精确到「第几个」。**

## 一、数据里套着数据：嵌套模型（约 10 分钟）

真实的数据很少是平的。比如排行榜，每一局有玩家和次数，一个排行榜有很多局：

```json
{"games": [{"player": "张三", "attempts": 5}, {"player": "李四", "attempts": 3}]}
```

用 pydantic 描述它，就是两个模型，一个装在另一个里面：

```python
from pydantic import BaseModel, Field


class Game(BaseModel):
    player: str
    attempts: int = Field(ge=1, le=100, strict=True)


class Leaderboard(BaseModel):
    games: list[Game]        # 一个列表，里面每一项都是 Game
```

就这么多。`list[Game]` 的意思是「一个列表，里面的每一项都要按 `Game` 的规则检查」。

```python
board = Leaderboard(games=[{"player": "张三", "attempts": 5}, {"player": "李四", "attempts": 3}])
print(board.games[1].player)
```

```text
李四
```

注意你传进去的是普通的字典，但 `board.games[1]` 拿出来的已经是 `Game` 对象了，可以直接用 `.player`。pydantic 一边检查一边帮你转好了。

现在故意把李四的次数写成 300：

```text
1 validation error for Leaderboard
games.1.attempts
  Input should be less than or equal to 100 [type=less_than_equal, input_value=300, input_type=int]
```

看第二行 `games.1.attempts`：**`games` 列表里下标为 1 的那一项，它的 `attempts` 字段。** 这就是开头说的「精确到第几个」。数据再深，它都能一路指过去。

## 二、直接从 JSON 读（约 10 分钟）

Day 14 读文件是两步：先 `json.load` 变成 Python 对象，再一项一项检查。pydantic 可以一步做完：

```python
text = '{"games": [{"player": "张三", "attempts": 5}]}'
board = Leaderboard.model_validate_json(text)
```

我拿三种坏数据试了一下，结果很有意思：

| 坏在哪 | 报的错 | 位置 |
|---|---|---|
| JSON 本身不完整，少了结尾的 `]}` | `ValidationError`，类型 `json_invalid` | 整体 |
| 根本不是排行榜，是 `[1, 2, 3]` | `ValidationError`，类型 `model_type` | 整体 |
| 次数写成了 `true` | `ValidationError`，类型 `int_type` | `games.0.attempts` |

三种情况，**抛的都是同一种异常 `ValidationError`**。连 JSON 格式坏了也是它，不是 Day 14 里 `json.load` 会抛的那个 `json.JSONDecodeError`。

这对写 `except` 很友好：只用接一种异常。但也要小心一件事，`ValidationError` 是 `ValueError` 的子类，还记得 Day 15-16 那个 `except` 顺序的坑吗？如果你同时接这两个，`ValidationError` 要写在前面。

反过来，把模型写回 JSON 也是一行：

```python
print(board.model_dump_json(indent=2))
```

```text
{
  "games": [
    {
      "player": "张三",
      "attempts": 5
    }
  ]
}
```

中文原样输出，不会变成 `\u5f20\u4e09`，不用再记着加 `ensure_ascii=False` 了。

## 三、自己定规则：`field_validator`（约 10 分钟）

`Field` 能管范围、长度，但有些规则它管不了。比如玩家名字：前后的空格要去掉，去掉以后不能是空的。这时候自己写一个检查函数：

```python
from pydantic import BaseModel, Field, field_validator


class Game(BaseModel):
    player: str
    attempts: int = Field(ge=1, le=100, strict=True)

    @field_validator("player")          # 这个函数负责检查 player 字段
    @classmethod
    def clean_player(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("名字不能是空的")
        return v                        # 返回的值就是最后存进去的值
```

它做了两件事：**检查**（不合格就 `raise ValueError`），和**整理**（返回去掉空格的名字）。

```python
Game(player="  张三 ", attempts=5).player     # '张三'
Game(player="   ", attempts=5)                # 报错
```

```text
1 validation error for Game
player
  Value error, 名字不能是空的 [type=value_error, input_value='   ', input_type=str]
```

你在函数里写的那句「名字不能是空的」，出现在了报错里。

`@classmethod` 那一行别漏了，这是 pydantic 要求的写法，照抄就行。

## 四、Day 14 的文件怎么办

Day 14 的 `history.json` 不是一个对象，而是一个光秃秃的列表 `[5, 3, 8]`。这种「最外层不是对象」的数据，用 `TypeAdapter`：

```python
from typing import Annotated

from pydantic import Field, TypeAdapter

Attempts = Annotated[int, Field(ge=1, le=100, strict=True)]   # 给「1-100 的整数」起个名字
history = TypeAdapter(list[Attempts])                          # 一个列表，每一项都是 Attempts

history.validate_json("[5, 3, 8]")       # [5, 3, 8]
history.validate_json("[5, 300, 8]")     # 报错，位置是 (1,)：第二个数
```

`Annotated[int, Field(...)]` 读作「带着这些规则的 int」，起了名字以后可以到处复用。

你 Day 14 那三个 `if`，现在就是这两行。

## 五、今天的作业

在 `dailypractice/Day24/` 下：

1. **`leaderboard.py`**：写 `Game` 和 `Leaderboard` 两个模型，`Game` 带上去空格的 `field_validator`
2. 在同一个文件里写 `load_leaderboard(path) -> Leaderboard`：
   - 文件不存在：返回空的排行榜 `Leaderboard(games=[])`（和 Day 14 的规则一样）
   - 文件内容不对：让 `ValidationError` 直接抛出去，不要接住
3. **`test_leaderboard.py`**：用 Day 23 学的参数化测试，至少测这几种文件内容：正常的、JSON 不完整的、次数是 300 的、名字全是空格的，还有文件不存在

运行 `python -m pytest dailypractice/Day24 -v`，把代码和结果发给我。

写的时候可以对比一下：同样的检查，你 Day 14 写了多少行，今天写了多少行。

## 六、小测

**1.** `games.1.attempts` 这个报错位置是什么意思？

- A. 第 1 局的 `attempts`
- B. `games` 列表里下标为 1（也就是第 2 局）的 `attempts`
- C. 一共有 1 个错误

**2.** 用 `model_validate_json` 读一段不完整的 JSON，会抛什么异常？

- A. `json.JSONDecodeError`
- B. `ValidationError`
- C. 不报错，返回 `None`

**3.** `field_validator` 里 `return` 的值有什么用？

- A. 没用，只要不报错就行
- B. 就是最后存进模型的值，可以趁机整理数据
- C. 决定这个字段是否必填

<details>
<summary>答案</summary>

1. B。下标从 0 开始，1 是第二项。
2. B。pydantic 连 JSON 格式错误也包在 `ValidationError` 里，类型是 `json_invalid`。
3. B。比如把 `"  张三 "` 整理成 `"张三"` 再存进去。

</details>
