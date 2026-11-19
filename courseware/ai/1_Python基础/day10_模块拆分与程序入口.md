---
kind: lesson
outline: [2, 2]
time: 45 分钟
uses: [模块与 import, __name__, 入口保护, python -m, pytest 收集测试]
record:
  - text: 当时的代码 Day10/
    link: https://github.com/syjlpineapple/ai-learning/tree/main/dailypractice/Day10
---

# Day 10：一个文件拆成三个

看看你的 `Day9.py`：上面是 `parse_guess()`，中间是被注释掉的交互代码，下面是测试。为了跑测试，你只好把交互代码注释掉，不然一运行就停下来等输入。

这说明三样东西不该挤在一个文件里。今天把它们拆开：业务函数一个文件，启动游戏一个文件，测试一个文件。

## 一、每个 `.py` 文件都是一个模块

Day 3 你 `import random`，导入的是 Python 自带的模块。你自己写的 `.py` 文件也是模块，同样可以导入：

```python
from game_logic import parse_guess, check_num
```

这一行的意思是：找到 `game_logic.py`，把里面的 `parse_guess` 和 `check_num` 拿过来用。

这里有一件很关键的事：**`import` 会把那个文件从头到尾执行一遍。** 它不是只把函数「抠」出来，而是整个文件跑一遍，再把你要的名字拿过来。

我写了一个 `greet.py`，在函数外面放了一行 `print`：

```python
def greet() -> None:
    print("你好，Python！")


print("greet.py 里的 __name__ 是：", __name__)

if __name__ == "__main__":
    greet()
```

再写一个文件，只导入它，不调用任何函数：

```python
from guess import greet

print("导入完成")
```

运行这个文件：

```text
greet.py 里的 __name__ 是： guess.greet
导入完成
```

只是导入，`greet.py` 里函数外面的那行 `print` 就执行了。这说明：**业务模块的函数外面，不能放启动游戏的代码**，不然别人只想借用一个函数，整个游戏就跑起来了。

## 二、`__name__`：我是被运行，还是被导入

上面打印的 `__name__` 是 Python 给每个文件自动准备的变量。它的值取决于这个文件是怎么被用的：

| 情况 | `__name__` 的值 |
|---|---|
| 直接运行这个文件 | `"__main__"` |
| 被别的文件导入 | 模块名，上面是 `guess.greet` |

直接运行 `greet.py`：

```text
greet.py 里的 __name__ 是： __main__
你好，Python！
```

被导入时 `greet()` 没有执行，直接运行时执行了，区别就在最后两行：

```python
if __name__ == "__main__":
    greet()
```

它不是什么特殊语法，就是一个普通的 `if`，判断的是「我现在是不是被直接运行」。放在这里面的代码，被导入时不会执行。所以启动游戏的代码要放进这个 `if`。

## 三、三个文件各管一件事

| 文件 | 放什么 | 不放什么 |
|---|---|---|
| `game_logic.py` | `parse_guess()`、`check_num()` | `input()`、启动代码 |
| `main.py` | 输入、循环、打印提示，放在 `if __name__ == "__main__":` 里 | 判断和校验的规则 |
| `test_game.py` | 导入业务函数，检查它们 | `input()` |

这样拆开，改交互不用动测试，测试也不用启动游戏。以后把游戏做成网页，`game_logic.py` 原样就能用。这是 Day 5「函数只负责判断」从函数这一层，升级到了文件这一层。

## 四、从哪里运行：`python -m`

`from game_logic import ...` 要能成功，Python 得知道去哪里找 `game_logic.py`。它会在一串目录里找，第一个目录取决于你**怎么运行**程序。

我建了一个小项目，目录是 `pe_a3_proj/guess/`，里面有 `main.py` 和 `game_logic.py`，`main.py` 用完整的包路径导入：

```python
from guess.game_logic import check_num
```

在 `pe_a3_proj` 下用两种方式运行（第一种只留了报错的最后一行）：

```text
> python guess\main.py
ModuleNotFoundError: No module named 'guess'

> python -m guess.main
sys.path[0] = C:\Users\hubo\AppData\Local\Temp\pe_a3_proj
小了
```

`sys.path[0]` 就是 Python 找模块的第一个目录。直接运行文件路径时，它是 `main.py` 所在的 `guess` 目录，在那里面找不到一个叫 `guess` 的东西，所以报错。用 `python -m` 时，它是你当前所在的目录，也就是项目根，`guess` 包就在这里。

记住：**从项目根目录，用 `python -m 包名.模块名` 运行。** 注意 `-m` 后面用点分隔，不带 `.py`，因为它是模块名，不是文件路径。

这个仓库就是这么约定的，比如 `python -m dailypractice.Day10.test_game`。另外，仓库用 `pip install -e .` 把 `dailypractice` 注册成了已安装的包，所以在这个仓库里直接运行文件路径也能找到它；没有注册的项目，就会遇到上面的报错。

## 五、今天的作业

**任务 1**：读下面的代码，用自己的话回答：

```python
def greet() -> None:
    print("你好，Python！")


if __name__ == "__main__":
    greet()
```

1. 直接运行这个文件，会发生什么？
2. 另一个文件 `import` 它，`greet()` 会自动执行吗？
3. `if __name__ == "__main__":` 解决了什么问题？

**任务 2**：新建 `game_logic.py`，放进 `parse_guess()` 和 `check_num()`；新建 `main.py`，导入这两个函数，写一个能连续猜的循环：输入 `q` 退出，非法输入提示，猜对结束。启动代码放进入口保护。

**任务 3**：新建 `test_game.py`，导入业务函数，测试 `check_num()` 的三种结果，`parse_guess("1")`、`parse_guess("100")`，以及 `parse_guess("abc")` 会抛 `ValueError`。运行它，确认不需要启动游戏。

**思考题**：在 `game_logic.py` 最后一行加上 `print("游戏启动了")`，再运行 `test_game.py`，这句话会打印吗？

## 六、小测

**1.** 被别的文件导入时，一个模块的 `__name__` 是什么？

- A. `"__main__"`
- B. 模块名
- C. 空字符串

**2.** `from game_logic import check_num` 执行时，`game_logic.py` 里函数外面的 `print()` 会执行吗？

- A. 会
- B. 不会，只拿了 `check_num`

**3.** 用 `python -m` 运行时，后面应该写哪个？

- A. `dailypractice/Day10/test_game.py`
- B. `dailypractice.Day10.test_game`

<details>
<summary>答案</summary>

1. B。只有直接运行时才是 `"__main__"`。
2. A。`import` 会执行整个文件，函数外面的语句都会跑。
3. B。`-m` 后面要的是模块名，写成 A 会报找不到模块。

</details>

## 讲评（10-22）

**任务 1** 你答的是「会打印你好，Python！」「不会」「入口」。三个都对。第三个可以说得更准确一点：它区分的是「被直接运行」还是「被导入」，被导入时把启动代码挡在外面，叫「入口保护」更贴切。

**任务 2** 交了两版。第一版拆分是对的，`main.py` 也用上了入口保护，但只调用了一次 `input()`，猜一次就结束了。第二版加了 `while True`，又出了 Day 7 出过的问题：输入 `q` 只打印「游戏结束！」，没有 `break`；猜对了也不退出。仓库里的 `main.py` 补上了 `q` 的 `break`，猜对那一支还没有。我把答案设成 50 跑了一下：

```text
启动了
随机数 50
请输入1~100的数字，输入q退出abc
输入格式错误，请输入整数
请输入1~100的数字，输入q退出101
请输入1~100的整数
请输入1~100的数字，输入q退出50
正确
请输入1~100的数字，输入q退出50
正确
请输入1~100的数字，输入q退出q
游戏结束！
```

猜对两次还在问。这两个坑是同一类：**只写了这一轮「发生什么」，没写「接下来去哪」。** 写循环里的每个分支时，都问一句：这之后是继续，还是退出？

第一行的「启动了」是思考题留下的。你在 `game_logic.py` 末尾加了 `print("启动了")` 做实验，答案是会打印，和第一节演示的一样。实验做完这行没删，现在每次导入 `game_logic` 都会打印它。

`game_logic.py` 里还有一处：

```python
    if not 1 <= int_num <= 100:
        raise ValueError("请输入1~100的整数") from None
```

这里的 `from None` 没有作用。昨天说过，它只在 `except` 里面才有「正在处理的旧异常」可以藏，这一行不在 `except` 里。我对比了加和不加，报错一模一样。写了不报错，但删掉更清楚。

**任务 3** 交的测试：

```python
from game_logic import check_num,parse_guess

if __name__ == "__main__":
    assert check_num(10,20) == "小了"
    ...
    try:
        parse_guess("abc")
    except ValueError:
        pass
    else:
        print("应该报错：格式错误")
```

`else` 里用了 `print`，讲评让你改成 `raise AssertionError(...)`，你改了。为什么一定要改？我写了一个故意不做校验的 `parse_guess`，两种写法各跑一次：用 `print` 的，屏幕上出现「应该报错：格式错误」，程序**正常结束，退出码 0**；用 `raise` 的，报 `AssertionError`，退出码 1。以后测试是交给工具自动跑的，工具只看退出码，不读你打印的字。

> 注意：当时的讲评说测试文件用 `if __name__ == "__main__":` 包起来「没有问题」。直接运行确实没问题，但交给 pytest 一个测试都不会跑。
<details>
<summary>为什么</summary>

我在仓库根目录实际跑了一次：

```text
collected 0 items
============================ no tests ran in 0.05s ============================
```

原因有两层。一是 pytest 是**导入**测试文件，不是直接运行它，所以 `__name__` 不是 `"__main__"`，整块被跳过。二是 pytest 只认名字以 `test` 开头的函数，这个文件里一个函数都没有。

</details>

正确的写法是把断言放进 `test_` 开头的函数，去掉入口保护：

```python
from dailypractice.Day10.game_logic import check_num, parse_guess


def test_check_num() -> None:
    assert check_num(10, 20) == "小了"
    assert check_num(20, 20) == "正确"
    assert check_num(20, 10) == "大了"


def test_parse_guess() -> None:
    assert parse_guess("1") == 1
    assert parse_guess("100") == 100
    try:
        parse_guess("abc")
    except ValueError:
        pass
    else:
        raise AssertionError("输入 abc 时预期出现 ValueError")
```

我在那个小项目里用同样的写法跑了 pytest：

```text
collecting ... collected 2 items
guess/test_game.py::test_check_num PASSED                                [ 50%]
guess/test_game.py::test_parse_guess PASSED                              [100%]
============================== 2 passed in 0.04s ==============================
```

这和 Day 8 那次「定义了测试函数却没调用」是同一个坑：文件在，测试却没在跑，而且不报错、不提醒。以后用 pytest，先看它报告收集到了几个测试，`collected 0 items` 就要警觉。

最后说一下导入路径。你当时写的是 `from game_logic import ...`，在 `Day10` 目录里直接运行能找到，因为第四节说过，那时 Python 先在文件所在的目录找。整理进仓库时改成了 `from dailypractice.Day10.game_logic import ...`，这样从仓库根目录用 `python -m` 运行、或者用 pytest 跑，都能找到。
