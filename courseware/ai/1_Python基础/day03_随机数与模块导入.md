---
kind: lesson
outline: [2, 2]
time: 25 分钟
uses: [import, random.randint, f-string, 变量放在循环外]
record:
  - text: 当时的代码 Day2.py
    link: https://github.com/syjlpineapple/ai-learning/blob/main/dailypractice/Day2.py
---

# Day 3：让程序自己出题

前两天的答案一直是 10。你自己写的程序，你当然知道答案，这样的游戏没法玩。

今天让程序在启动时随机想一个 1 到 100 之间的数，你来猜。为此要用到 Python 自带的一个工具箱：`random` 模块。

## 一、模块是什么

`print()`、`int()`、`input()` 这些函数随时能用，它们是**内置函数**。但 Python 自带的工具远不止这些，更多的工具按用途分装在不同的**模块**里：处理随机数的在 `random` 模块，处理 JSON 的在 `json` 模块。

模块要先导入才能用：

```python
import random

num = random.randint(1, 100)
```

`import random` 之后，`random` 这个名字就代表整个模块。要用模块里的函数，写成 `模块名.函数名`，比如 `random.randint`。

## 二、两种导入写法

另一种写法是只把需要的那个函数拿进来：

```python
from random import randint

num = randint(1, 100)
```

这时候直接写 `randint`，前面不带 `random.`。

两种写法都对，记住它们的区别：

| 写法 | 拿进来的是什么 | 之后怎么用 |
|---|---|---|
| `import random` | 整个模块 | `random.randint(1, 100)` |
| `from random import randint` | 模块里的 `randint` 函数 | `randint(1, 100)` |

初学时推荐第一种，读代码的人一眼就能看出 `randint` 来自哪个模块。

这里有个容易掉进去的坑。`random` 模块里恰好有一个函数也叫 `random`（返回 0 到 1 之间的小数）。所以：

```python
from random import random
print(random)
random.randint(1, 100)
```

```text
<built-in method random of Random object at 0x000001C69BE0CDC0>
AttributeError: 'builtin_function_or_method' object has no attribute 'randint'
```

第一行打印出来是一个 method（函数），不是模块。这说明 `from random import random` 拿进来的是那个函数，函数身上当然没有 `randint`。

## 三、`randint` 两端都能取到

`random.randint(1, 100)` 可能给出 1，也可能给出 100，两端都包含。我让 `randint(1, 3)` 跑了 1000 次，把出现过的数收集起来：

```text
[1, 2, 3]
```

3 也出现了。以后你还会常用 `range(1, 3)`，它不含右端，只有 `[1, 2]`。两个别混。

## 四、答案要在循环外面生成

这是今天最重要的一点。猜数字要循环，那 `randint` 写在 `while` 里面还是外面？

想一想写在里面会怎样：每进一轮循环，就重新抽一次答案。我连续调用了三次 `randint(1, 100)`：

```text
18
73
98
```

你第一次猜 50，程序说「猜小了」，可下一轮答案已经换了，刚才的提示全部作废，永远猜不中。

所以答案只抽一次，写在循环外面：

```python
random_num = random.randint(1, 100)   # 只抽一次

while True:
    ...                               # 每一轮都和同一个答案比
```

记住这个规律：**需要在每一轮之间保持不变的东西，放在循环外面。** 明天的计数器也是同一个道理。

## 五、把变量放进字符串：f-string

调试时你可能想把答案打出来看看。在字符串前面加一个 `f`，就可以在 `{}` 里直接写变量：

```python
random_num = 56
print(f"随机数：{random_num}")
print("随机数：", random_num)
print("随机数：{}", random_num)
print("随机数：{random_num}")
```

```text
随机数：56
随机数： 56
随机数：{} 56
随机数：{random_num}
```

前两种都对。第二种用逗号把两样东西交给 `print`，`print` 会在中间自动加一个空格。

后两种是常见错误，而且**都不报错**，只是输出不对：第三种的 `{}` 对 `print` 没有意义，原样打出来了；第四种漏了开头的 `f`，花括号和变量名也原样打出来了。

## 六、今天的作业

写一个猜数字游戏：

- 程序启动时随机生成一个 1 到 100 的数字
- 猜大了输出 `猜大了`，猜小了输出 `猜小了`，猜对了输出 `恭喜你，猜对了！` 并结束
- 输入 `q` 输出 `游戏结束`

动手前先回答自己：随机数在 `while` 外面生成，还是里面？

## 七、小测

**1.** 写了 `from random import randint` 之后，下面哪一行是对的？

- A. `random.randint(1, 100)`
- B. `randint(1, 100)`
- C. 两行都对

**2.** `random.randint(1, 100)` 能取到 100 吗？

- A. 能
- B. 不能，最大是 99

**3.** `print("答案是 {x}")` 会输出什么？

- A. 答案是 加上 x 的值
- B. `答案是 {x}`，原样输出
- C. 报错

<details>
<summary>答案</summary>

1. B。`from ... import` 只拿进来了 `randint`，`random` 这个名字并没有被定义，写 A 会报 `NameError`。
2. A。`randint` 两端都包含。
3. B。少了开头的 `f`，它只是一个普通字符串，不报错，原样输出。

</details>

## 讲评（10-17）

你一共交了两版。

**第一版**一运行就报错：

```python
from random import random

random_num = random.randint(1, 100)
print("随机数：{}",random_num)
while True:
    input_num = input("请输入数字")
    if input_num > random_num:
    ...
```

先说做对的：`random_num` 放在了 `while` 外面，今天最关键的一点你一开始就想对了。

报错的原因有三个，程序只会停在第一个上：

1. `from random import random` 拿进来的是函数，不是模块，所以第 3 行就报了 `AttributeError`，也就是第二节演示的那个错误
2. `print("随机数：{}", ...)` 不会替换 `{}`，会打出 `随机数：{} 56`
3. `input()` 拿到的是字符串，直接和整数比大小会报 `TypeError: '>' not supported between instances of 'str' and 'int'`

第 3 个是 Day 1 就讲过的事：`input()` 永远返回字符串。知道一件事，和写代码时想得起来，是两回事。这种错误多犯两次就记住了。

**第二版**三处都改对了，一次通过：

```python
import random

random_num = random.randint(1, 100)
print("随机数：",random_num)
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

你还把另一种打印写法留成了注释。学习阶段这个习惯很好，回头看能想起当时在比较什么。

剩下一个问题：作业要求输入 `q` 退出，这一版没做。`int()` 直接套在 `input()` 外面，输入 `q` 会这样：

```text
请输入数字:q
ValueError: invalid literal for int() with base 10: 'q'
```

Day 2 你用 `isdigit()` 先判断再转换，已经解决过这个问题，这里加随机数的时候把它丢了。明天的作业会把它补回来，顺便学一种更好的办法。

另外，`print("随机数：", random_num)` 是调试用的，正式游戏要删掉，不然答案就直接告诉玩家了。
