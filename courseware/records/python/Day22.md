# Day 22 · pytest Fixture 与测试资源管理

> **学习日** 2026-11-13（11:47 - 14:03，3 轮迭代）
> **对应代码** [`dailypractice/Day22/`](../../../dailypractice/Day22/)（`api_client.py` / `test_api_client.py`）
> **原始对话** `courseware/_raw/markdown/11_Python每日练习出题 (3).md`（对话里称「Day 22」）

> **A 线最后一节。** 从 Day01 的 `input()` 到这里的 fixture，同一个「猜数字」项目演化成了带配置管理、
> HTTP 客户端和单元测试的小型工程。整条线的回顾见 [`python/README.md`](README.md)。

## 本节掌握

- `@pytest.fixture` 的作用与**参数名自动注入**机制
- `yield` 把 fixture 分成 setup 和 teardown 两段
- 测试失败时 teardown **仍然会执行**
- `pytest.raises()` 取代手写的 `assert False`
- 为什么 `test_call_close` **不能**用这个 fixture
- 测试的标准结构：Arrange-Act-Assert
- **`/` 运算符在 `str` 和 `Path` 上的区别**（以及用 `Path` 拼 URL 为什么也是错的）
- Mock 的返回值是真实对象时，不再有 Mock 的宽容特性

---

# 第一部分 · 知识讲解

## 1. 为什么需要 Fixture

Day21 的三个测试都以同样两行开头和结尾：

```python
def test_post_success():
    client = APIClient("https://example.com", "test_key")   # 重复
    ...
    client.close()                                          # 重复

def test_post_fail():
    client = APIClient("https://example.com", "test_key")   # 重复
    ...
    client.close()                                          # 重复
```

三个测试重复两次还能忍，几十个测试就不行了。更麻烦的是：**每个测试都要自己记得清理资源**，漏写一个就泄漏一个 Session。

Fixture 就是把「测试前的准备」和「测试后的清理」提取出来统一管理。

## 2. `@pytest.fixture` 与参数名注入

```python
import pytest

@pytest.fixture
def user():
    return {"id": 1, "name": "jack"}


def test_user(user):            # ← 参数名和 fixture 名一致
    assert user["id"] == 1
```

**注意 `test_user(user)` 里的 `user` 不需要你传。** pytest 看到测试函数有个参数叫 `user`，就去找同名的 fixture，调用它，把返回值作为参数传进来。

这个机制叫**依赖注入**：测试函数只声明「我需要一个 user」，由框架负责提供。好处是测试函数不关心这个对象怎么造出来的——以后改造方式只动 fixture。

> 代价是**可读性有点隐式**：第一次看到 `def test_user(user)` 会疑惑这个参数从哪来。所以 fixture 的名字要起得能自解释，而且通常放在文件顶部或 `conftest.py` 里（Day21 遇到的那个 `conftest.py` 就是放共享 fixture 的地方）。

## 3. `yield`：把 fixture 切成两段

这是本节最重要的知识点。

```python
@pytest.fixture
def api_client():
    client = APIClient("https://example.com", "test_key")   # ① 测试前

    yield client                                            # ② 把它交给测试函数

    client.close()                                          # ③ 测试后
```

执行顺序：

| 阶段 | 执行什么 |
|---|---|
| 测试开始前 | `yield` **之前**的代码（setup） |
| 测试进行中 | 测试函数拿到 `yield` 出去的那个对象 |
| 测试结束后 | `yield` **之后**的代码（teardown） |

**关键保证：即使测试函数抛了异常、断言失败，`yield` 后面的清理代码也会执行。** 这和 `finally` 的保证一样，所以 fixture 适合管理数据库连接、HTTP Session、临时文件这类需要释放的资源。

Day22 的写法更保险，显式加了 `try/finally`：

```python
@pytest.fixture
def api_client():
    client = APIClient("https://example.com", "test_key")
    try:
        yield client
    finally:
        client.close()
```

严格说 pytest 本身就保证了清理会执行，但写上 `try/finally` 的好处是**意图明确**，而且万一 fixture 以后被当普通生成器用，行为也正确。

> 对比一下三种资源清理的写法，它们解决的是同一个问题：
>
> | 写法 | 场景 |
> |---|---|
> | `with open(...)` | 单个语句块内的资源（Day11） |
> | `try/finally` | 手动控制生命周期（Day20 的 `main`） |
> | fixture 的 `yield` | 跨多个测试复用的资源（本节） |

## 4. Fixture 的作用域

默认每个测试函数都会重新执行一次 fixture（每个测试拿到独立的新对象）。可以改：

```python
@pytest.fixture(scope="module")
def api_client():
    ...
```

| scope | 多久创建一次 |
|---|---|
| `function`（默认） | 每个测试函数一次 |
| `class` | 每个测试类一次 |
| `module` | 每个测试文件一次 |
| `session` | 整个测试会话一次 |

**默认值是对的选择**：每个测试拿到全新的对象，测试之间不会相互污染（Day12 讲的「测试隔离」）。只有在创建成本很高时（启动数据库容器、加载大模型）才改成更大的 scope，代价是要自己保证测试不会互相干扰。

## 5. `pytest.raises()`

Day21 测异常用的是手写模式：

```python
try:
    client.post("/users", {"name": "jack"})
    assert False, "应该抛出 HTTPError"
except requests.exceptions.HTTPError:
    pass
```

Day22 换成：

```python
with pytest.raises(requests.exceptions.HTTPError):
    api_client.post("/users", {"name": "jack"})
```

好处有三个：

- **意图直接写在 `with` 上**，一眼看出在测什么
- **不会因为漏写 `assert False` 而变成假测试**——这是手写模式最容易出的错（Day07、Day10、Day11 都踩过）
- 可以顺便检查异常内容：

```python
with pytest.raises(requests.exceptions.HTTPError) as exc_info:
    api_client.post("/users", {})
assert "500" in str(exc_info.value)
```

还能用正则匹配消息：`pytest.raises(ValueError, match="必须在 1~100")`。

> 但要注意 Day14 的教训：**用消息文本断言会把测试和文案焊死**。更稳的是断言异常类型，必要时才检查消息。

## 6. 为什么 `test_call_close` 不能用这个 fixture

这是个容易忽略的细节。

```python
def test_call_close(api_client):        # ← 如果用 fixture
    api_client.session.close = MagicMock()
    api_client.close()
    api_client.session.close.assert_called_once()
    # fixture 的 teardown 又会调用一次 close()
```

问题在于 **fixture 自己的 teardown 也会调 `client.close()`**。虽然断言在 teardown 之前执行所以这次能通过，但语义上已经混乱了：这个测试要验证「close 只被调用一次」，而测试环境本身就会多调一次。

所以这个测试应该**独立创建 client**：

```python
def test_call_close(api_client):
    client = APIClient("https://example.com", "test_key")   # 自己造一个
    client.session.close = MagicMock()
    client.close()
    client.session.close.assert_called_once()
```

> 一般规律：**当被测行为和 fixture 的清理动作是同一件事时，不能用那个 fixture。** 否则你测的是自己布置的环境，不是被测代码。

## 7. 测试的标准结构：Arrange-Act-Assert

当时那个「把两行代码放到断言之前」的调整，背后是测试代码的标准三段结构：

| 阶段 | 做什么 | 本节对应 |
|---|---|---|
| **Arrange**（准备） | 构造输入、替换依赖 | 创建 `mock_response`、替换 `session.post` |
| **Act**（执行） | 调用被测代码**一次** | `resp = api_client.post(...)` |
| **Assert**（验证） | 检查结果和行为 | `assert resp == ...`、`assert_called_once_with(...)` |

顺序不能乱，原因很实际：

- Mock 必须在调用之前替换好，否则被测代码用的还是真实依赖
- 断言必须在调用之后，否则什么都还没发生
- **「执行」只应该有一次**，否则 `assert_called_once` 之类的次数断言会失败

这三段之间通常空一行隔开，读测试时一眼能分清「什么是环境、什么是被测对象、什么是期望」。

---

# 第二部分 · 当天的练习

## 一、题目

把 Day21 的三个测试改用 fixture 组织：写 `api_client` fixture（`yield` + 自动关闭）、用它重写成功和失败两个测试、失败测试改用 `pytest.raises()`、`test_call_close` 独立创建 client。

三道理解题的回答全部正确：

| 题目 | 答案 |
|---|---|
| `@pytest.fixture` 的作用 | B. 为测试函数提供可复用的测试数据或资源 |
| `yield` 前后的代码何时执行 | C. 前者测试前，后者测试结束后 |
| 为什么要在 `yield` 后 `close()` | B. 自动释放资源，避免泄漏 |

## 二、那个 `/` 运算符的 bug

提交的 `api_client.py` 里有这一行：

```python
url = self.base_url/path         # ← 两个字符串相除
```

实测报错：

```text
TypeError: unsupported operand type(s) for /: 'str' and 'str'
```

### 为什么会这么写

因为 Day18-19 刚用过 `pathlib`：

```python
BASE_DIR / ".env"                # 这是合法的
```

**`Path` 重载了 `/` 运算符**（实现了 `__truediv__`），所以用斜杠拼路径非常自然。但 `str` 没有这个方法：

```python
hasattr(str, "__truediv__")      # False
hasattr(Path, "__truediv__")     # True
```

于是把 pathlib 的习惯带到字符串上就报错了。正解是 f-string：

```python
url = f"{self.base_url}/{path.lstrip('/')}"
```

### 顺带一个发现：用 `Path` 拼 URL 同样是错的

既然 `Path` 支持 `/`，那把 base_url 转成 `Path` 行不行？实测：

```python
Path("https://example.com") / "users"
# WindowsPath('https:/example.com/users')
```

**`https://` 变成了 `https:/`**——双斜杠被压缩掉了。因为 `Path` 是为**文件系统路径**设计的，它会规范化连续的分隔符，而 URL 的 `//` 是协议部分的必要组成。

所以 `Path` 只能拼文件路径，不能拼 URL。URL 拼接要么用 f-string，要么用标准库的 `urllib.parse.urljoin`。

> 这个 bug 的价值在于它展示了**运算符重载的边界**：`/` 的含义取决于左边对象的类型。
> 同一个符号在不同类型上含义不同，这已经是第三次遇到了——
> Day14 的按位或、Day16 的类型联合、这里的路径拼接。

## 三、另外两个问题

### 一、断言写到了函数外面

PyCharm 报「未解析的引用 `mock_response`」。原因是缩进不对，断言跑到了 `test_success()` 函数外面，而 `mock_response` 是函数内的局部变量。

调整后的理解是对的：**先准备 Mock，再执行被测代码，最后验证结果**——也就是上面说的 AAA 结构。

### 二、要区分静态检查提示和实际运行错误

PyCharm 还报了「在 'function' 中找不到引用 'session'」。这一条和上面那条性质不同：**`self.session` 确实存在，只是 PyCharm 无法从类型推断出动态赋值的属性。**

| 提示 | 性质 | 怎么办 |
|---|---|---|
| 未解析的引用 `mock_response` | **真问题**——变量确实不在作用域内 | 修代码 |
| 找不到引用 `session` | **静态分析的局限**——运行时存在 | 可以忽略 |

> 这个区分很重要：IDE 的红波浪线不等于代码有错。判断方法是**实际跑一遍**——
> 能跑通就是静态分析的局限，跑不通才是真问题。
> 反过来也成立：没有红波浪线也不代表代码对（Day15 那个死分支 IDE 就没提示）。

## 四、最终代码

```python
from unittest.mock import MagicMock

import pytest
import requests

from dailypractice.Day22.api_client import APIClient


@pytest.fixture
def api_client():
    client = APIClient("https://example.com", "test_key")
    try:
        yield client
    finally:
        client.close()


def test_success(api_client):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"id": 1, "email": "abc@gmail.com"}
    api_client.session.post = MagicMock(return_value=mock_response)

    resp = api_client.post("/user_info", {"name": "jack"})

    mock_response.raise_for_status.assert_called_once()
    api_client.session.post.assert_called_once_with(
        "https://example.com/user_info",
        json={"name": "jack"},
        timeout=10,
    )
    assert resp == {"id": 1, "email": "abc@gmail.com"}


def test_post_fail(api_client):
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = (
        requests.exceptions.HTTPError("500 Server Error")
    )
    api_client.session.post = MagicMock(return_value=mock_response)

    with pytest.raises(requests.exceptions.HTTPError):
        api_client.post("/users", {"name": "jack"})


def test_call_close(api_client):
    client = APIClient("https://example.com", "test_key")
    client.session.close = MagicMock()
    client.close()
    client.session.close.assert_called_once()
```

实测运行结果：

```text
dailypractice/Day22/test_api_client.py::test_success PASSED       [ 33%]
dailypractice/Day22/test_api_client.py::test_post_fail PASSED     [ 66%]
dailypractice/Day22/test_api_client.py::test_call_close PASSED    [100%]
3 passed in 0.26s
```

**这是 A 线第一份在 pytest 下真正跑起来、且全部通过的测试文件**（对比 Day10 那个 `collected 0 items`）。

## 五、现在回头看

### 一、曾经有一行 `assert resp.status_code == 200`

迁移到独立仓库时删掉了这行（仓库 `README.md` 的迁移记录里有），因为它会抛 `AttributeError`。实测：

```python
mock_response.status_code = 200
mock_response.json.return_value = {"id": 1, "email": "abc@gmail.com"}

resp = mock_response.json()        # {'id': 1, 'email': 'abc@gmail.com'}，类型是 dict
resp.status_code                   # AttributeError: 'dict' object has no attribute 'status_code'
```

**原因是搞混了两个对象：**

| 对象 | 是什么 | 有 `status_code` 吗 |
|---|---|---|
| `mock_response` | MagicMock | 有（自己设的） |
| `resp = api_client.post(...)` | `response.json()` 的结果，**真实 dict** | 没有 |

`APIClient.post()` 返回的是解析后的数据，不是 `Response` 对象。想验证状态码得断言在 `mock_response` 上。

> 这里有个一般性的认识：**Mock 的宽容只限于 Mock 对象本身。**
> 一旦 `return_value` 设成了真实对象（这里是 dict），从它身上取属性就按真实类型的规则来，
> 该报 `AttributeError` 就报。所以「用了 Mock 就不会有类型错误」是错觉。

现在代码里留着 `mock_response.status_code = 200`，但没有任何断言用它——属于无用赋值，可以删，或者改成断言 `mock_response.status_code == 200`（不过那只是在验证自己刚设的值，没有意义）。

### 二、`test_call_close` 接收了 fixture 但没用它

```python
def test_call_close(api_client):        # ← 参数 api_client 没被使用
    client = APIClient(...)             # 自己又造了一个
```

函数体里没用到 `api_client`，但声明了这个参数，所以 fixture 照样会执行（创建一个 client、测试后关掉它）。**白创建了一个对象。**

去掉这个参数即可：

```python
def test_call_close():
    client = APIClient("https://example.com", "test_key")
```

独立创建的决定是对的（见知识讲解第 6 节），只是参数忘了删。

### 三、`__init__` 的参数名叫 `test_key`

```python
def __init__(self, base_url, test_key):          # Day22
def __init__(self, base_url: str, api_key: str): # Day20
```

Day20 叫 `api_key`，Day22 改成了 `test_key`。这个名字把「测试用的密钥」这个使用场景写进了生产代码的接口里——和 Day18 那个 `API_KEY_TEST` 是同一类问题。参数名应该描述**它是什么**（API 密钥），而不是**谁在用它**。

另外这一版的 `__init__` 还丢了类型标注（Day20 有）。

### 四、`post()` 没有返回类型标注

Day20 是 `-> Any`，Day22 没写。

## 六、复习自测

1. `def test_user(user)` 里的 `user` 参数是谁传进来的？
2. fixture 里 `yield` 前后的代码分别在什么时候执行？测试失败时后半段还会执行吗？
3. fixture 的默认 scope 是什么？为什么这个默认值是合理的？
4. `pytest.raises()` 比手写 `try/except` + `assert False` 好在哪？
5. 为什么验证「close 只被调用一次」的测试不能用那个 `api_client` fixture？
6. 测试代码的 Arrange-Act-Assert 三段，顺序为什么不能乱？
7. `"a" / "b"` 会怎样？`Path("a") / "b"` 呢？为什么有这个区别？
8. 用 `Path` 拼接 `https://example.com` 和 `users` 会得到什么？为什么不能用它拼 URL？
9. `mock_response.status_code = 200` 之后，`api_client.post(...)` 的返回值上有 `status_code` 吗？
10. IDE 报「未解析的引用」一定说明代码有错吗？怎么判断？

<details>
<summary>参考答案</summary>

1. pytest 传的。它看到测试函数有个参数名和某个 fixture 同名，就自动调用那个 fixture 并把返回值注入进来——这叫依赖注入。
2. `yield` 之前是 setup（测试开始前执行），之后是 teardown（测试结束后执行）。**即使测试抛异常或断言失败，teardown 仍然会执行**，和 `finally` 的保证一样。
3. 默认 `function`，每个测试函数都重新创建。合理是因为保证了测试隔离——每个测试拿到全新对象，不会被别的测试污染。
4. 意图直接写在 `with` 上更清楚；不会因为漏写 `assert False` 而变成永远通过的假测试；还能用 `exc_info` 或 `match=` 顺便检查异常内容。
5. 因为 fixture 的 teardown 自己会调 `client.close()`，而这个测试要验证的恰好是「close 被调用了几次」——测试环境会干扰被测行为。规律是：被测行为和 fixture 的清理动作相同时，不能用那个 fixture。
6. Mock 必须在调用被测代码之前替换好，否则用的还是真实依赖；断言必须在调用之后，否则什么都没发生；而「执行」只能一次，否则次数类断言会失败。
7. `"a" / "b"` 抛 `TypeError`——`str` 没有实现 `__truediv__`。`Path("a") / "b"` 正常，因为 `pathlib.Path` 重载了 `/` 运算符。
8. 得到 `https:/example.com/users`——**双斜杠被压缩成了单斜杠**。因为 `Path` 是为文件系统路径设计的，会规范化连续分隔符，而 URL 的 `//` 是协议部分必需的。拼 URL 要用 f-string 或 `urllib.parse.urljoin`。
9. 没有。`post()` 返回的是 `response.json()` 的结果，也就是一个**真实的 dict**，dict 没有 `status_code` 属性，访问会抛 `AttributeError`。`status_code` 在 `mock_response` 上。
10. 不一定。「未解析的引用 `mock_response`」是真问题（变量确实不在作用域内）；「找不到引用 `session`」是静态分析的局限（运行时确实存在）。判断方法是实际跑一遍。反过来，没有警告也不代表代码对。

</details>
