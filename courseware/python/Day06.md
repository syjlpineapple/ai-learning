# Day 06 · 统计函数、控制流与边界条件

> **学习日** 2026-10-19 出题 / 2026-10-20 交作业（10:38、10:50 两版）
> **对应代码** [`dailypractice/Day6.py`](../../dailypractice/Day6.py)
> **原始对话** `courseware/_raw/markdown/01_Python每日练习出题.md`（对话里称「第 7 天」）

## 本节掌握

- `len()` `max()` `min()` `sum()` 四个内置函数
- `f"{avg:.2f}"` 格式化保留两位小数
- **空列表边界**：不能对空列表求 `max()`，也不能除以零
- 守卫语句：用 `return` 提前结束函数
- `not 1 <= x <= 100` 为什么比 `x < 0 or x > 100` 正确
- 精确类型提示 `list[int]`
- 函数名被变量覆盖的坑

这一节是 A 线第一个「坑比知识点多」的日子，交了两版才过。

---

# 第一部分 · 知识讲解

## 1. 四个统计内置函数

```python
items = [30, 70, 50]

len(items)        # 3      元素个数
max(items)        # 70     最大值
min(items)        # 30     最小值
sum(items)        # 150    求和
```

它们都是**内置函数**，不需要导入。注意写法是 `len(items)` 而不是 `items.len()`——这是 Python 的设计选择，这些函数对多种类型都适用（`len()` 能用于列表、字符串、字典、集合）。

### 边界行为

| 调用 | 空列表时 |
|---|---|
| `len([])` | `0`（正常） |
| `sum([])` | `0`（正常） |
| `max([])` | **抛 `ValueError`** |
| `min([])` | **抛 `ValueError`** |

`max()` 和 `min()` 对空序列会报 `ValueError: max() arg is an empty sequence`。这不是 bug——空集合确实没有最大值。要么提前判断，要么给默认值：

```python
max(items, default=0)       # 空列表时返回 0
```

`max()` 还能比较多个参数、能指定比较依据：

```python
max(3, 7, 5)                        # 7
max(words, key=len)                 # 最长的那个词
```

## 2. 除法的三种运算符

```python
7 / 2         # 3.5    真除法，结果【总是】浮点数
7 // 2        # 3      整除，向下取整
7 % 2         # 1      取余
```

**`/` 的结果一定是 `float`，即使能整除**：

```python
6 / 2         # 3.0    ← 不是 3
type(6 / 2)   # <class 'float'>
```

计算平均值用 `/`：

```python
avg = sum(items) / len(items)
```

这里埋着一个边界：**`len(items)` 为 0 时会抛 `ZeroDivisionError`**。

`//` 对负数是**向下取整**（朝负无穷），不是截断：

```python
-7 // 2       # -4    不是 -3
```

## 3. f-string 的格式规格

```python
avg = 50.666666

f"{avg:.2f}"          # '50.67'      保留两位小数（四舍五入）
f"{avg:.0f}"          # '51'         不要小数
f"{avg:10.2f}"        # '     50.67' 总宽度 10，右对齐
f"{avg:<10.2f}"       # '50.67     ' 左对齐
f"{avg:^10.2f}"       # '  50.67   ' 居中
```

格式规格写在冒号后面，基本结构是 `{值:[对齐][宽度][.精度][类型]}`：

| 规格 | 含义 |
|---|---|
| `.2f` | 浮点数，2 位小数 |
| `,` | 千位分隔符，`f"{1234567:,}"` → `1,234,567` |
| `.1%` | 百分比，`f"{0.856:.1%}"` → `85.6%` |
| `>` `<` `^` | 右对齐、左对齐、居中 |
| `08.2f` | 宽度 8，不足补 0 |
| `e` | 科学计数法 |

> `.2f` 做的是**显示层面的四舍五入**，不改变原值。想真的改变数值用 `round(avg, 2)`。
>
> 另外浮点数有精度问题：`round(2.675, 2)` 得到 `2.67` 而不是 `2.68`，因为 2.675 在二进制里存的是略小于它的值。涉及金额计算要用 `decimal.Decimal`。

## 4. 空容器的边界条件

这是本节的核心主题。任何处理集合的代码都要问一句：**集合为空时会怎样？**

```python
def show_statistics(items):
    print("最大值:", max(items))              # 空列表 → ValueError
    print("平均值:", sum(items) / len(items))  # 空列表 → ZeroDivisionError
```

空列表不是罕见情况——用户一次都没猜就退出、第一次运行还没有数据、筛选后什么都没剩下，都会得到空集合。

**这两个异常属于「正常使用中必然会遇到」，不该靠 `try` 兜，应该靠前置判断避免。**

### 判断空容器用真值测试

```python
if not items:             # 推荐
if len(items) == 0:       # 可以，但啰嗦
if items == []:           # 不推荐
```

空列表、空字符串、空字典、`0`、`None` 都是假值（Day01 讲过），所以 `if not items` 是 Python 惯用法。

## 5. 守卫语句（guard clause）

处理「异常情况先排除」有两种结构：

```python
# 写法 A：if/else 嵌套
def show_statistics(items):
    if len(items) == 0:
        print("暂无数据")
    else:
        avg = sum(items) / len(items)
        print("最大值:", max(items))
        print("平均值:", avg)
        # 主流程全部缩进在 else 里

# 写法 B：守卫语句
def show_statistics(items):
    if not items:
        print("暂无数据")
        return                # ← 提前退出
    # 下面的代码不用再担心空列表
    avg = sum(items) / len(items)
    print("最大值:", max(items))
    print("平均值:", avg)
```

**B 更好，三个理由：**

- **缩进浅**。主流程不嵌在 `else` 里，多个边界条件时差距更明显（A 会嵌套好几层）
- **先排除异常，后写主流程**。读到后面时可以确信「不正常的情况已经被挡在外面了」
- **边界处理集中在函数开头**，一眼能看出这个函数对输入有什么要求

`return` 在这里不返回任何值，**单纯用来提前结束函数**——这是 Day04 学的「`return` 会立即结束函数」的另一种用法。

> 守卫语句在实际项目里非常常见，参数校验、权限检查、空值处理都用这个结构。
> 对应的反面是「嵌套地狱」——`if` 里套 `if` 套 `if`，到第四层就读不懂了。

## 6. 命名：函数名用动词，变量名用名词

```python
def generate_random_number() -> int:      # 动词：做什么
    return random.randint(1, 100)

target_num = generate_random_number()     # 名词：是什么
```

这不只是风格问题，它能避免一类实际的 bug：

```python
def random_num():                 # 名词做函数名
    return random.randint(1, 100)

random_num = random_num()         # 函数被自己的返回值覆盖了
random_num()                      # TypeError: 'int' object is not callable
```

**函数名和变量名表达不同的东西，自然就不会撞名。**

其他命名惯例：

| 对象 | 风格 | 例子 |
|---|---|---|
| 变量、函数 | 小写加下划线 | `target_num`、`check_guess` |
| 常量 | 全大写 | `MAX_RETRY`、`BASE_DIR` |
| 类 | 首字母大写驼峰 | `APIClient` |
| 内部使用 | 前面加下划线 | `_internal_helper` |

还有一条：**名字要说明「业务含义」而不是「技术动作」**。`print_out` 说的是它调了 print，`show_statistics` 说的是它负责展示统计——后者让人不看实现就知道能拿它干什么。

## 7. 类型提示：容器与 `None`

```python
def show_statistics(guess_list: list[int]) -> None:
```

| 写法 | 含义 |
|---|---|
| `list` | 是个列表，不知道装什么 |
| `list[int]` | **整数列表**（Python 3.9+） |
| `dict[str, int]` | 键是字符串、值是整数的字典 |
| `-> None` | 没有有意义的返回值 |

**容器类型要写元素类型。** `list[int]` 让编辑器能发现 `items.append("abc")` 这类错误，`list` 做不到。

`-> None` 不是「可以不写」，它明确表达了「这个函数靠副作用工作（打印、写文件），不返回结果」。调用方看到就知道不该去接它的返回值。

> Python 3.9 之前要写 `from typing import List` 再用 `List[int]`，现在直接用内置的小写形式即可。

## 8. 不要维护两份表达相同含义的数据

```python
count = 0
guess_history = []

# 每次有效输入：
count += 1
guess_history.append(num)
```

`count` 的值永远等于 `len(guess_history)`——**两个变量表达同一件事**。

危害是：任何一个分支只更新了其中一个，两者就不一致了，而且**不会报错**，只会悄悄显示错误的数字。这种 bug 很难发现，因为程序一切「正常」。

正确做法是只保留一个数据源，次数现算：

```python
len(guess_history)
```

> 这条原则在数据库设计里叫「避免冗余」，在代码里叫 **Single Source of Truth（单一数据源）**。
> 判断方法：**能算出来的就不要存。** 存了就要负责同步。

## 9. 正面描述合法范围，再取反

```python
if i_num < 0 or i_num > 100:        # 枚举非法情况 → 容易漏
if not 1 <= i_num <= 100:           # 描述合法区间再取反 → 不会漏
```

第一种写法有个实际漏洞：它放过了 `0`（0 既不小于 0 也不大于 100）。而题目要求的是 1~100。

**枚举非法情况要求你想全所有边界，描述合法区间只要说清上下界。** 后者的心智负担小得多，出错概率也低。

这是个通用技巧：遇到范围判断，先写出「什么是对的」，再用 `not` 取反。

---

# 第二部分 · 当天的练习

## 一、题目

猜中或输入 `q` 退出时，显示：总次数、最大值、最小值、平均值（两位小数）。

**边界要求：** 用户可能一次都没猜就输入 `q`，这时列表为空——不能调 `max()`，也不能除以零。

## 二、第一版：两个必须修的问题

```python
random_num = random_num()          # ← 坑 3
count = 0
guess_his = []
while True:
    i_num = input("请输入1~100的正整数")
    try:
        if i_num == 'q':
            print_out(guess_his)    # ← 坑 1：少了 break
        i_num = int(i_num)

        if i_num < 0 or i_num > 100:    # ← 坑 2：0 能通过
            print("请输入1~100的数字")
            continue
        count += 1                      # ← 坑 4：和 len() 重复
        ...
```

### 坑 1：输入 `q` 之后程序没有退出

```python
if i_num == 'q':
    print_out(guess_his)      # 打印完统计……然后呢？
i_num = int(i_num)            # ← 继续执行到这里，int('q') 抛 ValueError
```

缺了 `break`，所以流程继续往下走，`int('q')` 抛出 `ValueError`，被 `except` 抓住，打印「格式错误」，然后 `continue` 开始下一轮。

**表现出来的现象是：输入 `q` 会打印一遍统计、再打印一句格式错误，然后游戏继续。** 想退出只能一直按 `q`，或者强行关掉。

这个 bug 的隐蔽之处在于**它没有崩溃**——异常被 `except` 吃掉了，看起来只是「提示有点怪」。

修法是补上 `break`：

```python
if i_num == 'q':
    print_out(guess_his)
    break
```

> 教训：`if` 分支里做完事情之后，要明确「接下来该去哪」。只写处理、不写流程控制，代码就会顺着往下流到不该去的地方。

### 坑 2：`i_num < 0 or i_num > 100` 放过了 0

题目要求 1~100，这个条件只拦住了负数和大于 100 的数，**`0` 能通过**。

```python
if i_num < 0 or i_num > 100:    # 0 不满足，所以不会被拦
```

正确写法：

```python
if not 1 <= i_num <= 100:       # -1、0、101 全部拒绝
    print("请输入 1~100 的数字")
    continue
```

把条件写成「**不在合法区间内**」，而不是逐个列举非法情况。列举的写法很容易漏掉边界——这次漏的就是 0 这个边界。

> 规律：**正面描述合法范围，再取反**，比枚举所有非法情况更难出错。

### 坑 3：函数名被它自己的返回值覆盖

```python
def random_num():
    return random.randint(1, 100)

random_num = random_num()    # 右边调用函数，左边把结果赋给同一个名字
```

这行执行完，`random_num` 这个名字就**从函数变成了一个整数**。本题只调用一次，所以能跑；但如果后面想再抽一个随机数，`random_num()` 会报：

```text
TypeError: 'int' object is not callable
```

而且这个报错信息对新手很难懂——明明定义了函数，怎么说 int 不能调用？

正确做法是让函数名和变量名表达不同的东西：

```python
def generate_random_number() -> int:
    return random.randint(1, 100)

target_num = generate_random_number()
```

> **函数名用动词（做什么），变量名用名词（是什么）。** `generate_random_number` 是动作，`target_num` 是结果，自然不会撞名。

**注意：这个问题当时被指出了，但 `Day6.py` 的最终代码没有修改**，仍然是 `random_num = random_num()`。复习时看到这一行要知道它是个隐患。

### 坑 4：`count` 与 `len()` 维护同一份信息

最终统计用的是 `len(guess_list)`，`count` 从头到尾没参与输出。两份数据表达同一个含义，却要分别更新——这是 bug 的温床。

直接删掉 `count`，次数用 `len(guess_his)` 现算。

> 原则：**不要维护两份表达相同含义的数据。** 能算出来的就不要存。

## 三、空列表边界与守卫语句

第一版用 `if/else` 把空列表和非空分成两个大分支：

```python
if len(guess_list) == 0:
    print("猜测记录:[]")
    print("有效猜测次数:0")
    print("暂无统计数据")
else:
    avg = sum(guess_list) / len(guess_list)
    ...
```

能用，但「打印记录」和「打印次数」这两件事在两个分支里各写了一遍。

更好的写法是**守卫语句**（guard clause）：先处理异常情况、提前 `return`，剩下的主流程不再缩进。

```python
def show_statistics(guess_list: list[int]) -> None:
    print("游戏结束！")
    print("猜测记录：", guess_list)
    print("有效猜测次数：", len(guess_list))

    if not guess_list:          # 空列表：说一声就走
        print("暂无统计数据")
        return

    # 下面的代码不用再担心列表是空的
    avg = sum(guess_list) / len(guess_list)
    print("最大猜测值：", max(guess_list))
    print("最小猜测值：", min(guess_list))
    print(f"平均猜测值：{avg:.2f}")
```

两个要点：

- **`return` 不只用来返回值，也可以单纯用来提前结束函数。** 这里 `-> None`，`return` 后面什么都不跟。
- **`if not guess_list` 就是判断空列表。** 空列表、空字符串、空字典、`0`、`None` 在布尔上下文里都是假值，不用写 `len(x) == 0`。

为什么必须守卫：`max([])` 会抛 `ValueError: max() arg is an empty sequence`，`sum([])/len([])` 会抛 `ZeroDivisionError`。这两个异常都是「正常使用中必然会遇到」的，不该靠 `try` 兜，应该靠前置判断避免。

## 四、类型提示与命名

**`list` 不如 `list[int]`。** 前者只说明「这是个列表」，后者说明「这是个整数列表」。Python 3.9 以上支持 `list[int]` 这种写法（更早的版本要 `from typing import List`）。

**`print_out` 不如 `show_statistics`。** 前者说的是「它干了什么动作」（打印输出），后者说的是「它负责什么业务」（展示统计）。函数名应该让人不看实现就知道能拿它干什么。

## 五、最终代码

```python
import random


def random_num():
    return random.randint(1, 100)

def check_num(input_num: int, target_num: int) -> str:
    if input_num == target_num:
        return "正确"
    elif input_num < target_num:
        return "小了"
    else:
        return "大了"

def show_statistics(guess_list: list[int]) -> None:
    print("游戏结束！")
    print("猜测记录：", guess_list)
    print("有效猜测次数：", len(guess_list))

    if not guess_list:
        print("暂无统计数据")
        return

    avg = sum(guess_list) / len(guess_list)
    print("最大猜测值：", max(guess_list))
    print("最小猜测值：", min(guess_list))
    print(f"平均猜测值：{avg:.2f}")

random_num = random_num()
guess_his = []
while True:
    i_num = input("请输入1~100的正整数")
    try:
        if i_num == 'q':
            show_statistics(guess_his)
            break
        i_num = int(i_num)

        if not 1 <= i_num <= 100:
            print("请输入1~100的数字")
            continue
        guess_his.append(i_num)
        result = check_num(i_num, random_num)

        if result == "正确":
            show_statistics(guess_his)
            break
        else:
            print("结果", result, "请继续猜")
            continue
    except ValueError:
        print("格式错误,重新输入")
        continue
```

程序已经分成三个函数：生成答案、判断大小、展示统计。主循环只负责「拿输入、调函数、控制流程」。这是**单一职责**的雏形，Day 10 会把这三个函数搬进独立文件。

### 这一版还剩两个问题

**一、`random_num = random_num()` 没改**（见坑 3）。

**二、`try` 包的范围太大。** 整个游戏主体都在 `try` 里面，但真正会抛 `ValueError` 的只有 `int(i_num)` 那一行。范围过大有两个坏处：

- 别处笔误导致的 `ValueError` 也会被当成「用户输入格式错误」，掩盖真 bug
- 读代码的人得扫完整个 `try` 块才知道在防什么

更好的结构是只包住危险的那一行：

```python
try:
    input_num = int(user_input)
except ValueError:
    print("格式错误，请输入整数或 q")
    continue

# 转换成功，后面的代码不在 try 里
if not 1 <= input_num <= 100:
    ...
```

异常处理的范围怎么收，Day 15-17 会专门练。

## 六、复习自测

1. `if i_num == 'q': show_statistics(...)` 少写 `break` 会出现什么现象？为什么不崩溃？
2. 为什么 `if i_num < 0 or i_num > 100` 拦不住 0？怎么写才不会漏边界？
3. `random_num = random_num()` 之后再调用 `random_num()` 会发生什么？
4. `max([])` 和 `sum([])/len([])` 分别抛什么异常？该用 `try` 还是前置判断？
5. 守卫语句（提前 `return`）比 `if/else` 好在哪？
6. `list` 和 `list[int]` 作为类型提示有什么区别？

<details>
<summary>参考答案</summary>

1. 打印统计后流程继续往下走，`int('q')` 抛 `ValueError` 被 `except` 捕获，打印「格式错误」然后进入下一轮——现象是「输入 q 退不出去」。不崩溃正是因为异常被 `except` 吃掉了，这让 bug 更难发现。
2. 因为 0 既不小于 0 也不大于 100，两个条件都不满足。应该正面描述合法区间再取反：`not 1 <= i_num <= 100`。
3. 抛 `TypeError: 'int' object is not callable`。那个名字已经被整数覆盖，不再是函数。
4. `max([])` 抛 `ValueError: max() arg is an empty sequence`；`sum([])/len([])` 抛 `ZeroDivisionError`。这两种情况是正常流程里必然会出现的，应该用前置判断（守卫语句）避免，而不是用 `try` 兜。
5. 异常情况先处理掉并提前退出，主流程不必嵌在 `else` 里，缩进浅、可读性好；而且主流程后面的代码可以确信「不正常的情况已经被排除了」。
6. `list` 只说明是列表，不说明元素类型；`list[int]` 明确元素是整数，编辑器和 mypy 能据此检查出 `append("abc")` 这类错误。

</details>
