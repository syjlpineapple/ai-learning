---
kind: lesson
outline: [2, 2]
time: 30 分钟
uses: [while True, break 与 exit(), str.isdigit(), 先判断再转换]
record:
  - text: 当时的代码 Day1.py
    link: https://github.com/syjlpineapple/ai-learning/blob/main/dailypractice/Day1.py
---

# Day 2：让它一直猜下去

昨天的程序只能猜一次，猜完就结束了。真正的猜数字游戏应该是：没猜中就接着猜，直到猜中为止。

今天就在昨天的代码上加一个循环。

## 一、`while`：只要条件成立，就一直做

```python
while 条件:
    要重复做的事
```

每做完一遍，Python 回到开头再看一次条件，成立就再做一遍，不成立就停下。

猜数字的情况有点特殊：我们不知道用户要猜几次，只知道「猜中了就停」。这时候常见的写法是先让它「永远循环」，在里面判断什么时候跳出来：

```python
while True:
    num = int(input("请输入数字："))
    if num > 10:
        print("太大了")
    elif num < 10:
        print("太小了")
    else:
        print("猜对了！")
        break           # 跳出循环
```

`break` 的意思是：**立刻结束当前这个循环**，接着执行循环后面的代码。

## 二、`break` 和 `exit()` 的区别

很多人第一次会用 `exit()` 来结束：

| | 结束什么 |
|---|---|
| `break` | 当前这个循环，循环后面的代码照常执行 |
| `exit()` | 整个程序，后面什么都不执行了 |

现在的程序很短，两者看不出区别。但以后循环后面可能还有事要做，比如打印「一共猜了几次」、保存成绩。用 `exit()` 的话，这些都执行不到了。所以**想结束循环，就用 `break`**。

## 三、用户输入 `q` 怎么办

挑战题要让用户输入 `q` 退出。问题来了：昨天说过，`int("q")` 会直接报错。

所以顺序要换一换：**先判断用户输入的是什么，再决定要不要转成数字。** 字符串有一个方法 `isdigit()`，可以判断它是不是全由数字组成：

```python
"123".isdigit()   # True
"abc".isdigit()   # False
```

思路就变成：

```text
用户输入
  ├─ 是数字 → 转成 int → 和 10 比大小
  └─ 不是数字 → 是 q 吗？是就退出
```

## 四、今天的作业

1. 把昨天的程序改成：没猜中就一直让用户重新输入，猜中了结束
2. 挑战题：用户输入 `q` 时，输出 `游戏结束！` 并退出

先自己想清楚两个问题再动手：什么时候继续循环？什么时候停下来？

## 五、小测

**1.** `break` 结束的是什么？

- A. 整个程序
- B. 当前这个循环
- C. 当前这一个 `if`

**2.** 为什么判断 `q` 要放在 `int()` 之前？

- A. 因为 `int("q")` 会报错
- B. 因为 `q` 比数字重要
- C. 没有原因，放后面也一样

<details>
<summary>答案</summary>

1. B。程序会接着执行循环后面的代码。`exit()` 才是结束整个程序。
2. A。`int("q")` 会抛出 `ValueError`，程序直接崩溃，根本走不到后面的判断。

</details>

## 讲评（10-16）

那天你一共交了三版，每一版都往前走了一步。

**第一版**用 `while 1` 加 `exit(0)`，能正常工作。`while 1` 和 `while True` 效果一样，但 `while True` 一眼就能看出意思，Python 里更常用。

**第二版**开始处理「输入可能不是数字」，这一步很重要。不过写成了这样：

```python
from pydantic.v1.validators import Number
...
if input_num is Number:
```

这里有两个问题。一是 `is` 判断的是「是不是同一个对象」，不是「是不是某种类型」，`"5" is Number` 永远是 `False`。二是为了一个判断，引入了一个完全用不着的第三方库。判断是不是数字，字符串自带的 `isdigit()` 就够了。

**第三版**用上了 `isdigit()`，先判断再转换，挑战题完成：

```python
while 1:
    input_num = input("请输入数字")

    if input_num.isdigit():
        input_num = int(input_num)
        if input_num > 10:
            print("输入的数字太大了")
        elif input_num < 10:
            print("输入的数字太小了")
        else:
            exit(0)
    else:
        if input_num == 'q':
            exit(0)
```

剩下的就是把两个 `exit(0)` 换成 `break`，原因前面说过了。

### 回头再看：`isdigit()` 不是万能的

整理的时候我把 `isdigit()` 拿各种输入试了一遍，有几个结果值得知道：

| 输入 | `isdigit()` | `int()` |
|---|---|---|
| `"-5"` | `False` | `-5` |
| `" 7"`（前面有空格） | `False` | `7` |
| `"７"`（全角数字） | `True` | `7` |
| `"²"`（上标的 2） | `True` | **报错** |

前两行是「明明是合法数字却被拦下了」：负数、带空格的输入，`isdigit()` 都说不是。最后一行反过来，`isdigit()` 说是，`int()` 却转不了，程序照样崩溃。

现在的猜数字只收 1 到 100，用 `isdigit()` 够用。但它只是「看起来像数字」的粗略检查，不是可靠的校验。更稳的做法是直接 `int()`，转不了就接住报错，这是 Day 4 要学的 `try / except`。
