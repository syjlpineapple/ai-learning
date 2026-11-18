# Day 02 · 随机数与模块导入

> **学习日** 2026-10-17（09:33 - 09:39，2 轮对话）
> **对应代码** [`dailypractice/Day2.py`](../../dailypractice/Day2.py)
> **原始对话** `courseware/_raw/markdown/01_Python每日练习出题.md`（对话里称「Day 3」）

## 本节掌握

- `import random` 与 `from random import randint` 两种导入方式的区别
- `random.randint(a, b)` 生成闭区间 `[a, b]` 内的随机整数
- f-string：`f"随机数：{x}"`
- 为什么随机数要生成在循环外面
- 字符串和整数不能直接比大小

---

# 第一部分 · 知识讲解

## 1. 模块：为什么需要，怎么用

一个 `.py` 文件就是一个**模块**。模块的意义是：把代码分到不同文件里，需要时再取用，而不是把所有东西堆在一个文件。

Python 的能力大部分来自模块：

| 来源 | 说明 | 例子 |
|---|---|---|
| **内置函数** | 不用导入，直接用 | `print()`、`len()`、`int()` |
| **标准库** | 随 Python 安装，`import` 即可 | `random`、`json`、`os`、`logging` |
| **第三方库** | 需要 `pip install` | `requests`、`numpy` |
| **自己的模块** | 自己写的 `.py` 文件 | Day10 会学 |

**标准库不用装，第三方库要装**——这个区别很实际：`import random` 永远能用，`import requests` 在新环境里会报 `ModuleNotFoundError`。

## 2. `import` 的几种形式

这是本节最重要的知识点，四种写法含义不同：

```python
# ① 导入整个模块，用的时候带模块名
import random
random.randint(1, 100)

# ② 只导入模块里的某个成员，用的时候不带模块名
from random import randint
randint(1, 100)

# ③ 导入并起别名
import numpy as np
np.array([1, 2, 3])

# ④ 导入模块里的所有成员（不推荐）
from random import *
randint(1, 100)
```

| 写法 | 之后怎么用 | 适用 |
|---|---|---|
| `import X` | `X.成员` | **推荐默认用这个**——看得出函数来自哪 |
| `from X import Y` | `Y` | 只用少数几个成员、名字不会冲突时 |
| `import X as Y` | `Y.成员` | 模块名太长，或社区有约定别名（`np`、`pd`） |
| `from X import *` | 直接用 | **不要用**——不知道引入了哪些名字，容易覆盖已有变量 |

### 混用的陷阱

**搞混 ① 和 ② 是本节的核心坑。** 关键是看清「你导入的到底是模块还是成员」：

```python
from random import random       # 导入的是 random 模块里的 random 函数
random.randint(1, 100)          # AttributeError：函数没有 randint 方法
```

`random` 这个名字恰好既是**模块名**又是该模块里一个**函数名**（`random()` 返回 0~1 的浮点数）。所以上面这行导入的是函数，不是模块。

判断方法：**`from A import B` 之后，`B` 就是你导入的那个东西本身，不能再用 `B.` 去访问它的「兄弟」。**

## 3. `random` 模块常用函数

```python
import random

random.randint(1, 100)            # 1~100 的随机整数，两端都包含
random.random()                   # 0.0 ~ 1.0 的随机浮点数
random.choice(["a", "b", "c"])    # 从序列里随机选一个
random.shuffle(my_list)           # 原地打乱列表（返回 None，不是新列表）
random.sample(range(100), 5)      # 不重复地随机取 5 个
```

**`randint(a, b)` 是闭区间**，两端都能取到。这点要和 `range()` 区分开：

```python
random.randint(1, 100)     # 可能取到 1，也可能取到 100
range(1, 100)              # 1 到 99，取不到 100
```

**容易混的两个边界约定**，Python 里 `range`、切片都是「左闭右开」，而 `randint` 是例外。

> 随机数其实是**伪随机**：由一个种子（seed）通过算法推算出来。`random.seed(42)` 可以固定种子，让每次运行产生相同的序列——这在**测试**里很有用（让随机行为变得可重现）。

## 4. 字符串格式化：三代写法

把变量嵌进字符串里，Python 历史上有三种方式：

```python
name, age = "Tom", 25

# ① % 格式化（最老，C 风格）
"我叫 %s，今年 %d 岁" % (name, age)

# ② str.format()（Python 2.6+）
"我叫 {}，今年 {} 岁".format(name, age)
"我叫 {n}，今年 {a} 岁".format(n=name, a=age)

# ③ f-string（Python 3.6+，推荐）
f"我叫 {name}，今年 {age} 岁"
```

**现在一律用 f-string**：最短、最直观，变量就写在它该出现的位置，性能也最好。

### f-string 的关键是开头那个 `f`

```python
f"随机数：{num}"      # 正确：num 被替换成值
"随机数：{num}"       # 错误：原样输出 {num} 这几个字符
```

**漏掉 `f` 不会报错**，只是花括号和变量名被原样打印——这种 bug 要靠看输出才能发现。

### 另一个坑：`{}` 不是 `print` 的功能

```python
print("随机数：{}", num)       # 输出：随机数：{} 56
```

这行把 `"随机数：{}"` 和 `num` 当成 `print` 的两个参数，`{}` 不会被替换。`{}` 占位符属于 `str.format()`，单独写在字符串里对 `print` 没有意义。

### f-string 的进阶用法

```python
f"{3.14159:.2f}"        # '3.14'      保留两位小数
f"{1234567:,}"          # '1,234,567' 千位分隔符
f"{0.85:.1%}"           # '85.0%'     百分比
f"{42:>8}"              # '      42'  右对齐，宽度 8
f"{name!r}"             # "'Tom'"     用 repr() 而不是 str()
f"{x + y}"              # 可以直接写表达式
f"{x=}"                 # 'x=10'      Python 3.8+，调试神器
```

`f"{x=}"` 这个写法在排查时很好用——它会同时打印变量名和值，不用自己写 `f"x={x}"`。

## 5. `print()` 的参数

```python
print("a", "b", "c")                    # a b c        默认用空格分隔
print("a", "b", sep="-")                # a-b          改分隔符
print("a", end="")                      # 不换行
print("错误信息", file=sys.stderr)        # 输出到标准错误
```

默认 `sep=" "`、`end="\n"`。所以 `print("随机数：", num)` 的输出是 `随机数： 56`——中间**有一个空格**，因为那是两个参数。想紧贴着就用 f-string。

## 6. 注释

```python
# 单行注释

"""
多行字符串，常被当作注释用。
放在模块、函数、类开头时叫 docstring，是正式的文档（Day16 会学）。
"""
```

注释该写什么：**写「为什么」，不写「是什么」**。

```python
x = x + 1                      # 把 x 加一        ← 废话，代码本身就说了
random_num = random.randint(1, 100)   # 放在循环外，否则每轮答案都会变   ← 有价值
```

学习阶段有个例外值得保持：**把尝试过的其他写法留成注释**，回头看能想起当时在对比什么。

## 7. 变量定义的位置很重要

```python
# 正确：答案在循环外生成一次
random_num = random.randint(1, 100)
while True:
    guess = input("猜：")
    ...

# 错误：每轮循环都重新抽一个答案
while True:
    random_num = random.randint(1, 100)     # ← 答案一直在变，永远猜不中
    guess = input("猜：")
```

规律：**需要在多轮之间保持不变、或者需要累积的东西，都必须定义在循环外面。** 写在循环里就等于每轮重置。

这条规律在后面反复出现：计数器 `count`（Day03）、历史记录列表（Day05）都是同一个道理。

---

# 第二部分 · 当天的练习

## 一、题目

把 Day 01 的猜数字改成真正的游戏：答案由程序随机生成 1~100 的整数，而不是固定的 10。

## 二、第一版：三个错误

当时的写法（报错）：

```python
from random import random

random_num = random.randint(1, 100)
print("随机数：{}", random_num)
while True:
    input_num = input("请输入数字")
    if input_num > random_num:
        print("猜大了")
    ...
```

思路是对的——**`random_num` 放在 `while` 外面**，这点很关键，否则每轮循环都重新抽一个答案，永远猜不中。但有三处错误。

### 坑 1：导入的是函数，不是模块

```python
from random import random      # 导入的是 random 模块里的 random 函数
random_num = random.randint(1, 100)   # 函数没有 .randint 方法 → AttributeError
```

`random` 这个名字同时是**模块名**和该模块里一个**函数名**（`random()` 返回 0~1 的浮点数）。`from random import random` 导入的是那个函数，它当然没有 `randint` 方法。

两种正确写法，选一种：

```python
# 写法 A：导入整个模块，用的时候带模块名（推荐，看得出来函数是哪来的）
import random
random_num = random.randint(1, 100)

# 写法 B：只导入需要的函数，用的时候不带模块名
from random import randint
random_num = randint(1, 100)
```

> 规律：`import X` 之后用 `X.成员`；`from X import Y` 之后直接用 `Y`。两者混用就会出现「以为导入了模块，其实导入了函数」。

### 坑 2：`{}` 占位符不会自动替换

```python
print("随机数：{}", random_num)
```

输出是 `随机数：{} 56`——`{}` 被原样打印了，`random_num` 被当成 `print` 的第二个参数。

`{}` 这种占位符属于 `str.format()`，不是 `print` 的功能。三种正确写法：

```python
print("随机数：", random_num)              # 逗号分隔，print 自动加空格
print(f"随机数：{random_num}")             # f-string，推荐
print("随机数：{}".format(random_num))     # str.format
```

**f-string 的关键是开头那个 `f`**。没有 `f` 的 `"随机数：{random_num}"` 会原样输出大括号和里面的变量名。

### 坑 3：字符串和整数比大小

```python
input_num = input("请输入数字")   # 这是 str
if input_num > random_num:       # str > int → TypeError
```

这个坑 Day 01 已经踩过（`input()` 永远返回字符串），这里又犯了一次。说明「知道」和「写代码时记得」是两件事。

比较前必须转换：`input_num = int(input("请输入数字:"))`。

## 三、最终代码

```python
import random

random_num = random.randint(1, 100)
print("随机数：", random_num)
# 或者print(f"随机数：{random_num}")
while True:
    input_num = int(input("请输入数字:"))
    if input_num > random_num:
        print("猜大了")
    elif input_num < random_num:
        print("猜小了")
    else:
        print("猜对了")
        break
```

这一版能正常跑完整局游戏。注意第 4 行把另一种写法留成了注释——这个习惯在学习阶段值得保持，回头看能想起当时在对比什么。

遗留问题（下一节解决）：`int()` 直接套在 `input()` 外面，用户输入 `abc` 或 `q` 时程序会崩在 `ValueError` 上。Day 01 做过的输入校验，在这一版里丢了。

> 调试用的 `print("随机数：", random_num)` 正式游戏里要删掉——答案都打出来了还猜什么。学习阶段留着方便验证逻辑。

## 四、复习自测

1. `from random import random` 和 `import random` 分别导入了什么？前者为什么不能调 `randint`？
2. `print("值：{}", x)` 会输出什么？想用占位符该怎么写？
3. `random_num = random.randint(1, 100)` 写在 `while` 里面会怎样？
4. `random.randint(1, 100)` 能取到 100 吗？

<details>
<summary>参考答案</summary>

1. 前者导入的是 `random` 模块里名为 `random` 的**函数**（返回 0~1 的浮点数），它没有 `randint` 方法，调用会抛 `AttributeError`；后者导入整个**模块**，可以用 `random.randint()`。
2. 输出 `值：{}` 后面跟一个空格和 x 的值，`{}` 被原样打印。要用占位符得写 `f"值：{x}"` 或 `"值：{}".format(x)`。
3. 每轮循环都会重新抽一个答案，上一次的提示全部作废，游戏永远赢不了。
4. 能。`randint(a, b)` 是**闭区间**，两端都包含。这和 `range(a, b)` 不含 b 不一样，容易混。

</details>
