# Day 03 · 计数器与异常处理

> **学习日** 2026-10-17（09:57 - 10:03，2 轮对话）
> **对应代码** [`dailypractice/Day3.py`](../../dailypractice/Day3.py)
> **原始对话** `courseware/_raw/markdown/01_Python每日练习出题.md`（对话里称「Day 4」）

## 本节掌握

- 计数器 `count += 1`，以及它该放在哪
- `try / except ValueError` 捕获类型转换失败
- **先校验、再计数、后比较**的顺序
- `isdigit()` 的边界：不认负号
- 异常处理相比 `isdigit()` 校验的优势

---

# 第一部分 · 知识讲解

## 1. 增强赋值运算符

```python
count = count + 1
count += 1          # 等价的简写
```

所有算术运算符都有对应的增强形式：

| 写法 | 等价于 |
|---|---|
| `x += 1` | `x = x + 1` |
| `x -= 1` | `x = x - 1` |
| `x *= 2` | `x = x * 2` |
| `x /= 2` | `x = x / 2`（结果是浮点数） |
| `x //= 2` | `x = x // 2`（整除） |
| `x %= 2` | `x = x % 2`（取余） |

**注意 Python 没有 `++`**。`count++` 是语法错误，`++count` 虽然不报错但等于「正号的正号」，值不变——这是从 C 或 Java 过来时的常见误写。

## 2. 什么是异常，为什么需要它

程序运行中出现无法继续的情况时，Python 会**抛出异常**（raise an exception）：

```python
int("abc")
# ValueError: invalid literal for int() with base 10: 'abc'
```

异常不是「程序崩了」这么简单，它是一套**信息传递机制**：

- 它带着**类型**（`ValueError`）说明出了哪一类问题
- 它带着**消息**说明具体细节
- 它带着**traceback** 说明是从哪一行、经过哪些调用来的
- 它会**沿调用栈向上传播**，直到有人处理它

如果没有异常机制，函数只能用返回值表示失败（比如返回 `-1` 或 `None`），而那样调用方很容易忘记检查，错误就被静默忽略了。**异常的好处是「不处理就会炸」**——强迫你面对它。

## 3. `try / except` 语法

```python
try:
    num = int(user_input)      # 可能抛异常的代码
except ValueError:
    print("输入无效")           # 抛出 ValueError 时执行这里
```

执行逻辑：

1. 执行 `try` 块里的代码
2. 如果**没有异常**，跳过所有 `except`，继续往下
3. 如果抛出了异常，**立刻中断 `try` 块的剩余代码**，去找匹配的 `except`
4. 找到就执行它，然后继续往下；找不到就继续向上抛

**第 3 点很重要：异常一旦抛出，`try` 块里后面的代码一行都不会执行。**

```python
try:
    num = int("abc")       # 这里就炸了
    print("转换成功")        # ← 永远不会执行
except ValueError:
    print("转换失败")
```

## 4. 常见的内置异常

| 异常 | 什么时候抛 |
|---|---|
| `ValueError` | 类型对但值不合法，如 `int("abc")` |
| `TypeError` | 类型不对，如 `"a" + 1` |
| `KeyError` | 字典里没有这个键 |
| `IndexError` | 序列下标越界 |
| `AttributeError` | 对象没有这个属性或方法 |
| `ZeroDivisionError` | 除以零 |
| `FileNotFoundError` | 文件不存在 |
| `NameError` | 用了没定义的变量名 |

**`ValueError` 和 `TypeError` 的区别值得分清**：

```python
int("abc")        # ValueError  ← 类型是 str 没问题，但内容不是合法的整数
"abc" + 1         # TypeError   ← str 和 int 根本不能相加
```

一句话：**类型不对是 `TypeError`，类型对但值不行是 `ValueError`。**

## 5. 捕获的几种写法

```python
# 捕获一种
except ValueError:

# 捕获多种（写成元组）
except (ValueError, TypeError):

# 拿到异常对象
except ValueError as e:
    print(f"出错了：{e}")

# 捕获所有异常（慎用）
except Exception:
```

关于 `as e`：拿到异常对象后可以 `print(e)` 看消息、`type(e)` 看类型。**但如果后面不用 `e`，就不要写 `as e`**——这是 lint 工具会报的告警。

### 不要用 `except:`（裸 except）

```python
except:              # 不要这样写
```

裸 `except` 会捕获**所有**异常，包括 `KeyboardInterrupt`（用户按 Ctrl+C）和 `SystemExit`——结果是程序没法用 Ctrl+C 中断。要兜底至少写 `except Exception:`，它不包含这两个。

`except Exception` 本身也要慎用，原因在 Day12 会详细讲：它会把程序自己的 bug 也吞掉。

## 6. 完整结构：`try / except / else / finally`

```python
try:
    ...
except ValueError:
    ...        # 抛出 ValueError 时执行
else:
    ...        # try 块【没有】抛异常时执行
finally:
    ...        # 无论如何都执行
```

四个块的触发条件：

| 块 | 什么时候执行 |
|---|---|
| `try` | 总是执行（这是被保护的代码） |
| `except` | 抛出了匹配的异常 |
| `else` | **没有**抛出任何异常 |
| `finally` | **无论如何**都执行（包括有 `return` 时） |

`else` 容易被忽略，但它有明确的用途：**把「成功后才该做的事」和「可能出错的事」分开**。

```python
try:
    num = int(user_input)      # 只保护这一行
except ValueError:
    print("格式错误")
else:
    print(f"转换成功：{num}")   # 只在转换成功时执行
```

这比把 `print` 也塞进 `try` 更好——`try` 块越小，越不容易误捕获。

> `else` 还有个重要用途：测试「某段代码应该抛异常」。如果没抛，就在 `else` 里主动让测试失败。Day09 会用到。
>
> `finally` 用于资源清理（关文件、关连接），Day20 会用到。

## 7. 两种风格：LBYL 与 EAFP

处理「可能失败的操作」有两种思路：

**LBYL（Look Before You Leap，先检查再行动）：**

```python
if user_input.isdigit():
    num = int(user_input)
else:
    print("不是数字")
```

**EAFP（Easier to Ask Forgiveness than Permission，先做再处理失败）：**

```python
try:
    num = int(user_input)
except ValueError:
    print("不是数字")
```

| | LBYL | EAFP |
|---|---|---|
| 思路 | 先判断条件是否满足 | 直接做，失败了再兜 |
| 优点 | 意图直白 | 不会漏掉边界情况 |
| 缺点 | **检查条件容易写不全** | 需要知道会抛什么异常 |

**Python 社区更偏向 EAFP**，原因是「什么样的输入能成功」这件事，交给那个操作自己判断最准确。

本节就是个好例子：`isdigit()` 认为 `"-5"` 不是数字，但 `int("-5")` 完全能成功。**用 LBYL 时，你的检查逻辑和真实的操作规则可能不一致**，而 EAFP 不存在这个问题。

还有个场景 LBYL 根本不可靠：检查和使用之间状态可能变化（比如先 `if os.path.exists(f)` 再 `open(f)`，中间文件可能被删了）。这类问题叫 TOCTOU，只有 EAFP 能避免。

## 8. 链式比较

```python
if 1 <= num <= 100:
    ...
```

Python 支持把比较串起来，等价于 `1 <= num and num <= 100`，但只求值 `num` 一次。

这是 Python 特有的语法糖（多数语言不支持），用在范围判断上非常自然：

```python
not 1 <= num <= 100          # 不在 1~100 范围内
0 < x < y < 100              # 还能继续串
```

### 但 `not` 的优先级要注意

```python
not 1 <= x <= 100            # not (1 <= x <= 100)        ← 正确
not 1 <= x and x <= 100      # (not 1 <= x) and x <= 100  ← 含义完全不同
```

**`not` 的优先级高于 `and`/`or`，但低于比较运算符。** 所以 `not a <= b` 是 `not (a <= b)`，而加上 `and` 之后就要小心了。

链式比较用错会造成严重后果——Day14 会遇到一个「条件永远不成立」的 bug，根源就在这里。

## 9. 异常处理的范围要小

```python
# 不好：try 包住了一大段
try:
    num = int(user_input)
    count += 1
    if num < target:
        print("小了")
    ...
except ValueError:
    print("输入无效")

# 更好：只包住真正会抛异常的那一行
try:
    num = int(user_input)
except ValueError:
    print("输入无效")
    continue

count += 1          # 下面的代码不在 try 里
if num < target:
    ...
```

`try` 范围过大有两个危害：

1. **误捕获**。里面任何一处笔误导致的 `ValueError` 都会被当成「用户输入无效」，真 bug 被伪装成正常分支。
2. **难读**。读代码的人得扫完整个 `try` 块才知道你在防什么。

这条原则会在 Day09、Day15 反复强调，是异常处理的核心纪律。

---

# 第二部分 · 当天的练习

## 一、题目

给游戏加次数统计：猜中后显示一共猜了多少次；输入 `q` 退出；**无效输入不计入次数**。

最后那条要求是本节的难点，它决定了代码的判断顺序。

## 二、第一版：用 isdigit 校验

```python
count = 0
random_num = random.randint(1, 100)
while True:
    input_num = input("请输入数字")

    if input_num == 'q':
        print(f"游戏退出：共输入{count}次")
        break
    else:
        count += 1                              # ← 位置错了
        if not input_num.isdigit():
            print("输入无效，请输入数字，退出请输入‘q’")
        elif int(input_num) < random_num:
            ...
```

两处做对了，一处做错了。

### 做对了：`count` 和 `random_num` 都在循环外

如果把 `count = 0` 写进 `while` 里面，每轮都重置为 0，最后永远显示「猜了 1 次」。

### 做对了：先判断 `q`，再碰 `int()`

```python
if input_num == 'q':   # 先处理退出
    ...
```

没有急着转换类型，避免了 `int('q')` 直接崩掉。**判断顺序本身就是一种防御**。

### 坑 1：计数器位置错误，无效输入也被算进去

```python
else:
    count += 1                      # 不管输入是什么，先加一次
    if not input_num.isdigit():     # 然后才发现这是个无效输入
        print("输入无效")
```

用户输入 `abc`，次数也 +1，违反了「无效输入不计入次数」。

正确顺序是**校验通过之后才计数**：

1. 是不是 `q` → 退出
2. 是不是有效整数 → 不是就提示，并且**不计数**
3. 是有效整数 → 计数，然后比较大小

> 规律：**先验证输入，再执行后续操作。** 这个顺序在后面读文件（Day 11-14）和处理 HTTP 响应（Day 15-20）时会反复出现，是同一个原则。

## 三、第二版：改用 try/except

### 坑 2：`isdigit()` 不认负号

```python
"123".isdigit()    # True
"-5".isdigit()     # False  ← 负号让它判为非数字
"3.14".isdigit()   # False  ← 小数点也不认
```

这个游戏只要 1~100，负数没意义，所以 `isdigit()` 够用。但要知道它的边界：**它判断的是「每个字符都是数字字符」，不是「能不能转成数字」**。

真实项目里更通用的做法是**直接尝试转换，失败了再处理**：

```python
try:
    num = int(input_num)
except ValueError:
    print("输入无效")
```

这叫 EAFP（Easier to Ask for Forgiveness than Permission，先做再处理失败），是 Python 的惯用风格；前面 `isdigit()` 那种先检查再动手叫 LBYL（Look Before You Leap）。Python 社区更偏向前者，因为「什么样的字符串能转成 int」这件事交给 `int()` 自己判断最准确。

## 四、最终代码

```python
import random

count = 0
random_num = random.randint(1, 100)
print("随机数", random_num)
while True:
    input_num = input("请输入数字")

    if input_num == 'q':
        print(f"游戏退出：共输入{count}次")
        break

    try:
        input_num = int(input_num)
        count += 1
        if int(input_num) < random_num:
            print("猜小了")
        elif int(input_num) > random_num:
            print("猜大了")
        else:
            print(f"猜对了，共猜了{count}次")
            break
    except ValueError:
        print("输入无效，请输入正整数，退出请输入‘q’")
```

`count += 1` 现在在 `int()` 转换成功之后，无效输入不会计数了。

### 还有两个小问题

**一、转换完又调了一次 `int()`。**

```python
input_num = int(input_num)        # 这里已经是 int 了
if int(input_num) < random_num:   # 不必再转
```

直接写 `if input_num < random_num:` 即可。不是错误，是多余——而且会让读代码的人怀疑「这里是不是还有可能是字符串」。

**二、提示语和实际校验不一致。**

提示写的是「请输入正整数」，但 `int()` 接受 `-5` 和 `0`，它们都能通过校验进入比较。要么把提示改准确（「请输入 1~100 的整数」），要么真的加上范围判断。

这类「提示语承诺了代码没做的事」的问题，在真实项目里是 bug 的常见来源。

## 五、复习自测

1. `count = 0` 写在 `while` 里面会怎样？
2. 「无效输入不计入次数」这个要求，决定了 `count += 1` 必须放在哪里？
3. `"-5".isdigit()` 和 `int("-5")` 分别是什么结果？
4. `try` 块里应该只包裹哪一行？把整个游戏逻辑都放进 `try` 有什么坏处？

<details>
<summary>参考答案</summary>

1. 每轮循环重置为 0，最终输出永远是「猜了 1 次」。
2. 必须放在类型转换成功之后——也就是 `try` 块里 `int()` 那一行的下面。放在 `else` 开头会把无效输入也算上。
3. `"-5".isdigit()` 返回 `False`（不认负号）；`int("-5")` 正常返回整数 `-5`。所以用 `isdigit()` 校验会把合法的负数拒掉。
4. 原则上 `try` 只包住**可能抛出该异常的那一行**。范围放太大会误捕获——比如里面某处笔误导致的 `ValueError` 也会被当成「用户输入无效」，掩盖掉真正的 bug，排查时非常难找。

</details>
