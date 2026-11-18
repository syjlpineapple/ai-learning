# Day 05 · 列表与数据记录

> **学习日** 2026-10-19（09:21 - 09:26，2 轮对话）
> **对应代码** [`dailypractice/Day5.py`](../../dailypractice/Day5.py)
> **原始对话** `courseware/_raw/markdown/01_Python每日练习出题.md`（对话里称「第 6 天」）

## 本节掌握

- `[]` 创建空列表，`.append(x)` 追加元素
- 列表要在循环外初始化
- 只把**有效数据**放进列表
- `continue` 跳过本轮循环，进入下一轮
- 提示语必须和实际校验规则一致

---

# 第一部分 · 知识讲解

## 1. 列表：有序、可变的容器

前四天只用过单个值的变量。列表让一个变量能装**多个有序的值**：

```python
guesses = [23, 50, 42]
```

三个特点：

- **有序**——元素有固定位置，顺序不会自己变
- **可变**——可以增删改
- **元素类型不限**——`[1, "a", True, [2, 3]]` 完全合法（但实践中通常保持同一类型）

## 2. 创建与访问

```python
items = []                  # 空列表
items = [1, 2, 3]
items = list("abc")         # ['a', 'b', 'c']
items = [0] * 5             # [0, 0, 0, 0, 0]
```

### 索引从 0 开始

```python
items = [10, 20, 30, 40]

items[0]        # 10   第一个
items[3]        # 40   第四个
items[4]        # IndexError: list index out of range
```

**长度为 n 的列表，合法索引是 0 到 n-1。** 用 `items[len(items)]` 一定越界——这是最常见的 off-by-one 错误。

### 负索引从末尾倒数

```python
items[-1]       # 40   最后一个
items[-2]       # 30   倒数第二
```

`items[-1]` 是取最后一个元素的标准写法，比 `items[len(items) - 1]` 简洁。

## 3. 切片

```python
items = [10, 20, 30, 40, 50]

items[1:3]      # [20, 30]      从 1 到 3（不含 3）
items[:3]       # [10, 20, 30]  从头到 3
items[2:]       # [30, 40, 50]  从 2 到尾
items[:]        # 全部（这是个浅拷贝）
items[::2]      # [10, 30, 50]  步长 2
items[::-1]     # [50, 40, 30, 20, 10]  反转
```

**切片是左闭右开**：`items[1:3]` 包含索引 1、2，不含 3。这和 `range(1, 3)` 一致，但和 `random.randint(1, 3)`（闭区间）不一致——Python 里大部分「范围」都是左闭右开，`randint` 是例外。

切片的两个实用特性：

- **不会越界报错**：`items[10:20]` 返回 `[]`，不抛 `IndexError`
- **返回新列表**：改切片结果不影响原列表

## 4. 常用方法

```python
items = [1, 2, 3]

items.append(4)           # [1, 2, 3, 4]        末尾加一个元素
items.extend([5, 6])      # [1, 2, 3, 4, 5, 6]  末尾加多个
items.insert(0, 0)        # [0, 1, 2, ...]      在指定位置插入
items.remove(3)           # 删除第一个值为 3 的元素，没有则 ValueError
items.pop()               # 删除并返回最后一个
items.pop(0)              # 删除并返回索引 0 的元素
items.clear()             # 清空
```

### `append` 和 `extend` 的区别

```python
a = [1, 2]
a.append([3, 4])          # [1, 2, [3, 4]]   ← 整个列表作为一个元素
a = [1, 2]
a.extend([3, 4])          # [1, 2, 3, 4]     ← 逐个加进去
```

### 这些方法大多返回 `None`

```python
items = [3, 1, 2]
result = items.sort()     # result 是 None！列表被原地排序了
print(items)              # [1, 2, 3]
```

**`sort()`、`append()`、`reverse()` 都是「原地修改 + 返回 None」。** 写 `items = items.sort()` 会把列表变成 `None`，这是高频错误。

想要新列表不改原值，用对应的内置函数：

| 原地修改（返回 None） | 返回新对象 |
|---|---|
| `items.sort()` | `sorted(items)` |
| `items.reverse()` | `reversed(items)` 或 `items[::-1]` |

## 5. 可变与不可变

Python 的类型分两大阵营，这个区分非常重要：

| 可变（mutable） | 不可变（immutable） |
|---|---|
| `list`、`dict`、`set` | `int`、`float`、`str`、`tuple`、`bool` |
| 可以原地修改内容 | 任何「修改」都是创建新对象 |

```python
s = "hello"
s[0] = "H"                # TypeError: 'str' object does not support item assignment
s = s.upper()             # 这不是修改，是创建了新字符串并重新绑定
```

所以字符串的所有方法（`upper()`、`strip()`、`replace()`）都**返回新字符串**，不改原值。

### 元组：不可变的列表

```python
point = (1, 2)
point[0] = 5              # TypeError
```

什么时候用元组：**数据不该被改动时**。而且元组可以做字典的键（列表不行，因为键必须不可变）。

## 6. 赋值是引用，不是拷贝

这是列表最容易出错的地方：

```python
a = [1, 2, 3]
b = a                     # b 和 a 指向【同一个】列表
b.append(4)
print(a)                  # [1, 2, 3, 4]  ← a 也变了！
```

`b = a` 不是复制，只是让 `b` 指向同一个对象。想要独立的副本：

```python
b = a[:]                  # 切片
b = a.copy()              # 方法
b = list(a)               # 构造新列表
```

这三种都是**浅拷贝**——只复制一层。嵌套列表仍然共享内层：

```python
a = [[1, 2], [3, 4]]
b = a.copy()
b[0].append(99)
print(a)                  # [[1, 2, 99], [3, 4]]  ← 内层还是共享的
```

要完全独立得用深拷贝：

```python
import copy
b = copy.deepcopy(a)
```

> 为什么不可变类型没有这个问题？因为不可变对象没法原地修改，共享它完全安全。
> 这也是「能用不可变就用不可变」的理由之一。

## 7. 遍历列表

```python
items = ["a", "b", "c"]

# 直接遍历元素（最常用）
for item in items:
    print(item)

# 需要索引时用 enumerate
for i, item in enumerate(items):
    print(i, item)        # 0 a / 1 b / 2 c

# 不要这样写
for i in range(len(items)):
    print(items[i])       # 能用，但不是 Python 风格
```

**`enumerate()` 是需要索引时的标准做法**，比 `range(len(...))` 清楚且不易出错。

### 遍历时不要修改列表

```python
for item in items:
    if item < 0:
        items.remove(item)      # 危险：会跳过元素
```

删除会让后面的元素前移，而迭代器的位置继续前进，结果漏掉元素。正确做法是**建新列表**：

```python
items = [x for x in items if x >= 0]
```

## 8. `in` 运算符

```python
3 in [1, 2, 3]            # True
"a" in "abc"              # True
"x" not in [1, 2]         # True
```

对列表来说 `in` 是逐个比较，长列表会慢（O(n)）。元素多且频繁查找时该用 `set`（O(1)）：

```python
valid = {"development", "testing", "production"}
if env not in valid:
    ...
```

## 9. 列表推导式

一种从旧列表造新列表的简洁写法：

```python
# 传统写法
squares = []
for x in range(5):
    squares.append(x ** 2)

# 列表推导式
squares = [x ** 2 for x in range(5)]       # [0, 1, 4, 9, 16]

# 带条件筛选
evens = [x for x in range(10) if x % 2 == 0]
```

结构是 `[表达式 for 变量 in 可迭代对象 if 条件]`。

**适合简单转换**；逻辑一复杂就该写回普通循环——推导式套两层循环加条件判断会变得没法读。

## 10. 需要跨轮累积的东西都放循环外

```python
guess_history = []            # ← 必须在循环外
count = 0                     # ← 同理

while True:
    ...
    guess_history.append(num)
    count += 1
```

写进循环就等于每轮重置。这条规律在 Day02（随机数）、Day03（计数器）已经出现过两次，这里是第三次。

**判断方法：问自己「这个变量需要记住上一轮的值吗？」** 需要就放外面。

---

# 第二部分 · 当天的练习

## 一、题目

在猜数字游戏里加记录功能：

1. 创建空列表 `guess_history`
2. 每次有效输入后把数字追加进列表
3. 猜中时显示所有猜过的数字
4. 输入 `q` 退出时也显示
5. **无效输入不进列表**

## 二、代码

```python
r_num = random.randint(1, 100)
count = 0
guess_history = []           # ← 循环外初始化
while True:
    i_num = input("请输入数字")
    if i_num == 'q':
        print(f"游戏退出：共输入{count}次")
        print("猜测记录:", guess_history)
        break
    try:
        i_num = int(i_num)
        count += 1
        guess_history.append(i_num)      # ← 转换成功后才记录
        result = check_guess(i_num, r_num)
        print(result)
        if result == "正确":
            print("猜测记录:", guess_history)
            break
    except ValueError:
        print("输入无效，请输入正整数，退出请输入‘q’")
```

这一版一次通过，四个要点都对。

**列表在循环外初始化。** 写进 `while` 里的话每轮都变回空列表，记录永远只有最后一个数字。这和 Day 03 里 `count = 0` 的位置是同一个道理：**需要跨轮次累积的东西，必须在循环外面创建**。

**`append()` 在 `int()` 成功之后。** 输入 `abc` 会跳进 `except`，不会污染列表。顺序是「先转换 → 成功才记录」，和 Day 03 里计数器的处理一致。

**两条退出路径都输出了记录。** 猜中时和输入 `q` 时都打印，符合题目要求。

## 三、两个改进点

### 改进 1：提示语承诺了代码没做的事

提示写「请输入正整数」，但 `-5` 和 `0` 都能通过 `int()` 转换，被记进列表参与比较。

加一道范围校验：

```python
i_num = int(i_num)

if not 1 <= i_num <= 100:
    print("请输入 1 到 100 之间的整数")
    continue              # 直接开始下一轮，不计数、不记录

count += 1
guess_history.append(i_num)
```

`not 1 <= i_num <= 100` 这种**链式比较**是 Python 的特色写法，等价于 `not (1 <= i_num and i_num <= 100)`，比写两个条件清楚。

`continue` 的作用是**跳过本轮剩下的代码，直接进入下一次循环**。和 `break`（结束整个循环）是一对：

| 关键字 | 作用 |
|---|---|
| `continue` | 结束**本轮**，继续下一轮 |
| `break` | 结束**整个循环** |
| `return` | 结束**整个函数** |
| `exit()` | 结束**整个程序** |

这四个的作用范围层层扩大，Day 01 已经混过一次 `break` 和 `exit()`。

### 改进 2：重复代码

`print("猜测记录:", guess_history)` 在两个地方各写了一遍。

这里**不急着改**。两处重复还在可接受范围，而且两条退出路径的提示语本来就可能要分别调整。真正该抽函数的时机是下一节——那时要输出的统计项从 1 项变成 5 项，重复就不能忍了。

> 过早抽象和重复代码一样是问题。判断标准不是「有没有重复」，而是「这段重复会不会一起变化」。

## 四、`count` 和 `len()` 的隐患

这一版同时维护了两个表达同一件事的数据：

```python
count += 1                      # 计数器
guess_history.append(i_num)     # 列表
```

`count` 的值永远等于 `len(guess_history)`。一旦哪天有个分支只做了其中一件，两者就不一致了，而且这种 bug 不会报错，只会表现为「次数显示得不对」。

下一节会把 `count` 整个删掉，直接用 `len(guess_history)`。

## 五、复习自测

1. `guess_history = []` 写在 `while` 里面会怎样？
2. `continue`、`break`、`return`、`exit()` 分别结束什么？
3. `not 1 <= x <= 100` 等价于什么？能写成 `not 1 <= x and x <= 100` 吗？
4. 为什么说同时维护 `count` 和 `guess_history` 是隐患？

<details>
<summary>参考答案</summary>

1. 每轮循环重新变成空列表，最后只剩当前这一次的记录。
2. `continue` 结束本轮循环体、继续下一轮；`break` 结束整个循环；`return` 结束整个函数；`exit()` 终止整个程序。
3. 等价于 `not (1 <= x and x <= 100)`。不能写成 `not 1 <= x and x <= 100`——`not` 的优先级高于 `and`，那样会被理解成 `(not 1 <= x) and (x <= 100)`，含义完全变了。
4. 两个变量表达同一个含义（有效猜测次数），需要同步更新。任何一个分支漏改就会不一致，而且不会报错，只会悄悄显示错误的数字。应该只保留一个数据源，次数用 `len()` 现算。

</details>
