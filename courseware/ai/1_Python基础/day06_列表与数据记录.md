---
kind: lesson
outline: [2, 2]
time: 30 分钟
uses: [列表, append(), 索引与切片, 可变与引用, continue]
record:
  - text: 当时的代码 Day5.py
    link: https://github.com/syjlpineapple/ai-learning/blob/main/dailypractice/Day5.py
---

# Day 6：把每一次猜测记下来

现在游戏能告诉你猜了几次，但说不出你猜了哪些数。要记住一串数，一个普通变量不够用，今天学 Python 最常用的容器：**列表**。

以后做 AI 应用，聊天记录、搜索结果、一批待处理的文本，都是用列表装的。

## 一、创建列表，往里加东西

```python
guess_history = []          # 空列表
guess_history.append(30)
guess_history.append(70)
guess_history.append(50)
print(guess_history)
print(len(guess_history))
```

```text
[30, 70, 50]
3
```

`[]` 是一个空列表。`.append(x)` 把 `x` 加到列表**末尾**，所以顺序就是你加进去的顺序。`len()` 告诉你里面有几个元素。

列表和计数器一样，要放在循环外面。放进循环会怎样？

```python
for guess in [30, 70, 50]:
    history = []            # 每轮都重新变成空列表
    history.append(guess)
print(history)
```

```text
[50]
```

前两次的记录都被清掉了，只剩最后一个。这是第三次遇到同一条规律了：随机数、计数器、列表，**要跨轮保留的东西都放在循环外面**。

## 二、按位置取元素

列表里每个元素都有一个位置编号，叫**索引**，从 0 开始：

```python
guess_history = [30, 70, 50]
print(guess_history[0], guess_history[2], guess_history[-1])
```

```text
30 50 50
```

`[0]` 是第一个，`[2]` 是第三个。`[-1]` 是倒数第一个，取最后一个元素时很常用。

三个元素的列表，合法的索引是 0、1、2。写 `guess_history[3]` 会报错：

```text
IndexError: list index out of range
```

## 三、切片：取一段

`列表[开始:结束]` 取出一段，**包含开始，不包含结束**：

```python
nums = [30, 70, 50, 60, 55]
print(nums[0:2])
print(nums[:3])
print(nums[-2:])
print(nums[1:100])
```

```text
[30, 70]
[30, 70, 50]
[60, 55]
[70, 50, 60, 55]
```

开始不写就是从头，结束不写就是到尾。`nums[-2:]` 是最后两个。最后一行结束位置超出了长度，切片不会报错，只是取到末尾为止。

「包含开始，不包含结束」和 `range()` 一样，和 `randint()` 不一样。

## 四、列表可以改，而且赋值不是复制

字符串造好了就不能改：

```python
s = "abc"
s[0] = "x"
```

```text
TypeError: 'str' object does not support item assignment
```

列表可以，`append` 就是在原地修改它。能改，就带来一个新问题：

```python
a = [30, 70]
b = a
b.append(50)
print(a)
print(b)
```

```text
[30, 70, 50]
[30, 70, 50]
```

只往 `b` 里加了 50，`a` 也变了。因为 `b = a` 没有复制出第二个列表，只是让 `b` 这个名字也指向**同一个**列表。两个名字，一个列表。

想要一份独立的副本，用 `.copy()`：

```python
c = a.copy()
c.append(99)
print(a)
print(c)
```

```text
[30, 70, 50]
[30, 70, 50, 99]
```

今天的作业用不到这一点，但它是列表最容易出错的地方，后面把列表传进函数时就会碰到。先记住：**`b = a` 是同一个列表，`a.copy()` 才是新的。**

## 五、`continue`：跳过这一轮

作业里会遇到「这次输入不合格，直接让用户重新输入」。`continue` 就是干这个的：结束**本轮**循环，回到 `while` 开头开始下一轮。

```python
if not 1 <= i_num <= 100:
    print("请输入 1 到 100 之间的整数")
    continue            # 下面的计数、记录都不执行
```

`1 <= i_num <= 100` 是 Python 特有的连写，意思是「`i_num` 在 1 到 100 之间」，前面加 `not` 就是「不在这个范围」。

它和 `break` 是一对：`continue` 跳过这一轮，`break` 结束整个循环。

## 六、今天的作业

在猜数字游戏里加一个猜测记录：

1. 创建空列表 `guess_history`
2. 每次输入有效整数后，把它加进列表
3. 输入无效内容时提示重新输入，**不要记录**
4. 猜对时显示全部猜测记录
5. 输入 `q` 退出时也显示
6. 保留之前的函数、次数统计

选做：退出时再显示猜过的「不同数字」，比如 `[30, 30, 50]` 里不同的是 `30` 和 `50`。可以查一下 `set()`。

## 七、小测

**1.** 下面的代码打印什么？

```python
a = [1, 2]
b = a
b.append(3)
print(len(a))
```

- A. `2`
- B. `3`

**2.** `[10, 20, 30, 40][1:3]` 是什么？

- A. `[10, 20, 30]`
- B. `[20, 30]`
- C. `[20, 30, 40]`

**3.** `.append()` 应该写在 `int()` 转换之前还是之后？

- A. 之前，先记下来再说
- B. 之后，转换成功才说明是有效输入

<details>
<summary>答案</summary>

1. B。`a` 和 `b` 是同一个列表，往 `b` 里加，`a` 也看得到。
2. B。从索引 1 开始，到索引 3 之前结束，也就是第二、第三个元素。
3. B。转换失败会跳进 `except`，不会走到 `append`，无效输入就进不了列表。

</details>

## 讲评（10-19）

你交的代码，一次通过：

```python
r_num = random.randint(1, 100)
print("随机数",r_num)
count = 0
guess_history = []
while True:
    i_num = input("请输入数字")
    if i_num == 'q':
        print(f"游戏退出：共输入{count}次")
        print("猜测记录:", guess_history)
        break
    try:
        i_num = int(i_num)
        count += 1
        guess_history.append(i_num)
        result = check_guess(i_num,r_num)
        print(result)
        if result == "正确":
            print("猜测记录:",guess_history)
            break
    except ValueError:
        print("输入无效，请输入正整数，退出请输入‘q’")
```

列表在循环外创建，`append` 紧跟在 `int()` 后面，两条退出路径都打印了记录，昨天的函数和类型注解也都保留着。答案设成 50，依次输入 `30`、`abc`、`70`、`50`：

```text
请输入数字30
小了
请输入数字abc
输入无效，请输入正整数，退出请输入‘q’
请输入数字70
大了
请输入数字50
正确
猜测记录: [30, 70, 50]
```

`abc` 没有混进记录。

还是 Day 4 那个老问题：提示说「正整数」，但代码没拦。依次输入 `-5`、`0`、`q`：

```text
请输入数字-5
小了
请输入数字0
小了
请输入数字q
游戏退出：共输入2次
猜测记录: [-5, 0]
```

两个不合规则的数被记下来，还算进了次数。用第五节的写法补上：`int()` 之后先检查范围，不在 1 到 100 就 `continue`，计数和 `append` 都放在检查后面。

另外留意两件事，明天会用到：

- `print("猜测记录:", ...)` 写了两遍。现在只有一行还能接受，明天要显示的统计项变成五项，就该抽成函数了。
- `count` 和 `len(guess_history)` 永远相等，等于同一件事记了两份。两份数据就得同步更新，哪天某个分支只改了一份，次数就对不上了，而且不会报错。能用 `len()` 算出来的，就不用再单独存一个 `count`。
