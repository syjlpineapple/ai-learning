---
kind: lesson
outline: [2, 2]
time: 30 分钟
uses: [计数器 +=, try / except, ValueError, 先校验再计数]
record:
  - text: 当时的代码 Day3.py
    link: https://github.com/syjlpineapple/ai-learning/blob/main/dailypractice/Day3.py
---

# Day 4：数一数猜了几次

昨天的游戏已经能玩了，但还缺两样东西：猜中以后告诉玩家一共猜了几次；玩家输入 `q` 或者 `abc` 时，程序不能崩。

今天就做这两件事。第二件会用到一个新工具 `try / except`，它比 Day 2 的 `isdigit()` 更可靠。

## 一、计数器

数次数的办法很朴素：先准备一个从 0 开始的变量，每猜一次加 1。

```python
count = 0
count = count + 1
count += 1          # 和上一行意思一样，更常用的简写
print(count)
```

```text
2
```

注意 Python 没有 `count++` 这种写法，要写 `count += 1`。

`count = 0` 放在哪里？回忆昨天的规律：需要在每一轮之间保持的东西，放在循环外面。如果放进循环，每一轮都会被重新设成 0。我模拟了一下，猜三次，第三次猜中：

```python
for guess in [50, 70, 63]:
    count = 0       # 放错了地方
    count += 1
    if guess == 63:
        print(f"猜对了，共猜了{count}次")
```

```text
猜对了，共猜了1次
```

明明猜了三次，却说只猜了一次。

## 二、`int()` 转不了的时候

`int("abc")` 会报错：

```text
ValueError: invalid literal for int() with base 10: 'abc'
```

报错的第一个词 `ValueError` 是**异常的类型**，冒号后面是具体说明。`ValueError` 的意思是「类型没问题（是字符串），但值不行（内容不是整数）」。

没人处理的异常会让程序直接退出。`try / except` 就是用来处理它的：

```python
for text in ["42", "abc"]:
    try:
        num = int(text)
        print("转换成功：", num)
    except ValueError:
        print("输入无效：", text)
```

```text
转换成功： 42
输入无效： abc
```

一步一步看它是怎么走的：

1. 先执行 `try` 里面的代码
2. 如果都顺利，`except` 整段跳过
3. 如果某一行抛出了 `ValueError`，`try` 里**剩下的代码不再执行**，直接跳到 `except`
4. `except` 执行完，程序接着往下走，不会退出

第 3 步是关键。`"abc"` 那一轮，`int()` 一失败，下面的 `print("转换成功")` 就被跳过了。这说明：**只有转换成功，`try` 里 `int()` 后面的代码才会执行。** 计数写在这里，无效输入自然就不会被算进去。

## 三、为什么比 `isdigit()` 好

Day 2 用的是「先检查再转换」：`isdigit()` 说是数字，才去 `int()`。今天换成「直接转换，失败了再处理」。拿几个输入对比一下：

| 输入 | `isdigit()` | `int()` |
|---|---|---|
| `"-5"` | `False` | `-5` |
| `"3.5"` | `False` | `ValueError` |
| `"abc"` | `False` | `ValueError` |

`isdigit()` 是你自己找来的一个「检查」，它的规则和 `int()` 的规则并不完全一样，`"-5"` 就被它冤枉了。而 `try / except` 直接问 `int()` 本人能不能转，答案一定准。

记住：**能不能转成整数，交给 `int()` 自己判断。**

## 四、今天的作业

在昨天的代码上继续改：

1. 每猜一次，次数加 1
2. 猜对后显示 `你一共猜了 N 次`
3. 输入 `q` 时显示退出提示并结束
4. 输入 `abc` 这类内容时提示重新输入，程序不能崩，**也不计入次数**

动手前想清楚三个问题：

- `count = 0` 放在循环里面还是外面？
- `count += 1` 放在哪一步之后？
- 为什么要先判断 `q`，再去 `int()`？

## 五、小测

**1.** 下面的代码，`text` 是 `"abc"` 时会打印什么？

```python
try:
    num = int(text)
    print("A")
except ValueError:
    print("B")
print("C")
```

- A. `A` 和 `C`
- B. `B` 和 `C`
- C. 只有 `B`

**2.** 「无效输入不计入次数」，`count += 1` 应该放在哪？

- A. 刚拿到输入就加
- B. `int()` 转换成功之后
- C. 猜对的时候再加

<details>
<summary>答案</summary>

1. B。`int("abc")` 失败，`print("A")` 被跳过，进入 `except` 打印 `B`；异常处理完，程序继续往下，打印 `C`。
2. B。转换成功才说明这是一次有效的猜测。

</details>

## 讲评（10-17）

你交了两版。

**第一版**用的还是 `isdigit()`：

```python
    if input_num == 'q':
        print(f"游戏退出：共输入{count}次")
        break
    else:
        count += 1
        if not input_num.isdigit():
            print("输入无效，请输入数字，退出请输入‘q’")
        elif int(input_num) < random_num:
            ...
```

两处做得好：`count` 和 `random_num` 都在循环外；先判断 `q` 再碰 `int()`，`int('q')` 的崩溃避开了。

问题出在 `count += 1` 的位置。它写在了「检查是不是数字」**之前**，所以 `abc` 也被算了一次。我把答案设成 63，依次输入 `abc`、`50`、`63`：

```text
请输入数字abc
输入无效，请输入数字，退出请输入‘q’
请输入数字50
猜小了
请输入数字63
猜对了，共猜了3次
```

有效的猜测只有两次。正确的顺序是：先判断 `q`，再确认是有效整数，**确认之后才计数**，最后比大小。

**第二版**你主动换成了 `try / except`。上一版讲评里只是顺带提了这个写法，说了今天不要求改，你还是自己动手改了：

```python
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

`count += 1` 紧跟在 `int()` 后面，转换失败就跳不到这里。同样的输入再跑一次：

```text
请输入数字abc
输入无效，请输入正整数，退出请输入‘q’
请输入数字50
猜小了
请输入数字63
猜对了，共猜了2次
```

次数对了，作业通过。

还有两个小地方。

一是转换完又写了两次 `int(input_num)`。第一行已经把它变成整数了，后面直接写 `input_num < random_num` 就行。多转一次不出错，但读代码的人会怀疑「这里是不是还可能是字符串」。

二是提示语说「请输入正整数」，代码却没检查。输入 `-5` 照样能进去：

```text
请输入数字-5
猜小了
请输入数字q
游戏退出：共输入1次
```

提示里承诺了的规则，代码就要做到。范围检查过两天会补上。
