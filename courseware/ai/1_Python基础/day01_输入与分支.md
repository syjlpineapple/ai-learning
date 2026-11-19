---
kind: lesson
outline: [2, 2]
time: 20 分钟
uses: [input(), int() 类型转换, if / elif / else, 比较运算]
record:
  - text: 当时的代码 Day1.py
    link: https://github.com/syjlpineapple/ai-learning/blob/main/dailypractice/Day1.py
---

# Day 1：猜数字，从一次判断开始

这是整门课的第一天。我们从一个很小的程序开始：**猜数字**。之后的 89 天，这个小游戏会一点点长大，加上循环、函数、文件、网络请求、测试……一直长成一个真正的项目。

今天只做最简单的一步：用户输入一个数，程序告诉他大了还是小了。

## 一、程序怎么「听」用户说话

`input()` 让程序停下来，等用户在键盘上输入，回车以后把输入的内容交给你：

```python
text = input("请输入一个数字：")
```

这里有一个后面会反复遇到的细节：**`input()` 拿到的永远是字符串。** 用户敲的是 `7`，你拿到的是 `"7"`，一个字符，不是数字 7。

字符串不能和数字比大小。直接比会报错：

```text
TypeError: '>' not supported between instances of 'str' and 'int'
```

所以要先用 `int()` 把它转成整数：

```python
num = int(input("请输入一个数字："))
```

## 二、程序怎么「做决定」

`if / elif / else` 就是「如果……否则如果……否则……」：

```python
if num > 10:
    print("太大了")
elif num < 10:
    print("太小了")
else:
    print("猜对了！")
```

Python 会从上往下检查，**第一个成立的分支执行完就结束**，后面的不再看。三个分支里只会走一个。

注意两个 Python 的习惯：条件后面有冒号 `:`；分支里的代码要缩进（一般是 4 个空格），Python 靠缩进判断哪些代码属于这个分支。如果你学过 Java，这里没有花括号，缩进就是花括号。

## 三、今天的作业

写一个程序：用户输入一个数字，

- 大于 10，输出 `太大了`
- 小于 10，输出 `太小了`
- 等于 10，输出 `猜对了！`

挑战题：让程序一直让用户猜，直到猜中 10 为止。（不会也没关系，这是明天的内容。）

## 四、小测

**1.** 用户在 `input()` 里输入 `7`，程序拿到的是什么？

- A. 整数 7
- B. 字符串 `"7"`
- C. 浮点数 7.0

**2.** 下面的代码，输入 5 会打印几行？

```python
if num < 10:
    print("小于 10")
elif num < 20:
    print("小于 20")
```

- A. 一行
- B. 两行
- C. 不打印

<details>
<summary>答案</summary>

1. B。`input()` 拿到的永远是字符串，要比大小得先 `int()`。
2. A。5 满足第一个条件，打印「小于 10」以后就结束了，`elif` 不会再检查。

</details>

## 讲评（10-16）

你当时交的代码：

```python
input_num = int(input("请输入数字"))

if input_num > 10:
    print("输入的数字太大了")
elif input_num < 10:
    print("输入的数字太小了")
else:
    print("猜对了")
```

逻辑完全正确，一次就通过了。`input()`、`int()`、`if / elif / else`、比较运算，今天要用的四样都用上了。

一个小建议：提示文字后面加个冒号和空格，`input("请输入数字：")`，用户输入的内容就不会紧贴着提示了。

还有一件事你今天可能没碰到，但明天一定会碰到：如果用户输入的不是数字，比如 `q`，`int()` 会直接报错，程序退出：

```text
ValueError: invalid literal for int() with base 10: 'q'
```

这正是 Day 2 挑战题要解决的问题。
