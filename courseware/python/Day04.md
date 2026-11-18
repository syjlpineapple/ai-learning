# Day 04 · 函数、返回值与职责分离

> **学习日** 2026-10-18（18:07 - 18:11，3 轮对话）
> **对应代码** [`dailypractice/Day4.py`](../../dailypractice/Day4.py)
> **原始对话** `courseware/_raw/markdown/01_Python每日练习出题.md`（对话里称「Day 5」）

## 本节掌握

- `def` 定义函数、参数、`return` 返回结果
- **函数必须先定义后调用**，否则 `NameError`
- `return` 和 `print` 的区别
- 职责分离：判断逻辑该返回结果，而不是自己打印
- 类型注解 `def f(x: int) -> str`，以及它**不做运行时检查**

---

# 第一部分 · 知识讲解

## 1. 函数：为什么需要

前三天的代码都写在一条主流程里。随着功能增加，这种写法会遇到三个问题：

- **重复**：同样的逻辑在多处出现，改一处就得改所有地方
- **难读**：一眼看不出「这段代码在干什么」
- **难测**：想验证某段逻辑，只能把整个程序跑一遍

函数解决的是**把一件事封装起来、给它起个名字、可以反复调用**。

## 2. 定义与调用

```python
def add(a, b):          # 定义
    return a + b

result = add(3, 5)      # 调用，result 得到 8
```

| 部分 | 说明 |
|---|---|
| `def` | 定义函数的关键字 |
| `add` | 函数名，命名规则和变量一样（小写加下划线） |
| `(a, b)` | 形参（parameter），函数内部用的名字 |
| `:` | 冒号不能省 |
| 缩进的部分 | 函数体 |
| `return` | 把结果交出去（可选） |

调用时传进去的 `3, 5` 叫**实参**（argument）。

## 3. 参数的几种形式

```python
def greet(name, greeting="你好", *args, **kwargs):
    ...
```

现在需要掌握前三种：

### 位置参数

```python
def check(input_num, target_num):
    ...

check(50, 100)       # input_num=50, target_num=100，按位置对应
```

**顺序决定对应关系**，传反了不会报错但结果错——这是实际会踩的坑（Day12 就传反过一次）。

### 关键字参数

```python
check(input_num=50, target_num=100)      # 显式指定，顺序无关
check(target_num=100, input_num=50)      # 同样正确
```

参数多的时候用关键字参数更安全、更可读。

### 默认值

```python
def greet(name, greeting="你好"):
    return f"{greeting}，{name}"

greet("Tom")                  # '你好，Tom'
greet("Tom", "早上好")         # '早上好，Tom'
```

**带默认值的参数必须放在没有默认值的参数后面**，否则语法错误。

> 有个经典陷阱：**不要用可变对象做默认值**。
>
> ```python
> def add_item(item, items=[]):     # 危险
>     items.append(item)
>     return items
> ```
>
> 默认值在函数**定义时**创建一次，所有调用共享同一个列表，于是会累积。正确写法是用 `None`：
>
> ```python
> def add_item(item, items=None):
>     if items is None:
>         items = []
> ```

## 4. `return` 的语义

```python
def f():
    return 42        # 返回 42，并立即结束函数
```

三个要点：

**一、`return` 会立即结束函数**，后面的代码不执行。所以它也可以用来提前退出（Day06 的守卫语句就靠这个）。

**二、没有 `return` 的函数返回 `None`。**

```python
def show(x):
    print(x)         # 只打印，没有 return

result = show(5)     # 屏幕显示 5，但 result 是 None
```

**屏幕上看到了值，不等于程序拿到了值**——这是初学时最容易混的一点。

**三、可以返回多个值**（实际上是打包成元组）：

```python
def divide(a, b):
    return a // b, a % b

q, r = divide(17, 5)      # q=3, r=2
```

### `return` 与 `print` 的根本区别

| | `return` | `print` |
|---|---|---|
| 作用 | 把值交给**调用方** | 把文字显示给**人** |
| 结果去哪 | 可以继续参与运算、比较、传给其他函数 | 只到屏幕上，程序拿不到 |
| 能否测试 | 直接断言返回值 | 得捕获标准输出，很麻烦 |

一句话：**`print` 是给人看的，`return` 是给程序用的。**

## 5. 作用域：函数内外的变量

```python
x = 10                 # 全局变量

def f():
    y = 20             # 局部变量，只在函数内部存在
    print(x)           # 可以读到全局变量
    print(y)

f()
print(y)               # NameError: name 'y' is not defined
```

**函数内部定义的变量，外部访问不到。** 这是好事——它保证了函数内部的变量名不会和外面冲突。

### 读可以，写要声明

```python
count = 0

def increment():
    count = count + 1      # UnboundLocalError
```

一旦函数里有对某个名字的**赋值**，Python 就把它当成局部变量，于是 `count + 1` 里的 `count` 还没有值。要真的改全局变量得用 `global`：

```python
def increment():
    global count
    count += 1
```

**但 `global` 应该尽量避免。** 更好的做法是传参数、返回结果：

```python
def increment(count):
    return count + 1

count = increment(count)
```

理由是：用 `global` 的函数，行为取决于外部状态，既难测试也难推理——你没法只看函数本身判断它会做什么。

### LEGB 查找顺序

Python 查找一个名字时按这个顺序：

| 层 | 含义 |
|---|---|
| **L**ocal | 当前函数内部 |
| **E**nclosing | 外层函数（嵌套函数时） |
| **G**lobal | 模块级 |
| **B**uiltin | 内置名字（`print`、`len` 等） |

这解释了一类诡异问题：如果你定义了一个变量叫 `list` 或 `sum`，就会**遮蔽内置函数**，之后 `sum(...)` 会报 `TypeError`。所以不要用内置名字做变量名。

## 6. `def` 是一条语句，会按顺序执行

这点常被忽略：**`def` 不是「声明」，它是一条要执行的语句。** 执行它的效果是「创建一个函数对象，并把函数名绑定到它」。

所以：

```python
f()                  # NameError: name 'f' is not defined

def f():
    print("hi")
```

模块最外层的代码自上而下执行，跑到 `f()` 时下面那个 `def` 还没执行，这个名字还不存在。

**但函数之间互相调用没问题：**

```python
def a():
    b()              # 这时 b 还没定义，但没关系

def b():
    print("hi")

a()                  # 正常工作
```

因为 `a()` 里的 `b()` 是在**运行时**才去查找 `b`，那时两个 `def` 都已经执行完了。

> 规律：**名字必须在「使用的那一刻」已经存在**，而不是「写在前面」。

## 7. 函数是一等公民

函数名就是一个变量，指向函数对象：

```python
def greet():
    print("hi")

f = greet            # 把函数赋给另一个变量（注意没有括号）
f()                  # hi

print(greet)         # <function greet at 0x...>
print(greet())       # 先执行 greet()，再打印它的返回值 None
```

**`greet` 和 `greet()` 完全不同**：前者是函数本身，后者是调用它。这个区别在 Day21 用 Mock 断言时会造成一个实际的 bug。

反过来也要小心：如果用函数名当变量名存结果，函数就被覆盖了：

```python
def random_num():
    return random.randint(1, 100)

random_num = random_num()      # 现在 random_num 是个整数，不再是函数
random_num()                   # TypeError: 'int' object is not callable
```

这个坑 Day06 会实际遇到。

## 8. 类型注解

```python
def check_guess(input_num: int, target_num: int) -> str:
    ...
```

| 写法 | 含义 |
|---|---|
| `input_num: int` | 这个参数预期是整数 |
| `-> str` | 返回值预期是字符串 |

**注解不做运行时检查**：

```python
def add(a: int, b: int) -> int:
    return "hello"

add(1, 2)        # 正常返回 'hello'，不报错
```

它的价值在三个地方：

- **给人看**——不用读实现就知道函数吃什么、吐什么
- **给编辑器看**——自动补全、提示明显的类型错误
- **给静态检查工具看**——`mypy`、`pyright` 能在**运行前**发现问题

常见的注解写法：

```python
def f(x: int) -> None: ...                    # 没有有意义的返回值
def f(items: list[int]) -> dict[str, int]: ...# 容器要写元素类型
def f(name: str | None = None) -> str: ...    # 可能是 None（Python 3.10+）
```

从现在开始养成写注解的习惯，成本很低，收益会在代码变多后显现。

## 9. 职责分离：一个函数只做一件事

本节的设计要求是「`check_guess()` 只负责判断，不负责打印，也不负责退出游戏」。这条要求背后是**单一职责原则**。

对比两种设计：

```python
# A：函数自己打印
def check_guess(a, b):
    if a < b:
        print("小了")

# B：函数返回结果，调用方决定怎么用
def check_guess(a, b):
    if a < b:
        return "小了"
```

B 更好，两个具体理由：

**一、可复用。** A 的结果只能去控制台。以后要显示在网页上、写进日志、发给另一个程序，A 就得重写，而 B 原样可用。

**二、可测试。**

```python
assert check_guess(5, 10) == "小了"     # B：三行搞定
```

A 要测就得捕获标准输出，麻烦得多。

> **一个函数能不能被方便地测试，取决于它有没有把「算什么」和「怎么输出」分开。**
> 这是后面 Day07 写 `assert`、Day21 写单元测试的前提——那时能轻松测试，靠的是现在做对的设计。

---

# 第二部分 · 当天的练习

## 一、题目

把「判断猜大猜小」的逻辑从主循环里提出来，做成一个函数：

```python
def check_guess(input_num, random_num):
    ...   # 小了返回 "小了"，大了返回 "大了"，对了返回 "正确"
```

附加要求：**`check_guess()` 只负责判断，不负责打印，也不负责退出游戏。**

这个要求是本节的重点，理由见第四节。

## 二、第一版：逻辑对了，但跑不起来

```python
while True:
    i_num = input("请输入数字")
    ...
    result = check_guess(i_num, r_num)     # ← 这里调用
    ...

def check_guess(input_num, random_num):    # ← 定义写在了后面
    if input_num < random_num:
        return "小了"
    ...
```

函数本身写得对：参数接对了，用 `return` 交出结果而不是自己打印。但程序一运行就报错：

```text
NameError: name 'check_guess' is not defined
```

### 坑 1：函数定义在调用之后

**Python 是从上往下逐行执行的。** `def` 语句本身就是一条「要执行的语句」——执行它才会把函数名绑定到内存里的函数对象上。程序跑到 `check_guess(...)` 这一行时，下面那个 `def` 还没被执行，这个名字还不存在。

正确结构是函数定义在前、主程序在后：

```python
import random

def check_guess(input_num, random_num):
    ...

# 主程序从这里开始
r_num = random.randint(1, 100)
```

> 这不是「Python 要求函数必须写在最上面」，而是「名字必须在使用前已经绑定」。所以函数之间互相调用没问题（调用发生在运行时，那时所有 `def` 都已执行完）；但模块最外层的代码调用下方定义的函数就会失败。

## 三、`return` 与 `print` 的区别

这是本节最值得记住的一点。

```python
def add(a, b):
    return a + b

result = add(3, 5)      # result == 8，可以继续参与运算
```

```python
def add(a, b):
    print(a + b)

result = add(3, 5)      # 屏幕显示 8，但 result 是 None
```

**没有 `return` 的函数返回 `None`。** 屏幕上看到了数字，不等于程序拿到了这个值。

一句话记法：**`print` 是给人看的，`return` 是给后续代码用的。**

## 四、为什么函数不该自己打印

当时的设计题：`check_guess()` 要扩展功能，哪种做法更好？

- **A.** 在 `check_guess()` 里面打印所有提示
- **B.** 让 `check_guess()` 返回结果，由主程序决定怎么处理

答案是 **B**。当时给出的理由是：「如果用 A，要三个位置都要加，而且函数需要比较返回结果，调用处决定是否需要打印。」这个判断是对的，它触及了**职责分离**（Separation of Concerns）。往下展开有两层。

### 第一层：可复用

如果函数内部写死了 `print`，那它就只能往控制台输出。以后要把结果显示在网页上、写进日志文件、或者传给别的程序，这个函数就用不了，只能重写一个。

返回结果的版本，调用方想怎么处理都行：

```python
result = check_guess(i_num, r_num)

if result == "正确":
    print("恭喜你猜对了！")
    break
else:
    print(f"提示：猜{result}")
```

### 第二层：可测试

```python
print(check_guess(5, 10))    # 小了
print(check_guess(15, 10))   # 大了
print(check_guess(10, 10))   # 正确
```

三行就能验证函数对不对，不需要启动游戏、不需要手敲输入。

如果函数内部是 `print`，要测它就得去捕获标准输出——麻烦得多。这正是 Day 07 开始写 `assert`、Day 21-22 写单元测试的前提：**一个函数能不能被方便地测试，取决于它有没有把「算什么」和「怎么输出」分开。**

> 这条原则在后面反复出现：`history.py` 把「读写文件」和「校验数据」分开（Day 11-14）、`APIClient` 把「发请求」和「处理响应」分开（Day 20）。都是同一件事。

## 五、类型注解

当时的追问：「函数返回类型不需要定义吗？」

**Python 不要求，但建议写。**

```python
def check_guess(input_num: int, random_num: int) -> str:
    ...
```

| 写法 | 含义 |
|---|---|
| `input_num: int` | 这个参数预期是整数 |
| `-> str` | 这个函数预期返回字符串 |

### 关键：注解不做运行时检查

```python
def add(a: int, b: int) -> int:
    return "hello"

print(add(1, 2))     # 正常输出 hello，不报错
```

注解只是写给**人**和**工具**看的：

- 让读代码的人立刻知道函数吃什么、吐什么
- 让编辑器能自动补全、能提示明显的类型错误
- 配合 `mypy`、`pyright` 这类静态检查工具，在**运行前**发现问题

注解本身不会在运行时拦截任何东西。想要运行时校验得自己写判断，或者用 Pydantic 这类库。

顺带一个后面会用到的写法：函数可能返回字符串、也可能什么都没有时，写成 `-> str | None`（Python 3.10+）。处理「查询不到结果」「接口返回空」时很常见。

## 六、最终代码

```python
import random

def check_guess(input_num: int, random_num: int) -> str:
    if input_num < random_num:
        return "小了"
    elif input_num > random_num:
        return "大了"
    else:
        return "正确"

r_num = random.randint(1, 100)
print("随机数", r_num)
count = 0

while True:
    i_num = input("请输入数字")

    if i_num == 'q':
        print(f"游戏退出：共输入{count}次")
        break
    try:
        i_num = int(i_num)
        count += 1
        result = check_guess(i_num, r_num)
        print(result)
        if result == "正确":
            break
    except ValueError:
        print("输入无效，请输入正整数，退出请输入‘q’")
```

最后那三个分支里，`else` 其实可以省掉——前两个条件都不成立时自然会执行到最后一行：

```python
    if input_num < random_num:
        return "小了"
    if input_num > random_num:
        return "大了"
    return "正确"
```

两种写法都对。`return` 会直接结束函数，所以不存在「漏掉 else 导致继续往下走」的问题。

### 用字符串做返回值，埋了一个隐患

`check_guess()` 返回的是中文字符串，主程序靠 `if result == "正确"` 判断。**这让业务逻辑和显示文案焊死了**——哪天想把提示改成「猜中了」，就得同时改函数里的 `return` 和主程序里的比较，改漏一处游戏就永远不结束。

更稳的做法是返回状态值（比如 `-1 / 0 / 1`，或者 `enum`），文案在打印时再决定。这个问题在 Day 14 会以另一种形式再出现一次：那边的测试用 `assert str(e) == "类型错误"` 把测试和中文文案绑死了，改一个字测试就断。

## 七、复习自测

1. 为什么函数定义必须写在调用之前？两个函数互相调用会有这个问题吗？
2. `def f(): print(1)`，那么 `x = f()` 之后 `x` 是什么？
3. 为什么说「函数自己打印」会让它难以测试？
4. `def add(a: int) -> int: return "hi"` 能运行吗？类型注解的作用是什么？
5. `check_guess` 返回中文字符串、主程序用 `== "正确"` 判断，有什么风险？

<details>
<summary>参考答案</summary>

1. 因为 `def` 是一条执行语句，执行后函数名才存在。模块最外层的代码自上而下执行，调用时下方的 `def` 还没执行到。但函数之间互相调用没问题——调用发生在运行时，那时所有 `def` 都已经执行完毕。
2. `None`。函数没有 `return`，默认返回 `None`；屏幕上打印出了 1，但这个值没有交给调用方。
3. 结果只去了标准输出，调用方拿不到返回值，断言无从下手。要测就得捕获 stdout，比直接断言返回值麻烦得多。
4. 能正常运行并输出 `hi`。注解不做运行时检查，它的作用是给人和工具（编辑器、mypy）提供信息，在运行前发现问题。
5. 业务判断依赖了显示文案。改文案就必须同步改所有比较它的地方，漏改一处就出 bug，而且这种 bug 不会报错，只会表现为「逻辑莫名不生效」。

</details>
