---
kind: lesson
outline: [2, 2]
time: 45 分钟
uses: [pytest.mark.parametrize, pydantic BaseModel, ValidationError, "Field(ge, le)", strict 模式]
record:
  - text: 当时写的代码 Day23/
    link: https://github.com/syjlpineapple/ai-learning/tree/main/dailypractice/Day23
---

# Day 23：参数化测试与 pydantic 入门

11-17 你提过一个问题：测试是不是学得太多了。确实多了：Mock 和 fixture 学完，测试工具已经够用。所以今天只花 10 分钟补一个小工具，剩下的时间学一个以后几乎每天都会用到的东西：**pydantic**。

先记住一句话，今天的两部分就是围绕它展开的：**pytest 验证代码，pydantic 验证数据。**

## 一、参数化测试（约 10 分钟）

还是那个年龄校验函数：

```python
def validate_age(age: int) -> bool:
    return 0 <= age <= 120
```

想测 18、0、120、-1、121 这五个数，你可能会在一个测试里写五行 `assert`。能用，但有两个麻烦：数据多了测试会很长；而且第一行一失败，后面四行就不执行了，你只知道「有错」，不知道一共错了几个。

`@pytest.mark.parametrize` 的思路是：**测试函数只写一遍，数据单独列出来，每组数据各跑一次。**

```python
import pytest


@pytest.mark.parametrize(
    "age, expected",        # 参数名
    [
        (18, True),         # 每一组数据，按顺序对应上面的参数名
        (0, True),
        (120, True),
        (-1, False),
        (121, False),
    ],
)
def test_validate_age(age, expected):
    assert validate_age(age) is expected
```

用 `-v` 运行，你会看到五个独立的测试，方括号里就是那一组数据：

```text
test_validate_age[18-True] PASSED
test_validate_age[0-True] PASSED
test_validate_age[120-True] PASSED
test_validate_age[-1-False] PASSED
test_validate_age[121-False] PASSED
```

这里有个容易忽略的地方：**-1 和 121 这两组比前面三组更重要。** 我试过把函数故意写坏成 `return True`，不管多少岁都通过。只测 18、0、120 的话，测试照样全部通过，根本发现不了。能抓住这个错误的，正是那两组「应该失败」的数据。

## 二、pydantic（约 25 分钟，今天的重点）

### 为什么需要它

回想一下 Day 11 到 Day 14，你读历史记录文件的时候，是不是一个字段一个字段地写 `if` 检查：是不是列表、是不是整数、在不在范围里？以后数据会越来越多：用户提交的表单、接口返回的 JSON，还有大模型返回的 JSON。每次都手写这些检查，代码会被检查淹没。

pydantic 换了个思路：**你只用一个类写出「数据应该长什么样」，检查的事交给它。**

你可以把它想成小区门口的保安：数据想进来，先在门口按登记表核对一遍，不合格的当场拦下，并且告诉你哪一项不对。

### 第一个模型

```python
from pydantic import BaseModel


class User(BaseModel):
    name: str
    age: int
    email: str


user = User(name="jack", age=18, email="jack@email.com")
print(user.name)
print(user.age)
print(user.email)
```

```text
jack
18
jack@email.com
```

看起来和普通的类差不多，区别在于继承了 `BaseModel`：创建对象的那一刻，pydantic 已经按每个字段的类型检查过一遍了。

### 数据不对的时候

```python
from pydantic import ValidationError

try:
    User(name="jack", age="hello", email="jack@gmail.com")
except ValidationError as e:
    print(e)
```

```text
1 validation error for User
age
  Input should be a valid integer, unable to parse string as an integer [type=int_parsing, input_value='hello', input_type=str]
```

这段报错值得仔细读一遍，它说清楚了三件事：**哪个字段**（`age`）、**为什么不行**（不是合法的整数）、**收到的是什么**（`'hello'`）。比你自己写 `raise ValueError("格式错误")` 详细多了。

还有一点很贴心：如果有好几个字段同时不对，它会**一次全部列出来**，不会只告诉你第一个。

### 再加上范围

光检查类型还不够，年龄是整数，但 -5 岁显然不合理。用 `Field` 加上限制：

```python
from pydantic import BaseModel, Field


class User(BaseModel):
    name: str = Field(min_length=2, max_length=20)   # 长度 2 到 20
    age: int = Field(ge=0, le=120)                    # 0 到 120
    email: str
```

`ge` 是 greater than or equal（大于等于），`le` 是 less than or equal（小于等于），`gt` 是严格大于。这样，数据的规则就集中写在模型里了，不用散落在各处的 `if` 里。

我拿这个模型试了几个年龄，有两个结果你可能想不到：

- 传 `"18"`（字符串）能通过，pydantic 自动把它转成了整数 18
- 传 `True` 也能通过，而且变成了 **1**

第二个是不是很眼熟？Day 11-12 讲过，`bool` 是 `int` 的子类。pydantic 默认是「宽松模式」，能转就转。如果你希望只收真正的整数，加上 `strict=True`：

```python
age: int = Field(ge=0, le=120, strict=True)
```

这样 `"18"`、`True`、`18.0` 就都会被拦下来。

另外提醒一句，`email: str` 只检查它是不是字符串，`"不是邮箱"` 也能过。检查邮箱格式要用 `EmailStr`，还得另装一个包，等用到再说。

### 它在 AI 应用里站在哪

后面做 AI 应用时，pydantic 会出现在两个关口：

```text
用户提交的数据 → 【pydantic 检查】→ 交给大模型 → 大模型返回 JSON → 【pydantic 检查】→ 你的业务代码
```

第一个关口挡住用户乱填的数据，第二个关口挡住大模型「胡说八道」的格式。第二个关口是 Day 35 的内容，到时候今天学的模型会直接用上。

## 三、今天的作业

在 `dailypractice/Day23/` 下新建三个文件：

1. **`user_model.py`**：`User` 模型。`name` 是字符串，长度 2-20；`age` 是整数，0-120；`email` 是字符串
2. **`product_model.py`**：`ProductRequest` 模型。`product_name` 是字符串；`price` 是浮点数，必须大于 0；`platform` 是字符串
3. **`test_models.py`**：用参数化测试检查 `User` 的年龄。18、0、120 能创建成功；-1、121 要抛出 `ValidationError`（用 `pytest.raises(ValidationError)`）

还有一件小事：你的 `.venv` 里装了 pydantic，但根目录的 `pyproject.toml` 没写它。现在能用，换一台电脑就不行了。在 `dependencies` 里加一行 `"pydantic>=2.10"`。

写完运行：

```powershell
python -m pytest dailypractice/Day23 -v
```

把三个文件和运行结果发给我。如果有兴趣，在测试数据里加一组 `age=True`，猜猜它会成功还是失败，再跑一下看看你猜得对不对。

## 四、小测

**1.** `@pytest.mark.parametrize` 是做什么的？

- A. 自动生成 Python 类
- B. 用多组数据分别执行同一个测试函数
- C. 自动捕获异常

**2.** pydantic 模型为什么要继承 `BaseModel`？

- A. 让 Python 支持多线程
- B. 获得 pydantic 的数据校验能力
- C. 自动连接接口

**3.** `age: int = Field(ge=0, le=120)`，传入 `age=True` 会怎样？

- A. 报错，`True` 不是整数
- B. 通过，`age` 变成 1
- C. 通过，`age` 还是 `True`

<details>
<summary>答案</summary>

1. B。
2. B。
3. B。宽松模式会把 `True` 转成 1，因为 `bool` 是 `int` 的子类。想拒绝它，就加 `strict=True`。

</details>

## 讲评（11-17，你已经做到的部分）

你那天把两段演示都跑通了：`parametrize_test.py` 和 `pydantic_demo.py`。作业的三个文件还没开始写。

**`parametrize_test.py`** 运行结果：

```text
dailypractice/Day23/parametrize_test.py::test_validate_age[18-True] PASSED
dailypractice/Day23/parametrize_test.py::test_validate_age[0-True] PASSED
dailypractice/Day23/parametrize_test.py::test_validate_age[120-True] PASSED
3 passed
```

参数化的写法完全正确，而且你测了 0 和 120 这两个边界，这一点很好。只差一步：课上例子里的 `(-1, False)` 和 `(121, False)` 没写进去。就像前面说的，少了这两组，函数写成 `return True` 也照样 3 个全过。把它们补上，这个测试才真正有用。

另外有个小习惯：`age:int` 冒号后面加个空格写成 `age: int`，`(18,True)` 逗号后面也加空格。这是 Python 通行的写法，`ruff format` 可以帮你自动改。

**`pydantic_demo.py`** 运行结果和课上一模一样，`ValidationError` 也正确接住了：

```text
jack
18
jack@email.com
1 validation error for User
age
  Input should be a valid integer, unable to parse string as an integer [type=int_parsing, input_value='hello', input_type=str]
```

可以再往前走一小步：`print(e)` 是写给人看的。如果程序要知道「到底是哪个字段错了」，用 `e.errors()`，它返回一个列表，每一项里有 `loc`（哪个字段）、`type`（什么错误）、`msg`（说明）。写作业的测试时你可能会用到。

接下来把三个作业文件写完，发给我看。
