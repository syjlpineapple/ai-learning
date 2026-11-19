---
kind: lesson
outline: [2, 2]
time: 45 分钟
uses: [raise, 异常层次, try 只包一行, from None, 测试异常]
record:
  - text: 当时的代码 Day9.py
    link: https://github.com/syjlpineapple/ai-learning/blob/main/dailypractice/Day9.py
---

# Day 9：让校验函数自己报错

昨天你测了 `check_num()`，它总会交回一个结果。今天把「校验输入」也拆成函数 `parse_guess()`：传进来一个字符串，合格就返回整数。

不合格的时候呢？它没有合适的值可以返回。这时候要让它**主动报错**，把问题交给调用它的人去处理。

## 一、`raise`：主动抛出异常

Day 4 你学的是接住别人抛出的异常，今天自己来抛：

```python
def check_range(n: int) -> int:
    if not 1 <= n <= 100:
        raise ValueError("数字必须在 1～100")
    return n

try:
    check_range(101)
except ValueError as e:
    print(e)
```

```text
数字必须在 1～100
```

`raise ValueError("...")` 造出一个 `ValueError`，括号里是说明文字。函数执行到 `raise` 就停了，后面的 `return` 不会执行。

调用的地方用 `except ValueError as e` 接住，`e` 就是那个异常，`print(e)` 打出的是说明文字。

为什么不在函数里直接 `print("数字必须在 1～100")`？和 Day 5 一个道理：函数只负责判断，出了错是提示一下、让用户重输，还是直接退出，由调用的地方决定。

## 二、异常也分家族

Python 的异常是一层一层继承下来的。每个异常类都有一个 `__mro__` 属性记着它的「家谱」，我把几个常见异常的家谱取出来，只留名字：

```text
ValueError ['ValueError', 'Exception', 'BaseException', 'object']
ZeroDivisionError ['ZeroDivisionError', 'ArithmeticError', 'Exception', 'BaseException', 'object']
FileNotFoundError ['FileNotFoundError', 'OSError', 'Exception', 'BaseException', 'object']
KeyboardInterrupt ['KeyboardInterrupt', 'BaseException', 'object']
```

从左往右读，是从自己一路到最上面的祖先。几乎所有「出错了」的异常都在 `Exception` 下面。用户按 Ctrl+C 产生的 `KeyboardInterrupt` 不在，所以 `except Exception` 接不住它，程序仍然能被 Ctrl+C 停下来。

这个家谱决定了一条规则：**`except` 接住一个异常，也会接住它的所有子孙。** 而且多个 `except` 是从上往下找，第一个对上的就用，后面的不再看：

```python
try:
    int("abc")
except Exception:
    print("被 except Exception 接住")
except ValueError:
    print("被 except ValueError 接住")
```

```text
被 except Exception 接住
```

`ValueError` 是 `Exception` 的子孙，被第一个 `except` 截走了，第二个永远轮不到。Python 不会对此报错或提醒。所以写多个 `except` 时，**具体的写在前面，宽泛的写在后面。**

## 三、`try` 只包住会出错的那一行

`parse_guess()` 里有两种错误：

- 格式错误：`"abc"` 转不成整数，`int()` 会抛 `ValueError`
- 范围错误：`"101"` 能转，但不在 1 到 100，你自己 `raise ValueError`

两种都是 `ValueError`。如果 `try` 把范围检查也包了进去，你自己抛出的范围错误，会被同一个 `try` 的 `except` 接住。

所以 `try` 只包 `int()` 这一行，范围检查放在 `try` 外面：

```python
def parse_guess(user_input: str) -> int:
    try:
        int_num = int(user_input)
    except ValueError:
        raise ValueError("输入格式错误，请输入整数") from None

    if not 1 <= int_num <= 100:
        raise ValueError("数字必须在 1～100")

    return int_num
```

拿四个输入试一下，左边是输入，右边是返回值或接住的异常说明：

```text
50 -> 50
abc -> 输入格式错误，请输入整数
101 -> 数字必须在 1～100
0 -> 数字必须在 1～100
```

两种错误各说各的。

## 四、异常链和 `from None`

上面 `except` 里抛出了一个新异常。新异常是在处理旧异常的时候产生的，Python 会把两个都记下来。如果没人接住，三种写法打出来的报错不一样。

**不加 `from`**：

```text
Traceback (most recent call last):
  ...
ValueError: invalid literal for int() with base 10: 'abc'

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  ...
ValueError: 输入格式错误，请输入整数
```

中间那句的意思是「处理上面那个异常的时候，又发生了另一个异常」。两个都打出来了。

**加 `from e`**（`e` 是接住的原异常）：中间那句变成 `The above exception was the direct cause of the following exception`，意思是「上面那个异常是下面这个的直接原因」。还是两个都打，但明确说了因果。

**加 `from None`**：

```text
Traceback (most recent call last):
  ...
ValueError: 输入格式错误，请输入整数
```

只剩你自己定义的那一个。`invalid literal for int()` 这种底层说明对玩家没有意义，`from None` 就是把它从报错里藏起来。

记住两点：

- `from None` 只改变**报错怎么显示**，异常照样抛出，调用的地方照样要接住
- 它只在 `except` 里面的 `raise` 上有意义，因为只有那里才有「正在处理的旧异常」可藏

## 五、测试「应该报错」的情况

`parse_guess("abc")` 不返回值，没法写 `assert parse_guess("abc") == ...`。要测的是「它确实报错了」：

```python
try:
    parse_guess("abc")
except ValueError:
    pass                                          # 报错了，符合预期
else:
    raise AssertionError("预期出现 ValueError")    # 没报错，测试失败
```

`try` 的 `else` 分支只在 `try` 里**没有发生异常**时执行。逻辑是反过来的：报错了就通过，没报错才失败。

`else` 不能省。我把 `parse_guess` 的范围检查删掉，再用一个没有 `else` 的测试去测 `"0"`：坏函数不报错，测试也一声不吭地通过了。

## 六、今天的作业

1. 写 `parse_guess(user_input: str) -> int`：`"1"`、`"50"`、`"100"` 返回整数；`"abc"`、`"0"`、`"101"` 抛 `ValueError`。函数里不用 `input()`、`print()`
2. 写一段调用它的代码：`q` 在调用 `parse_guess()` **之前**处理；`abc` 提示格式错误，`101` 提示范围错误
3. 写 `test_parse_guess()`：合法输入用 `assert 实际 == 预期`，非法输入用 `try / except / else`，最后调用它

想一想：为什么 `parse_guess()` 不应该自己打印「输入错误，请重试」？

## 七、小测

**1.** 下面的代码打印什么？

```python
try:
    int("abc")
except Exception:
    print("A")
except ValueError:
    print("B")
```

- A. `A`
- B. `B`
- C. `A` 和 `B`

**2.** `raise ValueError("...") from None` 之后，如果调用的地方没有 `try`，程序会怎样？

- A. 不报错，继续运行
- B. 照样报错退出，只是报错信息里看不到原来的异常

**3.** 测「应该抛异常」时，`try / except / else` 的 `else` 什么时候执行？

- A. 抛出了异常时
- B. 没有抛出异常时

<details>
<summary>答案</summary>

1. A。`ValueError` 是 `Exception` 的子孙，被第一个 `except` 接住，第二个不会再执行。
2. B。`from None` 只影响显示。
3. B。没抛异常说明被测函数有问题，所以在 `else` 里让测试失败。

</details>

## 讲评（10-21）

这一天你改了五版，是到目前为止最多的一天。每一版都解决了上一版的一个问题。

**第一版**把范围检查写进了 `try` 里面：

```python
def parse_guess(user_input: str) -> int:
    try:
        int_num = int(user_input)
        if not 1 <= int_num <= 100:
            raise ValueError("数字必须在 1～100")
        return int_num
    except ValueError:
        raise ValueError("输入格式错误")
```

```text
50 -> 50
abc -> 输入格式错误
101 -> 输入格式错误
```

101 的格式没有任何问题，却被说成「格式错误」。你自己抛出的范围错误，被下面那个 `except` 接住，换成了另一句话。错误提示把人往错的方向引，比不提示还糟。调用处 `parse_guess(input_num)` 也没有接返回值，算出来的整数直接丢了。

**第二版**去掉了 `try`，调用处改成 `guess = parse_guess(input_num)`。范围错误恢复正常，但 `abc` 打出来的是 Python 原来的英文说明：

```text
abc -> invalid literal for int() with base 10: 'abc'
101 -> 数字必须在 1～100
```

**第三版**让 `try` 只包住 `int()`，两种错误都有了中文提示。这就是第三节的写法。接着你问了 `from None` 是什么意思，也就是第四节的内容。

**第四版**开始写测试：

```python
def test_parse_guess() -> None:
    assert parse_guess("2")
    assert parse_guess("abc")
    assert parse_guess("1000")
```

三行都有问题。`assert parse_guess("2")` 只检查了「结果是真」，函数返回 3 也能过，Day 8 第四节讲的就是这种写法。后两行更直接，运行到 `parse_guess("abc")` 就抛出异常，整个测试停在这里：

```text
ValueError: 输入格式错误，请输入整数
```

`assert` 根本没机会判断。

**第五版**全改对了：

```python
def test_invalid_input() -> None:
    assert parse_guess("2") == 2
    assert parse_guess("50") == 50
    try:
        parse_guess("abc")
    except ValueError:
        pass
    else:
        raise AssertionError("预期出现 ValueError")
    ...
test_invalid_input()
```

合法输入比较了具体的值，三个非法输入都用了带 `else` 的结构，文件末尾也调用了测试函数，昨天漏掉的这一步这次没漏。我拿它测了一个删掉范围检查的坏版本：

```text
正确版本：通过
坏版本：AssertionError: 预期出现 ValueError
```

能抓住，测试是有效的。

两个小建议。一是三处失败提示都是「预期出现 ValueError」，真失败时不知道是哪个输入。写成「输入 0 时预期出现 ValueError」，一看就知道。二是函数名叫 `test_invalid_input`，里面却也测了合法输入，叫 `test_parse_guess` 更准确。
