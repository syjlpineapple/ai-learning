# Day 10 · 模块拆分与程序入口

> **学习日** 2026-10-22（14:04 - 15:07，4 轮对话）
> **对应代码** [`dailypractice/Day10/`](../../../dailypractice/Day10/)（`game_logic.py` / `main.py` / `test_game.py` / `Demo.py`）
> **原始对话** `courseware/_raw/markdown/03_Python每日练习出题.md`（对话里称「第十天」）

## 本节掌握

- 每个 `.py` 文件都是一个模块
- `from 模块 import 函数` 复用代码
- `if __name__ == "__main__":` 的机制和用途
- **导入模块会执行它的顶层语句**——所以业务模块不能有副作用
- 三层拆分：业务逻辑 / 程序入口 / 测试
- 测试失败时必须真的失败（`raise`，不是 `print`）

这是整个 A 线的结构转折点：从单文件脚本变成多文件项目。

---

# 第一部分 · 知识讲解

## 1. 模块、包、库

| 概念 | 是什么 |
|---|---|
| **模块**（module） | 一个 `.py` 文件 |
| **包**（package） | 一个包含 `__init__.py` 的目录，里面装模块 |
| **库**（library） | 泛称，指一组可复用的模块或包 |

```text
dailypractice/              ← 包
├── __init__.py             ← 标记这是一个包
├── Day1.py                 ← 模块
└── Day10/                  ← 子包
    ├── __init__.py
    ├── game_logic.py       ← 模块
    └── main.py
```

`__init__.py` 可以是空文件，它的存在就是在说「这个目录是个包，可以被导入」。

> Python 3.3+ 引入了「命名空间包」，没有 `__init__.py` 也能导入。但显式放一个空的 `__init__.py` 更稳妥——它让包的边界明确，也避免某些工具（包括旧版 pytest）识别不到。

## 2. `import` 到底做了什么

`import` 不是「把某个函数抠出来」，它做三件事：

1. **找到**那个模块文件
2. **从头到尾执行一遍**它
3. 把模块对象（或你指定的成员）**绑定到当前命名空间**的名字上

第 2 步是本节最重要的认识，见第 4 节。

### 模块是怎么找到的：`sys.path`

```python
import sys
print(sys.path)
```

Python 按 `sys.path` 列表里的目录**顺序查找**，第一个匹配的就用。这个列表大致包含：

| 位置 | 来源 |
|---|---|
| 脚本所在目录（或当前目录） | 自动加入 |
| `PYTHONPATH` 环境变量里的目录 | 手动配置 |
| 标准库目录 | Python 安装自带 |
| `site-packages` | `pip install` 装的东西 |

**这解释了一类常见错误**：自己写了个 `random.py` 放在当前目录，然后 `import random` 导入的是自己那个文件，而不是标准库——因为当前目录在 `sys.path` 更前面。所以**不要用标准库的名字给自己的文件命名**。

### `__pycache__` 是什么

导入模块后，Python 会把编译结果缓存成 `.pyc` 文件放进 `__pycache__/` 目录，下次导入直接用缓存（更快）。

- 它是**自动生成的产物**，应该写进 `.gitignore`
- 源文件改动时会自动重新编译，一般不用管
- 偶尔遇到「改了代码却没生效」，删掉 `__pycache__` 可以排除缓存因素

## 3. `__name__`：判断「我是被运行还是被导入」

Python 给每个模块一个内置变量 `__name__`：

| 情况 | `__name__` 的值 |
|---|---|
| 直接运行这个文件 | `"__main__"` |
| 被别的文件 `import` | 模块名，如 `"game_logic"` |

所以这个惯用写法：

```python
if __name__ == "__main__":
    main()
```

含义是「**只在我被直接运行时才执行**」。它不是什么特殊语法，就是个普通的 `if` 判断——判断的对象恰好是「我现在的身份」。

用途：让一个文件既能当脚本跑，又能被当模块导入而不产生副作用。

## 4. 导入会执行模块的顶层代码

```python
# game_logic.py
def check_num(a, b):
    ...

print("启动了")          # ← 顶层语句
```

```python
# test_game.py
from game_logic import check_num      # 这一行会打印「启动了」
```

**`import` 会把整个模块文件执行一遍**，所以模块里所有不在函数体内、不在 `if __name__` 保护内的代码（统称**顶层代码**）都会执行。

这是「业务模块不能在顶层写启动代码」的根本原因：别人只想导入一个函数，结果整个程序跑起来了。

### 模块只会被执行一次

```python
import game_logic        # 执行模块代码
import game_logic        # 不再执行，直接用缓存
```

Python 把已导入的模块存在 `sys.modules` 里，重复导入直接取缓存。所以模块级的初始化代码（比如 `logging.basicConfig()`）只会生效一次——这个特性在 Day13 会有实际影响。

## 5. 绝对导入与相对导入

```python
# 绝对导入：从项目根开始写完整路径
from dailypractice.Day10.game_logic import check_num

# 相对导入：相对当前模块的位置
from .game_logic import check_num          # 同一个包里
from ..Day9 import something               # 上一级包
```

| | 绝对导入 | 相对导入 |
|---|---|---|
| 可读性 | 一眼看出模块来自哪 | 要先知道当前文件在哪 |
| 移动文件 | 要改 | 包内移动不用改 |
| 能否直接运行该文件 | 可以 | **不行**（会报错） |

**推荐默认用绝对导入**，这也是 PEP 8 的建议。相对导入只在包内部、且确定不会直接运行那个文件时使用。

### 裸导入的陷阱

```python
from game_logic import check_num      # 没有包路径
```

这种写法**只在「当前目录就是 `game_logic.py` 所在目录」时有效**。所以：

- `cd Day10 && python main.py` → 能用
- 从项目根跑 `pytest` → **`ImportError`**

因为两种情况下 `sys.path` 里的目录不同。这正是本节代码最初踩的坑——文件在当天能跑，但用 pytest 一直是 `ImportError`。

## 6. `python -m` 的作用

```bash
python dailypractice/Day10/main.py        # 直接运行文件
python -m dailypractice.Day10.main        # 作为模块运行
```

关键区别：

| | `python 文件路径` | `python -m 包.模块` |
|---|---|---|
| `sys.path[0]` | **脚本所在目录** | **当前工作目录** |
| 包内的绝对导入 | 可能失败 | 正常 |

用 `-m` 时，当前目录（通常是项目根）进入 `sys.path`，所以 `from dailypractice.Day10.game_logic import ...` 能找到。而直接运行文件时，`sys.path[0]` 是 `Day10/` 目录，根本看不到 `dailypractice` 这个包。

**所以这个仓库的约定是从根目录用 `python -m` 跑脚本**（根 `README.md` 里写了这条）：

```bash
python -m dailypractice.Day10.main
```

注意 `-m` 后面用**点号**分隔、**不带 `.py` 后缀**——因为那是模块路径，不是文件路径。

## 7. 循环导入

```python
# a.py
from b import foo

# b.py
from a import bar        # ImportError: cannot import name 'bar'
```

两个模块互相导入会出问题：导入 `a` 时执行到第一行去导入 `b`，`b` 又要导入 `a`，但 `a` 还没执行完，`bar` 还不存在。

**循环导入通常说明模块划分有问题**——两个模块职责纠缠在一起了。解决办法按优先级：

1. **重新划分职责**，把共用的东西提到第三个模块
2. 把 `import` 移到函数内部（延迟到调用时才导入）
3. 改成 `import b` 而不是 `from b import foo`（有时能绕过）

前两天还不会遇到，但模块一多就会碰上。

## 8. 模块的职责划分

本节把一个文件拆成三个，划分依据是**职责**：

| 文件 | 职责 | 不该做什么 |
|---|---|---|
| `game_logic.py` | 业务逻辑（判断、校验） | 不调 `input()`、不打印、顶层不启动程序 |
| `main.py` | 交互与流程控制 | 不写业务规则 |
| `test_game.py` | 验证业务逻辑 | 不需要启动游戏、不需要人工输入 |

这样划分的收益：

- **改交互不影响测试**——`main.py` 怎么改，`test_game.py` 都不用动
- **业务逻辑可复用**——以后做成网页服务，`game_logic.py` 原样能用
- **测试不依赖交互**——这是能自动化的前提

> 这是 Day04「职责分离」从函数级升级到了文件级。同一条原则会继续升级：
> Day20 会分成 `config.py` / `api_client.py` / `main.py` 三层。

## 9. 测试文件的组织

两种常见布局：

```text
# 布局 A：测试和源码放一起
Day10/
├── game_logic.py
└── test_game.py

# 布局 B：测试单独一个目录
project/
├── src/
│   └── game_logic.py
└── tests/
    └── test_game.py
```

小项目用 A（就近，方便），正式项目多用 B（源码目录干净，打包时容易排除测试）。

命名约定（pytest 的默认规则）：

- 文件名 `test_*.py` 或 `*_test.py`
- 函数名 `test_*`
- 类名 `Test*`

**遵守约定的好处是测试框架能自动发现**，不用手工注册。Day21 会正式用上。

---

# 第二部分 · 当天的练习

## 一、题目

把猜数字游戏拆成三个文件：

| 文件 | 职责 |
|---|---|
| `game_logic.py` | 只放 `parse_guess()`、`check_num()`，不调 `input()`，导入时不启动游戏 |
| `main.py` | 交互流程，启动代码放进入口保护 |
| `test_game.py` | 导入业务函数做测试，**不需要启动游戏、不需要手动输入** |

## 二、先理解 `if __name__ == "__main__"`

`Demo.py` 就是为了搞懂这件事：

```python
def greet() -> None:
    print("Hello World")

if __name__ == "__main__":
    greet()
```

机制是这样的：Python 给每个模块一个内置变量 `__name__`。

| 情况 | `__name__` 的值 |
|---|---|
| 直接运行这个文件（`python Demo.py`） | `"__main__"` |
| 被别的文件 `import` | 模块名，比如 `"Demo"` |

所以 `if __name__ == "__main__":` 的含义是「**只在我被直接运行时才执行**」。它不是「程序入口」这种语法关键字，只是一个普通的 `if` 判断——判断的对象恰好是「我现在是被运行还是被导入」。

用途：让一个文件既能当脚本跑，又能被当模块导入而不产生副作用。

## 三、最重要的一点：导入会执行顶层语句

当时的思考题：**如果在 `game_logic.py` 最后一行加 `print("游戏启动了")`，然后运行 `test_game.py`，这句会打印吗？**

**会打印。**

因为这一行：

```python
from game_logic import check_num, parse_guess
```

Python 的 `import` 不是「把某个函数抠出来」，而是**把整个模块文件从头到尾执行一遍**，然后把你要的名字绑过来。所以模块里所有不在函数体内、不在 `if __name__` 保护内的代码（也就是「顶层语句」）都会执行。

这就是为什么业务模块不能在顶层写启动代码：别人只想导入一个函数，结果整个游戏跑起来了。

> `Day10/game_logic.py` 最后一行现在还留着 `print("启动了")`——那是当年做这个实验留下的。它意味着现在**每次导入 `game_logic` 都会打印一次「启动了」**，包括跑测试的时候。复习时不要以为那是正确写法。

## 四、三个文件

### `game_logic.py`：只定义，不执行

```python
def parse_guess(input_num: str) -> int:
    try:
        int_num = int(input_num)
    except ValueError:
        raise ValueError("输入格式错误，请输入整数") from None
    if not 1 <= int_num <= 100:
        raise ValueError("请输入1~100的整数") from None
    return int_num

def check_num(input_num: int, target_num: int) -> str:
    if input_num < target_num:
        return "小了"
    elif input_num > target_num:
        return "大了"
    else:
        return "正确"
```

这里第二个 `from None` 是多余的。`from None` 的作用是**隐藏当前正在处理的异常的上下文**，而这一行不在 `except` 块里，压根没有「正在处理的异常」。写了不报错，但没有任何效果——说明当时对 `from None` 的理解还停留在「加上更规范」的层面。

> 判断标准：`from None` 只在 `except` 块内部的 `raise` 上才有意义。

### `main.py`：交互与启动

```python
import random

from dailypractice.Day10.game_logic import parse_guess, check_num

if __name__ == "__main__":
    target_num = random.randint(1, 100)
    print("随机数", target_num)

    while True:
        input_num = input("请输入1~100的数字，输入q退出")
        if input_num == "q":
            print("游戏结束！")
            break
        else:
            try:
                int_num = parse_guess(input_num)
                result = check_num(int_num, target_num)
                print(result)
            except ValueError as e:
                print(e)
```

### `test_game.py`：独立测试

```python
from dailypractice.Day10.game_logic import check_num, parse_guess

if __name__ == "__main__":
    assert check_num(10, 20) == "小了"
    assert check_num(20, 20) == "正确"
    assert check_num(20, 10) == "大了"

    assert parse_guess("1") == 1
    assert parse_guess("100") == 100

    try:
        parse_guess("abc")
    except ValueError:
        pass
    else:
        raise AssertionError("输入 abc 时预期出现 ValueError")
```

**导入路径说明：** 这三个文件最初写的是 `from game_logic import ...`（裸导入），只在「切到该目录直接运行」时有效，用 pytest 跑一直是 `ImportError`。迁移到独立仓库时改成了完整包路径 `dailypractice.Day10.game_logic`。这个坑后面 Day 21 会正面撞上一次。

## 五、当天的三个坑

### 坑 1：`q` 分支又少了 `break`

```python
if input_num == "q":
    print("游戏结束！")      # 打印完继续下一轮
```

**这是 Day 06 踩过的同一个坑。** 相隔两天又犯一次，说明「`if` 分支里做完事要明确流程去向」这件事当时还没形成习惯。

### 坑 2：猜对了也不退出

主循环里只打印 `result`，没判断「正确」就 `break`。所以猜中之后游戏还在继续问。

正确的是：

```python
if result == "正确":
    print("恭喜你，猜对了！")
    break
```

> 两个坑是同一类问题：**只写了「发生什么」，没写「然后去哪」。** 循环里的每个分支都该问一句：这一轮结束后，是继续、还是退出？

### 坑 3：测试失败时只打印，不报错

当时写的是：

```python
try:
    parse_guess("abc")
except ValueError:
    pass
else:
    print("应该报错：格式错误")      # ← 只是打印
```

问题：如果 `parse_guess("abc")` 居然没抛异常，这段代码只会打印一句话，然后**程序正常结束，退出码是 0**。自动化流程（CI、脚本）看到退出码 0 就认为测试通过了。

必须改成抛异常：

```python
else:
    raise AssertionError("输入 abc 时预期出现 ValueError")
```

> 原则：**测试失败必须让进程以非零退出码结束。** 打印只给人看，机器不认。这和 Day 04 的「`print` 给人看、`return` 给程序用」是同一个道理的另一面。

## 六、现在回头看：这些测试一次都没跑过

`test_game.py` 的断言被包在 `if __name__ == "__main__":` 里面。当时 ChatGPT 说这「没有问题」——单看那天的要求（直接运行 `python test_game.py`）确实没问题。

但从 pytest 的角度，这是致命的。实测：

```
$ pytest dailypractice/Day10/
collecting ... collected 0 items
no tests ran
```

**一个测试都没有被收集到。** 两个原因叠加：

1. **断言在 `if __name__ == "__main__"` 块里。** pytest 是 `import` 测试文件，不是直接运行它，所以 `__name__` 是模块名，整个块被跳过。
2. **文件里没有 `test_` 开头的函数。** pytest 靠命名约定发现测试——文件名 `test_*.py`、函数名 `test_*`。这个文件满足了文件名，但里面一个 `test_` 函数都没有。

所以这个文件在 pytest 眼里是「一个成功导入、但不含任何测试的空文件」，不报错、不警告，静静地贡献 0 个测试。全仓库 `pytest` 跑出 13 passed，没有一个来自这里。

正确的写法是把断言放进 `test_` 函数、去掉入口保护：

```python
from dailypractice.Day10.game_logic import check_num, parse_guess


def test_check_num() -> None:
    assert check_num(10, 20) == "小了"
    assert check_num(20, 20) == "正确"
    assert check_num(20, 10) == "大了"


def test_parse_guess() -> None:
    assert parse_guess("1") == 1
    assert parse_guess("100") == 100
```

> 这是本节最该记住的一条：**「测试文件存在」和「测试在跑」是两件事。** 判断依据只有一个——看 pytest 报告的收集数量。看到 `collected 0 items` 要立刻警觉。

## 七、复习自测

1. `__name__` 在「直接运行」和「被导入」时分别是什么值？
2. `from game_logic import check_num` 时，`game_logic.py` 里的顶层 `print()` 会执行吗？为什么？
3. 为什么业务模块不该在顶层写启动代码？
4. `raise ValueError("...") from None` 写在 `except` 块外面有什么效果？
5. 测试失败时 `print("出错了")` 和 `raise AssertionError("出错了")` 有什么本质区别？
6. 把断言包在 `if __name__ == "__main__"` 里，用 pytest 跑会怎样？

<details>
<summary>参考答案</summary>

1. 直接运行时是字符串 `"__main__"`；被导入时是模块名（如 `"game_logic"`）。
2. 会执行。`import` 的机制是把整个模块文件执行一遍，再把需要的名字绑过来，所有顶层语句都会运行。
3. 因为别人只是想导入其中一个函数，却会连带启动整个程序。模块应该只定义东西，启动逻辑放在 `main.py` 的入口保护里。
4. 没有任何效果（但不报错）。`from None` 的作用是隐藏「当前正在处理的异常」的上下文，而 `except` 块外面不存在正在处理的异常。
5. `print` 只是输出文字，进程退出码仍是 0，自动化流程会认为测试通过；`raise` 会让进程以非零退出码结束，CI 才能识别为失败。
6. pytest 是 import 测试文件而非直接运行，`__name__` 不等于 `"__main__"`，整个块被跳过。再加上文件里没有 `test_` 开头的函数，结果是 `collected 0 items`——不报错，但一个测试也没执行。

</details>
