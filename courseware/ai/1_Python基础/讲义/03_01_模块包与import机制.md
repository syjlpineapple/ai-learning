# 3.1 模块、包与 `import` 机制

> **前置** 2.3 从 `assert` 到 `pytest`
> **时长** 约 100 分钟（讲解 45 + 练习 55）
> **配套代码** [`code/m03_structure/ch03_01_*.py`](../../code/m03_structure/)

## 学习目标

学完这一章，你应该能够：

1. 说出 `import` 做的三件事，解释模块顶层的 `print` 为什么在导入时会执行、而且只执行一次
2. 说出 `python 文件路径`、`python -m 模块名`、`python -c` 三种运行方式下 `sys.path[0]` 分别是什么，并**据此判断一条 `import` 会不会失败**
3. 说出 `__name__` 在三种情况下的值，解释第 2.3 章那个问题：`if __name__ == "__main__":` 里的断言为什么在 pytest 下不执行
4. 区分绝对导入、相对导入、裸导入，说出各自在哪种运行方式下会失败
5. **解释 `from config import LEVEL` 之后为什么看不到 `config.LEVEL` 的变化**
6. 读懂循环导入的报错，给出三种解法，并说出哪一种真正消除了循环
7. **说出 `pytest` 和 `python -m pytest` 的区别**，以及为什么这门课的代码仓要求 `pip install -e`
8. 写一个「遮蔽检查器」和一个「循环导入检测器」

## 为什么需要这一章

到目前为止，这门课一直要求你这样运行示例：

```powershell
python -m m02_testing.ch02_03_example        # ✓ 课程要求的写法
python m02_testing/ch02_03_example.py        # ✗ 为什么不行？
```

一直没解释为什么。第 2.3 章结尾也留了一个问题：断言写在 `if __name__ == "__main__":` 里，pytest 为什么一条都收集不到。

学习记录 Day10 里有一个更具体的例子。猜数字游戏拆成三个文件以后，`main.py` 里写的是：

```python
from game_logic import check_num, parse_guess
```

切到那个目录里运行，一切正常；回到项目根目录跑 pytest，一直是 `ImportError`。**同一份代码，换个地方运行结果就不一样。**

这一章把 `import` 的机制讲清楚。讲完以后，上面这些现象都能用同一条规则解释：**Python 只在 `sys.path` 列出的目录里找模块，而 `sys.path[0]` 取决于你怎么启动程序。**

### 本章的实验项目

讲解里所有输出都来自 `ch03_01_example.py`。它在临时目录里搭一个小项目 `lab/`，然后**每个场景开一个新的 Python 进程**来跑（同一个进程里做实验会被 `import` 缓存干扰，第 1 节会讲为什么）。

```text
lab/
├── app/
│   ├── __init__.py      打印一行「被执行」
│   ├── util.py          打印一行「被执行」，定义 VALUE = 42
│   ├── main.py          打印 sys.path[0] 和 __name__，然后 from app import util
│   ├── who.py           打印 __name__ 和 __package__
│   ├── rel.py           from .util import VALUE        （相对导入）
│   ├── bare.py          from util import VALUE         （裸导入，Day10 的写法）
│   └── twice.py         import app.util 写两遍
├── cyc/    a.py ⇄ b.py   用 from 形式互相导入
├── cyc2/   a.py ⇄ b.py   用 import 形式互相导入
├── snap/   config.py、use.py
├── dual/   state.py、other.py
├── warn/   __init__.py、tool.py
├── ns/     mod.py       ← 这个目录没有 __init__.py
├── tests/  test_lab.py  from app import util
└── shadow/ random.py    一个空文件
```

```powershell
python -m m03_structure.ch03_01_example
```

---

# 一、概念与原理

## 1. `import` 做的三件事

`import app.util` 这一行，Python 做了三件事：

1. **找到**模块文件：按顺序搜索 `sys.path` 里的每个目录
2. **执行**它：从第一行到最后一行，跑一遍
3. **绑定名字**：把得到的模块对象放进当前命名空间

第 2 步最容易被忽略。**`import` 不是「把函数抠出来」，而是把整个文件执行一遍。** 模块顶层（不在函数体里）的每一行都会运行，包括 `print`、包括启动游戏的代码。这就是 Day10 结论「业务模块不能在顶层写启动代码」的原因。

### 模块只执行一次

`lab/app/twice.py` 把同一个 `import` 写了两遍：

```python
import sys
import app.util
import app.util
print("第二次 import 没有再执行 util.py；它在 sys.modules 里：", "app.util" in sys.modules)
```

```text
  $ (lab/) python -m app.twice
      [app/__init__.py 被执行]
      [util.py 被执行]
      第二次 import 没有再执行 util.py；它在 sys.modules 里： True
```

`util.py` 只打印了一次。执行完的模块会存进字典 `sys.modules`，**之后再 `import` 同一个名字，直接从这个字典里取，不再执行文件**。

这个缓存带来两个后果：

- 模块级的初始化（比如第 4.4 章的 `logging.basicConfig()`）在一个进程里只生效一次
- 在同一个进程里反复做 `import` 实验，看到的是缓存，不是新结果。所以示例给每个场景开一个新进程

注意输出的第一行：**导入 `app.util` 之前，先执行了 `app/__init__.py`**。导入包里的任何子模块，都会先执行这个包的 `__init__.py`。

### `__pycache__`

模块第一次导入时，Python 会把编译结果写进同目录的 `__pycache__/` 文件夹，文件名形如 `util.cpython-313.pyc`。下次导入时如果源文件没改，就直接用它。

- 它是自动生成的，应该写进 `.gitignore`（第 0.2 章的模板里已经有了）
- **删掉源文件以后，`__pycache__` 里的 `.pyc` 不会让模块「复活」**。实测：`gone.py` 导入一次后删掉，`.pyc` 还在，再导入就是 `ModuleNotFoundError: No module named 'gone'`。所以重命名或删除文件之后，不用担心旧缓存还在起作用

## 2. 模块是怎么找到的：`sys.path`

`sys.path` 是一个目录列表。Python 按顺序在每个目录里找，**第一个找到的就用**，后面的不再看。

| 位置 | 来源 |
|---|---|
| **`sys.path[0]`** | **取决于启动方式**（下表） |
| `PYTHONPATH` 环境变量里的目录 | 手动设置，平时不建议用 |
| 标准库目录 | Python 安装时自带 |
| `site-packages` | `pip install` 装的东西都在这里 |

前三类都排在 `site-packages` 前面，所以第 1.4 章说的「自己的 `random.py` 遮蔽标准库」会发生。

### `sys.path[0]` 取决于启动方式

`lab/app/main.py` 先打印 `sys.path[0]`，再执行 `from app import util`。在 `lab/` 下用两种方式运行它：

```text
  $ (lab/) python app/main.py
      sys.path[0] = <lab>\app
      __name__   = __main__
      Traceback (most recent call last):
        File "<lab>\app\main.py", line 4, in <module>
          from app import util
      ModuleNotFoundError: No module named 'app'
      → 退出码 1

  $ (lab/) python -m app.main
      [app/__init__.py 被执行]
      sys.path[0] = <lab>
      __name__   = __main__
      [util.py 被执行]
      VALUE      = 42
      → 退出码 0
```

| 启动方式 | `sys.path[0]` |
|---|---|
| `python app/main.py` | **脚本所在的目录** `lab/app/` |
| `python -m app.main` | **当前工作目录** `lab/` |
| `python -c "..."` | 空字符串 `''`，也代表当前目录 |

用文件路径运行时，`sys.path[0]` 是 `lab/app/`。Python 在 `lab/app/` 里找一个叫 `app` 的模块或包，当然找不到。用 `-m` 运行时，`sys.path[0]` 是 `lab/`，`lab/app/` 正是一个叫 `app` 的包。

**这条规则解释了本章开头所有的现象。** 判断一条 `import` 会不会失败，先问自己：这次启动，`sys.path[0]` 是哪个目录？要导入的名字在那个目录下吗？

> Python 3.11 加了 `-P` 选项（环境变量 `PYTHONSAFEPATH`），作用是**不把上面这个目录放进 `sys.path`**。
> 实测 `python -P -m app.main` 报 `No module named 'app'`。了解即可，这门课不用它。

## 3. `__name__`：我是被运行，还是被导入

每个模块都有一个内置变量 `__name__`。`lab/app/who.py` 打印它和 `__package__`：

```text
  $ (lab/) python app/who.py
      __name__='__main__'  __package__=None

  $ (lab/) python -m app.who
      [app/__init__.py 被执行]
      __name__='__main__'  __package__='app'

  $ (lab/) python -c import app.who
      [app/__init__.py 被执行]
      __name__='app.who'  __package__='app'
```

| 情况 | `__name__` | `__package__` |
|---|---|---|
| 用文件路径运行 | `'__main__'` | `None`（**不知道自己属于哪个包**） |
| 用 `-m` 运行 | `'__main__'` | `'app'` |
| 被别的代码导入 | **模块的完整名字** `'app.who'` | `'app'` |

所以 `if __name__ == "__main__":` 的意思是「**只有我是被运行的那个模块时才执行**」。它不是特殊语法，就是一个普通的 `if`。

**回答第 2.3 章的问题**：pytest 收集测试时用的是**导入**。导入时 `__name__` 是 `'test_game'` 这样的模块名，不等于 `'__main__'`，整个块被跳过。

`__package__` 这一列下一节会用到：**用文件路径运行时它是 `None`，相对导入就是因为这个失败的。**

## 4. `python -m` 的作用

`-m` 的意思是「**按模块名找到它，当成主程序运行**」。和直接给文件路径相比，它有两个作用：

1. `sys.path[0]` 是当前目录，所以从项目根目录出发的绝对导入能找到
2. 模块知道自己属于哪个包（`__package__` 有值），所以相对导入能用

第 0.2 章说过 `python -m venv` 比直接敲 `venv` 更可靠，当时留了一句「第 3.1 章会详细讲 `-m`」。原因是 `-m` 还有一个作用：**用的一定是你敲的这个 `python`**。同样的道理适用于 `python -m pip`、`python -m pytest`：直接敲 `pip`，找到的可能是另一个 Python 的 `pip`。

### ⚠️ `-m` 后面写成了文件路径

`-m` 后面是模块名：**用点分隔，不带 `.py`**。写错时有两种情况，第二种比较隐蔽：

```text
  $ (lab/) python -m app/main.py
      ...python.exe: Error while finding module specification for 'app/main.py'
      (ModuleNotFoundError: No module named 'app/main'). Try using 'app/main' instead
      of 'app/main.py' as the module name.
      → 退出码 1

  $ (lab/) python -m app.main.py
      [app/__init__.py 被执行]
      sys.path[0] = <lab>
      __name__   = app.main
      [util.py 被执行]
      VALUE      = 42
      ...python.exe: Error while finding module specification for 'app.main.py'
      (ModuleNotFoundError: __path__ attribute not found on 'app.main' while trying
      to find 'app.main.py'). Try using 'app.main' instead of 'app.main.py' as the module name.
      → 退出码 1
```

**`python -m app.main.py` 报错之前，`main.py` 已经完整执行了一遍。** Python 把 `app.main.py` 理解成「`app.main` 包里的 `py` 子模块」，于是先导入 `app.main`（注意 `__name__ = app.main`，它是被当成普通模块导入的），然后才发现 `app.main` 不是包，下面没有 `py`。

如果 `main.py` 的顶层有副作用（写文件、发请求），这些副作用已经发生了。好在提示信息写得很清楚：`Try using 'app.main' instead of 'app.main.py'`。

## 5. 绝对导入、相对导入、裸导入

```python
from app.util import VALUE      # 绝对导入：从 sys.path 里的某个目录开始写完整路径
from .util import VALUE         # 相对导入：相对当前模块所在的包（一个点 = 同一个包）
from util import VALUE          # 裸导入：直接写模块名，不写包名
```

三种写法在不同运行方式下的结果，全部实测：

```text
  $ (lab/) python app/rel.py
      ImportError: attempted relative import with no known parent package
  $ (lab/) python -m app.rel
      rel VALUE = 42
  $ (lab/) python -m app.bare
      ModuleNotFoundError: No module named 'util'
  $ (lab/app/) python bare.py
      bare VALUE = 42
```

| 写法 | `lab/` 下 `python -m app.xxx` | `lab/` 下 `python app/xxx.py` | `lab/app/` 下 `python xxx.py` |
|---|---|---|---|
| 绝对 `from app.util import` | ✓ | ✗ `ModuleNotFoundError` | ✗ |
| 相对 `from .util import` | ✓ | ✗ `ImportError` | ✗ |
| 裸 `from util import` | ✗ `ModuleNotFoundError` | ✓ | ✓ |

**相对导入失败的原因**是上一节表里的 `__package__ = None`：用文件路径运行时，模块不知道自己在哪个包里，「同一个包」无从谈起。报错信息 `no known parent package` 说的正是这件事。

**裸导入的问题**是它只在 `sys.path[0]` 恰好是模块所在目录时才有效。Day10 的代码在 `Day10/` 目录里直接运行时能用，从项目根目录跑 pytest 时 `sys.path` 里没有 `Day10/`，于是 `ImportError`。

**这门课的约定**：

- **一律用绝对导入**，从包名开始写：`from m02_testing.ch02_03_example import parse_guess`。这也是 PEP 8 的建议，读代码的人一眼就知道它来自哪
- **一律在 `code/` 目录下用 `python -m` 运行**
- 不用裸导入

相对导入不是错的，大型包内部常用它（包改名时不用改内部的导入）。这门课的代码量用不上，统一用绝对导入更简单。

## 6. ⚠️ `from X import 名字` 拿到的是那一刻的值

`lab/snap/config.py` 有一个模块级变量和一个修改它的函数：

```python
# snap/config.py
LEVEL = "INFO"

def set_level(value):
    global LEVEL
    LEVEL = value
```

```python
# snap/use.py
import snap.config
from snap.config import LEVEL, set_level

set_level("DEBUG")
print("from 导入的 LEVEL   =", LEVEL)
print("snap.config.LEVEL   =", snap.config.LEVEL)
```

```text
  $ (lab/) python -m snap.use
      from 导入的 LEVEL   = INFO
      snap.config.LEVEL   = DEBUG
```

**`from snap.config import LEVEL` 等价于 `LEVEL = snap.config.LEVEL`**：在 `use.py` 里新建一个名字，指向导入那一刻 `snap.config.LEVEL` 指向的对象。之后 `config.py` 里的 `LEVEL` 改指向了 `"DEBUG"`，`use.py` 里的 `LEVEL` 还指向原来的 `"INFO"`。

这和第 1.7 章「赋值是引用」是同一个道理：两个名字原来指向同一个对象，其中一个改指向别处，另一个不受影响。

**什么时候会踩到**：

- 模块里有「运行中会被修改」的全局变量（配置、计数器），别的模块用 `from` 导入了它
- 测试里替换某个函数（第 2.3 章的变异测试、第 8.1 章的 Mock）。第 2.3 章 `test_m02.py` 里有一段注释说的就是这件事：弱测试必须写 `m.parse_guess`，写成 `from ... import parse_guess` 的话，替换对它不起作用

**规则：需要看到最新值的，用 `import 模块` 然后写 `模块.名字`。**

## 7. 循环导入

`lab/cyc/` 里两个模块互相导入：

```python
# cyc/a.py                       # cyc/b.py
from cyc.b import foo            from cyc.a import bar

def bar():                       def foo():
    return "bar"                     return "foo"
```

```text
  $ (lab/) python -c import cyc.a
      Traceback (most recent call last):
        ...
        File "<lab>\cyc\a.py", line 1, in <module>
          from cyc.b import foo
        File "<lab>\cyc\b.py", line 1, in <module>
          from cyc.a import bar
      ImportError: cannot import name 'bar' from partially initialized module 'cyc.a'
      (most likely due to a circular import) (<lab>\cyc\a.py)
```

按第 1 节的三步走一遍：

1. 导入 `cyc.a`：先在 `sys.modules` 里登记一个**空的** `cyc.a`，然后开始执行 `a.py`
2. `a.py` 第一行要导入 `cyc.b`：登记空的 `cyc.b`，开始执行 `b.py`
3. `b.py` 第一行要从 `cyc.a` 里拿 `bar`。`cyc.a` 已经在 `sys.modules` 里了，不会再执行一遍，但它**才执行到第一行，`bar` 还没定义**

报错里的 **partially initialized module**（初始化了一半的模块）说的就是第 3 步的状态。

> 第 1.4 章见过同样的措辞：Python 3.11 遇到「自己的 `random.py` 遮蔽标准库」时，
> 也报 `partially initialized module 'random' ... (most likely due to a circular import)`。
> 区分方法是**看报错末尾括号里的文件路径**。路径是你的项目文件、而模块名是标准库的名字，那就是遮蔽，不是循环导入。

### 三种解法

**解法 1：把两边都要用的东西挪到第三个模块。** `a` 和 `b` 都导入 `common`，`common` 不导入它们。**这是唯一真正消除了循环的解法。** 两个模块互相需要对方，通常说明职责划分有问题，第 3.3 章会讲怎么划分。

**解法 2：把 `import` 挪进函数体里。** 函数体在调用时才执行，导入阶段不会走到那一行，循环在导入阶段就不存在了。依赖关系还在，只是推迟了。

**解法 3：改成 `import 模块` 的形式。** `lab/cyc2/` 就是这样写的：

```python
# cyc2/a.py                      # cyc2/b.py
import cyc2.b                    import cyc2.a

def bar():                       def foo():
    return "bar"                     return "foo+" + cyc2.a.bar()

def call_foo():
    return cyc2.b.foo()
```

```text
  $ (lab/) python -c import cyc2.a; print(cyc2.a.call_foo())
      foo+bar
```

能跑。`import cyc2.a` 只要求 `cyc2.a` 这个模块对象存在（它已经在 `sys.modules` 里，哪怕是空的），不要求里面已经有 `bar`。等到 `call_foo()` 被调用时，两个模块都执行完了，`cyc2.a.bar` 早就有了。

**但循环还在。** 只要有人在 `b.py` 的顶层写一句 `cyc2.a.bar()`，它就会立刻坏掉。练习 4 写的检测器会把 `cyc2` 也报出来，这是对的。

| 解法 | 循环还在吗 | 什么时候用 |
|---|---|---|
| 1 拆出第三个模块 | **不在了** | **默认用这个** |
| 2 `import` 挪进函数 | 导入阶段不在了 | 依赖确实只在某个函数里用，而且拆分代价大 |
| 3 改成 `import 模块` | **还在** | 不推荐，只是让它暂时不报错 |

### ⚠️ 另一种「执行两次」：`__main__` 被再导入一次

`lab/dual/state.py` 定义了一个类 `Token`，用 `-m` 运行时，它导入 `other.py`，而 `other.py` 又反过来 `from dual.state import Token`：

```python
# dual/state.py
print(f"[state.py 被执行  __name__={__name__}]")

class Token:
    pass

if __name__ == "__main__":
    from dual import other
    t = Token()
    print("isinstance(t, other.Token) =", isinstance(t, other.Token))
```

```text
  $ (lab/) python -m dual.state
      [state.py 被执行  __name__=__main__]
      [state.py 被执行  __name__=dual.state]
      isinstance(t, other.Token) = False
```

**同一个文件执行了两次**，生成了两个毫不相干的 `Token` 类。原因是 `sys.modules` 按**名字**缓存：运行的那份登记为 `'__main__'`，`other.py` 要的是 `'dual.state'`，缓存里没有，于是又执行了一遍。

这不是循环导入报错，**它不报任何错**。表现是 `isinstance` 莫名其妙地返回 `False`、模块里的全局变量「改了又没改」。

包的 `__init__.py` 先导入了某个模块、你又用 `-m` 运行这个模块时，Python 会给一条警告：

```text
  $ (lab/) python -m warn.tool
      [tool.py 被执行  __name__=warn.tool]
      [tool.py 被执行  __name__=__main__]
      <frozen runpy>:128: RuntimeWarning: 'warn.tool' found in sys.modules after import
      of package 'warn', but prior to execution of 'warn.tool'; this may result in
      unpredictable behaviour
```

**规则：被当成入口运行的模块，不要再被别的模块导入。** 入口文件（`main.py`）只负责启动，业务代码放在别的模块里。这正是 Day10 三文件拆分的做法，第 3.3 章会继续讲。

## 8. 包、`__init__.py` 与遮蔽

**包**是一个目录，里面放模块。目录里有 `__init__.py` 的叫**常规包**，`__init__.py` 可以是空文件。

`lab/ns/` 没有 `__init__.py`，照样能导入：

```text
  $ (lab/) python -c import ns.mod, ns; print('ns.__file__ =', ns.__file__)
      ns.__file__ = None
```

这叫**命名空间包**（Python 3.3+）。它是为「一个包分散在多个目录里」这种场景设计的，`__file__` 是 `None`。**这门课的每个包目录都放 `__init__.py`**，包的边界明确，所有工具都能正确识别。

### 遮蔽的完整规则

第 1.4 章讲过：当前目录的 `random.py` 会遮蔽标准库。这里补全三条规则，都实测过：

**一、有 `__init__.py` 的同名目录也会遮蔽。** 当前目录有 `json/__init__.py`，`import json` 导入的就是它。

**二、没有 `__init__.py` 的同名目录不会遮蔽。** 当前目录有一个 `logging/` 文件夹（里面没有 `__init__.py`），`import logging` 拿到的仍然是标准库。原因是命名空间包优先级最低：Python 扫描 `sys.path` 时遇到这样的目录只是先记下来，后面的目录里只要有真正的模块或常规包，就用后者。

**三、被遮蔽的模块可能不是你导入的那个。** 当前目录有一个空的 `string.py`，然后 `import logging`：

```text
Python 3.13：
    ImportError: cannot import name 'Template' from 'string' (consider renaming
    '...\string.py' since it has the same name as the standard library module
    named 'string' and prevents importing that standard library module)

Python 3.11：
    ImportError: cannot import name 'Template' from 'string' (...\string.py)
```

你导入的是 `logging`，出错的却是 `string`：标准库的 `logging` 内部写了 `from string import Template`，它拿到了你的 `string.py`。3.13 会提示改名，3.11 只给一个路径。

同样的事情发生在 pytest 身上：

```text
  $ (lab/shadow/) python -m pytest --version
      ImportError: cannot import name 'Random' from 'random' (consider renaming
      '<lab>\shadow\random.py' since it has the same name as the standard library module
      named 'random' and prevents importing that standard library module)
```

**`shadow/` 里只有一个空的 `random.py`，`python -m pytest` 连启动都启动不了。** pytest 启动时会导入标准库的 `tempfile`，`tempfile` 内部要 `from random import Random`。

> 练习 2 要写的遮蔽检查器用 `sys.stdlib_module_names`（Python 3.10+）列出全部标准库模块名。
> 实测它**不包含 `test`**（官方文档说明它不列测试模块），但标准库里确实有一个 `test` 包。
> 所以 `test.py` 要单独检查。

## 9. `pytest` 和 `python -m pytest`

`lab/tests/test_lab.py` 只有一行导入：`from app import util`。在 `lab/` 下用两种方式跑：

```text
  $ (lab/) pytest tests -q
      E   ModuleNotFoundError: No module named 'app'
      1 error in 0.17s
      → 退出码 2

  $ (lab/) python -m pytest tests -q
      1 passed in 0.02s
      → 退出码 0
```

区别还是 `sys.path`：

| 命令 | 加进 `sys.path` 的目录 |
|---|---|
| `pytest` | 测试文件所在的目录 `lab/tests/`（因为 `tests/` 里没有 `__init__.py`） |
| `python -m pytest` | 上面那个，**再加上当前目录 `lab/`**（`-m` 的作用） |

`pytest` 要导入 `test_lab.py`，就得先把它所在的目录放进 `sys.path`（这是 pytest 默认的 `prepend` 导入模式）。当前目录它不管，所以 `app` 找不到。

### 这门课的代码仓就是这样

在 `code/` 目录下，**没有执行过 `pip install -e`** 的环境里：

```text
$ pytest tests/test_m00.py -q
    from m00_setup import check_env
E   ModuleNotFoundError: No module named 'm00_setup'

$ python -m pytest tests/test_m00.py -q
17 passed in 0.68s
```

**这就是 `code/README.md` 第 2 步要求 `pip install -e ".[dev]"` 的原因。** 可编辑安装把 `code/` 登记进了 `site-packages`，`m00_setup`、`m01_basics` 这些包从任何目录都能导入，直接敲 `pytest` 也就没问题了。

三种解决办法，效果一样：

| 办法 | 做法 |
|---|---|
| **可编辑安装**（这门课用的） | `pip install -e ".[dev]"`，一次就好 |
| 用 `python -m pytest` | 每次都要在 `code/` 下这样敲 |
| 让 pytest 自己加路径 | `pyproject.toml` 的 `[tool.pytest.ini_options]` 里写 `pythonpath = ["."]`（实测有效） |

> **第 0.2 章的环境自检要补一句说明。** `check_env.py` 里「课程模块都可导入」这一项，
> 在 `code/` 下用 `python -m m00_setup.check_env` 运行时，**没做 `pip install -e` 也会通过**，
> 因为 `-m` 已经把 `code/` 放进了 `sys.path`。所以它通过只说明「在 `code/` 下用 `python -m` 没问题」。
> 配套代码里那句注释已经改正。

## 10. 这门课代码仓的结构约定

把这一章的规则落到代码仓上：

```text
code/                          ← 永远在这里运行命令
├── pyproject.toml
├── m03_structure/             ← 每个包都有 __init__.py
│   ├── __init__.py
│   ├── ch03_01_example.py     ← 只用绝对导入：from m03_structure.xxx import ...
│   └── ...
└── tests/                     ← 没有 __init__.py，pytest 把它加进 sys.path
    └── test_m03.py
```

| 约定 | 原因 |
|---|---|
| 在 `code/` 下用 `python -m 包.模块` 运行 | `sys.path[0]` 是 `code/`，所有包都找得到 |
| 只用绝对导入 | 任何运行方式都一样；读代码的人知道它来自哪 |
| 每个包目录都有 `__init__.py` | 不依赖命名空间包；不会出现「同名目录遮蔽了没有」的疑问 |
| 文件名不用标准库和已装第三方库的名字 | 第 8 节 |
| 入口模块不被别人导入 | 第 7 节的「执行两次」 |
| `pip install -e ".[dev]"` | 直接敲 `pytest` 也能导入课程的包 |

`ch03_01_solution.py` 用练习 3、4 的两个函数扫描了整个代码仓：

```text
$ python -m m03_structure.ch03_01_solution
lab/ 里的循环： ['cyc.a', 'cyc.b', 'cyc.a']
去掉 cyc 包以后： ['cyc2.a', 'cyc2.b', 'cyc2.a']
lab/ 里会遮蔽标准库的名字： [] ['random']
课程代码仓（44 个模块）里的循环： None
```

---

# 二、动手练习

打开 `ch03_01_exercise.py`。

## 练习 1（基础）· 先猜，再验证

`ch03_01_example.py` 里的 `LAB_FILES` 就是 `lab/` 的全部文件。**先读懂每个文件写了什么，不要先跑示例**，然后判断 12 条命令的结果：

```python
PREDICTIONS = {
    "lab/ 下：python app/main.py": None,
    "lab/ 下：python -m app.main": None,
    "lab/ 下：python -m app.main.py": None,
    ...
    "lab/ 下：pytest tests": None,
    "lab/ 下：python -m pytest tests": None,
    "lab/shadow/ 下：python -m pytest --version": None,
}
```

成功填 `"OK"`，失败填**最后报出的那个异常名**。测试会现场搭一遍 `lab/`，把每条命令真的跑一遍来判分。

每一条都用同一个方法推：**这次启动，`sys.path` 里有哪些目录？要导入的名字在那些目录下吗？**

## 练习 2（基础）· 遮蔽检查器

写 `find_shadowing(directory, extra=())`，找出一个目录里会遮蔽标准库的名字：

```python
find_shadowing(Path("."))                           # → ["json", "random", "test"]
find_shadowing(Path("."), ("requests", "pytest"))   # → ["json", "random", "requests", "test"]
```

- 只看这一层，不递归
- 检查 `*.py` 文件和**含 `__init__.py`** 的子目录
- 跳过 `__` 开头的名字（`__init__.py`、`__main__.py`）
- 名字在 `sys.stdlib_module_names` 里、是 `"test"`、或在 `extra` 里，就算遮蔽

测试准备的目录里有 `logging/`（没有 `__init__.py`）和 `notes/string.py`（在子目录里），它们都不该被报出来。

## 练习 3（进阶）· 一个模块在导入时会导入谁

写 `module_imports(source)`，用标准库 `ast` 解析源码，返回它在**导入阶段**会导入的模块名：

```python
module_imports("import os\nfrom m.n import p\nfrom . import x")   # → {"os", "m.n"}
```

- 相对导入（`from . import x`、`from .m import y`）忽略
- **函数体里的 `import` 不算**，它们在调用时才执行（第 7 节解法 2）
- 类体、`if`、`try` 里的都算，它们在导入阶段就会执行

## 练习 4（进阶）· 找出循环依赖

写 `find_cycle(graph)`。`graph` 是「模块 → 它导入的模块集合」，返回其中一个环，没有环返回 `None`：

```python
find_cycle({"a": {"b"}, "b": {"a"}})              # → ["a", "b", "a"]
find_cycle({"a": {"a"}})                          # → ["a", "a"]
find_cycle({"a": {"b"}, "b": set()})              # → None
```

测试不要求环从哪个点开始，只检查**首尾相同、相邻两个之间真的有边**。测试里有一张「菱形」图（a 导入 b 和 c，b、c 都导入 d），`d` 会被走到两次，但它不是环，你的函数不能把它报出来。

做完以后，运行 `python -m m03_structure.ch03_01_solution` 看看参考答案怎么把练习 3、4 组合起来扫描整个代码仓。

## 怎么验证

```powershell
pytest tests/test_m03.py -k ch03_01 -v
```

---

# 三、常见错误

| # | 错误 | 表现 | 怎么避免 |
|---|---|---|---|
| **1** | **用文件路径运行包里的模块** | `ModuleNotFoundError: No module named 'app'` | 在项目根目录用 `python -m 包.模块` |
| **2** | **裸导入 `from util import ...`** | 换个目录运行就 `ModuleNotFoundError` | 写完整的包路径 |
| **3** | 用文件路径运行有相对导入的模块 | `ImportError: attempted relative import with no known parent package` | 用 `-m`，或改成绝对导入 |
| **4** | **`python -m app.main.py`** | 报错，**但 `main.py` 已经执行过一遍** | `-m` 后面用点分隔、不带 `.py` |
| **5** | **`from config import LEVEL` 后期待看到变化** | 一直是导入那一刻的旧值，不报错 | `import config` 再写 `config.LEVEL` |
| **6** | `from` 形式的循环导入 | `cannot import name ... from partially initialized module` | 把共用部分拆到第三个模块 |
| **7** | **入口模块又被别人导入** | 文件执行两次，`isinstance` 返回 `False`，不报错 | 入口只启动，不被导入 |
| **8** | **文件或目录和标准库同名** | 报错的可能是另一个模块，比如 `string.py` 让 `import logging` 失败 | 练习 2 的检查器；`json/` 这种带 `__init__.py` 的目录同样算 |
| **9** | **没装 `-e` 就直接敲 `pytest`** | `ModuleNotFoundError: No module named 'm00_setup'` | `pip install -e ".[dev]"` |
| **10** | 业务模块顶层写了启动代码 | 别人一导入就启动了程序 | 启动代码放进 `if __name__ == "__main__":` |

**第 5、7 条最难查**，它们都不报错。第 5 条表现为「改了配置没生效」，第 7 条表现为「明明是同一个类，`isinstance` 却不认」。

**第 8 条的提示信息与版本有关。** 3.13 会提示你改名；3.11 要么只给一个路径，要么（第 1.4 章）误导你去查循环导入。

---

# 四、本章小结

```text
import X 做三件事：找到 → 执行一遍 → 绑定名字
   └─ 执行过的存进 sys.modules，按名字缓存，同名不再执行
        ↓
去哪找：sys.path，第一个找到的就用
   └─ sys.path[0] 取决于启动方式
        python 文件路径   → 脚本所在目录
        python -m 模块名  → 当前目录（这门课的约定）
        pytest           → 测试文件所在目录，不含当前目录 ⚠️
        ↓
__name__：被运行时是 '__main__'，被导入时是模块名
   └─ pytest 是导入，所以 if __name__ 块不执行
        ↓
三种导入：绝对（默认用）/ 相对（需要 __package__）/ 裸（别用）
        ↓
⚠️ from X import 名字 = 拷一份引用，看不到之后的变化
⚠️ 循环导入：partially initialized → 拆出第三个模块
⚠️ 入口模块被再导入 → 同一文件执行两次，不报错
⚠️ 遮蔽：同名 .py 和带 __init__.py 的目录都会，报错的可能是别的模块
```

一句话总结：**判断一条 `import` 会不会成功，只需要问一个问题：这次启动，`sys.path` 里有哪些目录？**

## 下一章

[3.2 类与面向对象](03_02_类与面向对象.md) —— 第 1.6 章的 `play()` 里有一组变量：答案、次数上限、猜过的数。它们总是一起出现、一起传来传去。下一章把它们和操作它们的函数放进一个类里，并讲清楚类属性、`dataclass`、继承各自的坑。

---

# 五、自测

1. `import app.util` 做了哪三件事？为什么说「`import` 不是把函数抠出来」？
2. 同一个进程里 `import app.util` 写两遍，`util.py` 的顶层代码执行几次？为什么？
3. 导入 `app.util` 时，`app/__init__.py` 会执行吗？
4. 删掉 `gone.py` 后，`__pycache__` 里的 `gone.cpython-313.pyc` 还在，`import gone` 能成功吗？
5. `python app/main.py`、`python -m app.main`、`python -c "..."` 三种方式下，`sys.path[0]` 分别是什么？
6. 在 `lab/` 下运行 `python app/main.py`，里面的 `from app import util` 为什么失败？
7. `__name__` 在「用文件路径运行」「用 `-m` 运行」「被导入」三种情况下分别是什么？`__package__` 呢？
8. 断言写在 `if __name__ == "__main__":` 里，pytest 为什么收集不到？
9. `python -m app.main.py` 会发生什么？为什么说它比 `python -m app/main.py` 更危险？
10. 相对导入 `from .util import VALUE` 在什么情况下报 `attempted relative import with no known parent package`？
11. Day10 的 `from game_logic import check_num` 为什么在 `Day10/` 里能跑、在项目根目录跑 pytest 就失败？
12. `from snap.config import LEVEL` 之后调用 `set_level("DEBUG")`，`LEVEL` 是什么？为什么？
13. 循环导入的报错里 `partially initialized module` 是什么意思？按三步走一遍 `cyc.a` 的导入过程。
14. 循环导入的三种解法里，哪一种真正消除了循环？`cyc2` 那种写法为什么能跑？
15. `python -m dual.state` 为什么会让 `state.py` 执行两次？这会造成什么现象？
16. 当前目录有一个没有 `__init__.py` 的 `logging/` 文件夹，会遮蔽标准库的 `logging` 吗？有 `__init__.py` 的 `json/` 呢？
17. 当前目录有 `string.py`，为什么 `import logging` 会失败？
18. `pytest` 和 `python -m pytest` 在 `sys.path` 上有什么区别？这门课的代码仓为什么要 `pip install -e`？

<details>
<summary>参考答案</summary>

1. **找到**模块文件（搜索 `sys.path`）、**执行**整个文件、把模块对象**绑定**到当前命名空间的名字上。因为第 2 步会把整个文件从头到尾执行一遍，顶层的每一行都会运行。
2. **一次。** 执行完的模块存进 `sys.modules`，再次 `import` 同一个名字时直接从缓存取，不再执行文件。
3. **会，而且先于 `util.py` 执行。** 导入包里的任何子模块，都会先执行这个包的 `__init__.py`。
4. **不能**，报 `ModuleNotFoundError: No module named 'gone'`。`__pycache__` 里的缓存只在源文件存在时才会被使用。
5. 分别是**脚本所在的目录**（`lab/app/`）、**当前工作目录**（`lab/`）、**空字符串** `''`（也代表当前目录）。
6. 用文件路径运行时 `sys.path[0]` 是 `lab/app/`，Python 在 `lab/app/` 里找叫 `app` 的模块或包，找不到。`lab/` 不在 `sys.path` 里。
7. 文件路径运行：`'__main__'`，`__package__` 是 `None`；`-m` 运行：`'__main__'`，`__package__` 是包名 `'app'`；被导入：模块完整名字 `'app.who'`，`__package__` 是 `'app'`。
8. pytest 是**导入**测试文件，导入时 `__name__` 是模块名而不是 `'__main__'`，整个块被跳过。
9. 它把 `app.main.py` 理解成「`app.main` 包下的 `py` 子模块」，于是**先把 `app.main` 当普通模块导入（完整执行了一遍）**，然后才因为 `app.main` 不是包而报错。如果 `main.py` 顶层有副作用，这些副作用已经发生了。`python -m app/main.py` 在找模块阶段就失败，什么都没执行。
10. 用文件路径直接运行这个模块的时候。这时 `__package__` 是 `None`，模块不知道自己属于哪个包，「相对于当前包」无从谈起。
11. 在 `Day10/` 里运行时，`sys.path[0]` 就是 `Day10/`，`game_logic.py` 正好在那里；从项目根目录跑 pytest 时，`sys.path` 里没有 `Day10/`，裸导入找不到。
12. **还是 `"INFO"`。** `from snap.config import LEVEL` 等价于 `LEVEL = snap.config.LEVEL`，在当前模块新建了一个名字指向那一刻的对象。之后 `config` 里的 `LEVEL` 改指向别的对象，不影响这个名字。要看到变化，写 `snap.config.LEVEL`。
13. 意思是「这个模块已经在 `sys.modules` 里登记了，但还没执行完」。过程：导入 `cyc.a`，登记并开始执行 `a.py` → 第一行导入 `cyc.b`，登记并开始执行 `b.py` → `b.py` 第一行要从 `cyc.a` 拿 `bar`，`cyc.a` 已登记所以不重新执行，但它才执行到第一行，`bar` 还不存在 → `ImportError`。
14. **只有「拆出第三个模块」真正消除了循环。** `cyc2` 用 `import cyc2.b` 的形式，只要求模块对象存在、不要求里面已经有某个名字；属性要等到函数被调用时才访问，那时两个模块都执行完了。但循环依然存在，顶层一旦用到对方的属性就会坏。
15. `sys.modules` 按名字缓存。用 `-m` 运行的那份登记为 `'__main__'`，`other.py` 导入的是 `'dual.state'`，缓存里没有，于是又执行了一遍。结果是两个毫不相干的 `Token` 类，`isinstance` 返回 `False`，而且不报任何错。
16. 没有 `__init__.py` 的 `logging/` **不会**遮蔽：它只是命名空间包的候选，后面找到标准库的常规包就用后者。有 `__init__.py` 的 `json/` **会**遮蔽。
17. 标准库的 `logging` 内部写了 `from string import Template`，它找到的是你的 `string.py`，里面没有 `Template`。出错的模块不是你直接导入的那个。
18. `pytest` 只把测试文件所在目录（`tests/`）加进 `sys.path`；`python -m pytest` 还会把当前目录加进去。代码仓的测试要 `from m00_setup import ...`，没做可编辑安装时直接敲 `pytest` 就找不到。`pip install -e` 把 `code/` 登记进 `site-packages`，从哪里运行都能导入。

</details>
