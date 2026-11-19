---
kind: lesson
outline: [2, 2]
time: 30 分钟
uses: [def, return, return 与 print, 先定义后调用, 类型注解]
record:
  - text: 当时的代码 Day4.py
    link: https://github.com/syjlpineapple/ai-learning/blob/main/dailypractice/Day4.py
---

# Day 5：把判断大小拆成一个函数

到昨天为止，所有代码都写在一个 `while` 循环里：拿输入、转换、计数、比大小、打印提示，全挤在一起。现在还能看懂，再加几个功能就乱了。

今天学**函数**：把「判断猜大猜小」这件事单独拿出来，起个名字，用的时候叫它一声。

## 一、定义和调用

```python
def add(a, b):
    return a + b

result = add(3, 5)
print(result)
print(add(result, 10))
```

```text
8
18
```

逐个看：

- `def` 表示「我要定义一个函数」，`add` 是它的名字
- `a`、`b` 是**参数**，调用时传进来的值会放进这两个名字里
- `return` 把结果交还给调用的地方

`add(3, 5)` 这一整个表达式，最后就变成了 `8`，可以存进变量，也可以接着拿去算。

## 二、`return` 和 `print` 不一样

很多人第一次写函数，会在里面直接 `print`：

```python
def add(a, b):
    print(a + b)

result = add(3, 5)
print(result)
```

```text
8
None
```

屏幕上确实出现了 8，但 `result` 是 `None`。函数没有 `return`，就什么也没交出来，Python 默认给的是 `None`。

这说明：**屏幕上看到了值，不等于程序拿到了值。** 一句话记住：`print` 是给人看的，`return` 是给程序后面的代码用的。

## 三、先定义，再调用

Python 从上往下一行一行执行，`def` 也是其中一行。执行到 `def` 那一行，函数才真正存在。

所以如果调用写在上面、`def` 写在下面，运行到调用那一行时，Python 还不认识这个名字，会报：

```text
NameError: name 'check_guess' is not defined
```

规矩很简单：**函数定义写在文件上面，主程序写在下面。**

## 四、函数只负责判断

今天要写的函数是这样的：

```python
def check_guess(input_num, random_num):
    if input_num < random_num:
        return "小了"
    elif input_num > random_num:
        return "大了"
    else:
        return "正确"
```

它只做一件事：比较两个数，把结果交出去。它不打印，也不负责结束游戏，这些留给主程序：

```python
result = check_guess(i_num, r_num)
print(result)
if result == "正确":
    break
```

为什么不让函数自己打印？最直接的好处是，不启动游戏也能检查它对不对：

```python
print(check_guess(5, 10))
print(check_guess(15, 10))
print(check_guess(10, 10))
```

```text
小了
大了
正确
```

三行就验证完了，不用一遍遍手敲数字。如果函数里写死了 `print`，结果只能去屏幕，别的代码拿不到，这样检查就做不了。

## 五、类型注解

参数和返回值可以标上类型：

```python
def check_guess(input_num: int, random_num: int) -> str:
```

`input_num: int` 表示这个参数应该是整数，`-> str` 表示函数应该返回字符串。

注意，这只是**说明**，Python 运行时不会检查：

```python
def add(a: int, b: int) -> int:
    return "hello"

print(add(1, 2))
```

```text
hello
```

说好返回整数，实际返回了字符串，照样运行。注解是写给人和编辑器看的：读代码的人不用看函数体就知道它吃什么、吐什么；编辑器（比如 PyCharm）能据此提示你明显的类型错误。不是必须写，但从现在开始养成习惯，成本很低。

## 六、今天的作业

把猜数字游戏里判断大小的部分拆成函数 `check_guess(input_num, random_num)`：

- 猜小了返回 `"小了"`，猜大了返回 `"大了"`，猜对了返回 `"正确"`
- 主循环调用它，根据返回值打印提示、决定要不要结束
- 保留随机数、次数统计、输入 `q` 退出
- `check_guess()` 只负责判断，不打印，也不负责退出游戏

交作业时想一想：如果以后要让 `check_guess()` 还能判断数字是否在 1 到 100 之间，下面哪种设计更好？

- A. 在 `check_guess()` 里面打印所有提示
- B. 让 `check_guess()` 返回判断结果，由主程序决定怎么处理

## 七、小测

**1.** 下面代码中 `x` 的值是什么？

```python
def f():
    print(1)

x = f()
```

- A. `1`
- B. `None`
- C. 报错

**2.** `def add(a: int, b: int) -> int` 被调用成 `add("a", "b")`，会怎样？

- A. Python 报类型错误
- B. 正常运行，返回 `"ab"`

<details>
<summary>答案</summary>

1. B。屏幕上会打印 1，但函数没有 `return`，交出来的是 `None`。
2. B。类型注解不做运行时检查，两个字符串相加得到 `"ab"`。

</details>

## 讲评（10-18）

你交的代码：

```python
import random

r_num = random.randint(1, 100)
print("随机数",r_num)
count = 0

while True:
    i_num = input("请输入数字")
    ...
    try:
        i_num = int(i_num)
        count += 1
        result = check_guess(i_num,r_num)
        print(result)
        if result == "正确":
            break
    except ValueError:
        print("输入无效，请输入正整数，退出请输入‘q’")

def check_guess(input_num ,random_num):
    if input_num < random_num:
        return "小了"
    ...
```

函数本身写得对：参数接对了，用的是 `return` 而不是 `print`，`break` 留在了主程序里。今天的要求都做到了。

问题只有一个：`def` 写在了循环后面。我把答案设成 63，先输入 `abc`，再输入 `50`：

```text
请输入数字abc
输入无效，请输入正整数，退出请输入‘q’
请输入数字50
NameError: name 'check_guess' is not defined
```

有意思的是，输入 `abc` 和 `q` 都能正常走完，只有输入一个有效数字、真正去调用函数时才崩。`except ValueError` 也接不住它，因为这是 `NameError`，不是 `ValueError`。这类错误藏在某一条路径里，只试一两种输入很容易漏掉。

把 `def` 挪到 `import random` 下面就好了。

设计题你选了 B，理由是：「如果用 A，要三个位置都要加，而且函数是需要比较返回结果，调用处决定是否需要打印。」完全正确。你说的就是**职责分离**：函数负责算，调用的地方负责怎么展示。以后结果要显示在网页上、写进日志，B 这个函数一个字都不用改。

最后你问了一句：「函数返回类型不需要定义吗？」这引出了第五节的类型注解。最终的 `Day4.py` 你给函数加上了注解：

```python
def check_guess(input_num:int ,random_num:int) -> str:
```

一个小建议：冒号后面空一格，逗号前面不空，写成 `input_num: int, random_num: int`，这是 Python 通行的写法。

还有一个现在不用改、但值得留意的地方：主程序靠 `result == "正确"` 判断结束。哪天你想把返回值改成「猜中了」，就得同时改函数和这行比较，漏改一处，游戏就永远不会结束，而且不报错。
