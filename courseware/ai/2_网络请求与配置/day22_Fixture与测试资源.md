---
kind: lesson
outline: [2, 2]
time: 40 分钟
uses: [pytest.fixture, yield 前后两段, fixture 作用域, pytest.raises]
record:
  - text: 当时的代码 Day22/
    link: https://github.com/syjlpineapple/ai-learning/tree/main/dailypractice/Day22
---

# Day 22：Fixture 与测试资源

昨天三个测试，每个开头都是 `client = APIClient(...)`，结尾都是 `client.close()`。三个还能忍，几十个就不行了，而且每个测试都得自己记着关，漏一个就漏关一个 `Session`。

pytest 的 fixture 就是把「测试前的准备」和「测试后的清理」提出来，统一管。

## 一、fixture：按参数名自动送上门

```python
@pytest.fixture
def user():
    return {"id": 1, "name": "jack"}

def test_user(user):
    assert user["id"] == 1
```

`test_user(user)` 里的 `user` 你不用传。pytest 看到测试函数有个参数叫 `user`，就去找同名的 fixture，调用它，把结果塞进来。测试函数只说「我要一个 user」，怎么造出来是 fixture 的事。

## 二、`yield`：把 fixture 切成两段

需要清理的资源，用 `yield` 代替 `return`：

```python
@pytest.fixture
def client():
    print("\n准备：创建 client")
    c = {"open": True}
    yield c
    c["open"] = False
    print("清理：关闭 client")

def test_ok(client):
    print("测试中：", client)
    assert client["open"]

def test_fail(client):
    print("测试中：马上断言失败")
    assert client["open"] is False
```

用 `pytest -s` 跑（`-s` 让 `print` 显示出来）：

```text
准备：创建 client
测试中： {'open': True}
.清理：关闭 client
准备：创建 client
测试中：马上断言失败
F清理：关闭 client
（中间是 test_fail 的失败详情，省略）
1 failed, 1 passed in 2.62s
```

`yield` 之前的代码在测试开始前执行，`yield` 出去的东西交给测试，`yield` 之后的代码在测试结束后执行。看第二个测试：**断言失败了，清理照样执行**。这和 `finally` 是同一个保证，所以数据库连接、HTTP Session、临时文件都适合用它管。

对比一下三种「用完就清理」的写法：`with open(...)` 管一个代码块里的资源（Day 11），`try / finally` 手动管（Day 20），fixture 的 `yield` 管跨测试复用的资源。

## 三、作用域

默认每个测试都重新执行一次 fixture，每个测试拿到一个全新的对象，互不干扰，这就是 Day 12 说的测试隔离。可以改：

```python
@pytest.fixture(scope="module")      # 整个测试文件只创建一次
```

| `scope` | 多久创建一次 |
|---|---|
| `function`（默认） | 每个测试一次 |
| `module` | 每个测试文件一次 |
| `session` | 整次 pytest 运行一次 |

默认值通常就是对的。只有创建一次很贵时（比如启动一个服务）才放大，代价是测试之间可能互相影响，得自己隔开。

## 四、`pytest.raises()`

昨天测异常是手写的 `try` 加 `assert False`。换成：

```python
with pytest.raises(requests.exceptions.HTTPError):
    api_client.post("/users", {"name": "jack"})
```

想测什么写在 `with` 上，一眼就看明白。要是代码块里**没有**抛出这个异常，测试直接失败：

```python
def test_raises_catches_nothing():
    with pytest.raises(ValueError):
        int("42")
```

```text
E       Failed: DID NOT RAISE ValueError
```

手写 `try/except` 最容易出的错，就是漏了「没抛异常时让测试失败」那一句，变成永远通过的假测试（Day 11 碰到过）。`pytest.raises()` 把这一句替你写好了。

## 五、今天的作业

在 `Day22/` 下放 `api_client.py`（从 Day 21 复制）和 `test_api_client.py`：

1. 写 `api_client` fixture：创建 `APIClient`，`yield` 出去，测试结束后自动关闭
2. 用它重写「POST 成功」：Mock `session.post()`，检查返回值
3. 用它重写「HTTPError」：`side_effect` 模拟失败，用 `pytest.raises()` 检查
4. 「close 被调用一次」这个测试**自己创建 client**，不用这个 fixture

## 六、小测

**1.** `@pytest.fixture` 的主要作用是？

- A. 自动执行所有测试函数
- B. 给测试函数提供可复用的数据或资源
- C. 自动接住所有异常

**2.** fixture 里 `yield` 前后的代码什么时候执行？

- A. 都在测试前
- B. 都在测试后
- C. 前面的在测试前，后面的在测试结束后

**3.** 测试函数里断言失败了，fixture 里 `yield` 后面的清理代码还会执行吗？

- A. 会
- B. 不会

<details>
<summary>答案</summary>

1. B。
2. C。
3. A。第二节的 `test_fail` 就是实测。

</details>

## 讲评（11-13）

三道理解题你答的是 B、C、B，全对。第一次交的测试有两处需要改。

**一是 `test_success` 断言了 `resp.status_code == 200`。** 实测：

```text
E       AttributeError: 'dict' object has no attribute 'status_code'
```

`api_client.post()` 返回的是 `response.json()` 的结果，一个普通字典，不是响应对象。`status_code` 是你设在 `mock_response` 上的。

这里有个容易有的错觉：用了 Mock 就怎么点都不报错。其实 Mock 的「宽容」只在 Mock 对象身上，`return_value` 设成了真字典，从它身上取属性就按字典的规矩来。

改法是直接断言 `resp == {"id": 1, "email": "abc@gmail.com"}`，再补上 `assert_called_once_with` 检查 URL、`json`、`timeout`。

**二是 `test_call_close` 用了 fixture。** GPT 当时指出这里不对，方向是对的，但说的理由要更正一下。

> 注意：GPT 说这个测试会失败，实测是通过的：断言在测试函数里执行，fixture 的清理在断言**之后**才跑。把调用次数在清理时打出来：

```text
.
teardown 之后，close 一共被调用了 2 次
1 passed in 3.63s
```

真正的问题是：这个测试想验证「`close` 被调用几次」，而 fixture 自己也会调 `close`，测试环境和被测行为搅在了一起。今天通过，是因为断言恰好排在清理前面。规律是：**被测的行为和 fixture 的清理是同一件事时，就别用这个 fixture。** 自己创建一个 client 最干净。

后来 PyCharm 报了几条红线，你把 `api_client.py` 发过去，真正的问题在这一行：

```python
url = self.base_url/path
```

```text
TypeError: unsupported operand type(s) for /: 'str' and 'str'
```

Day 18、19 刚用过 `BASE_DIR / ".env"`，手顺就写上了。`Path` 支持用 `/` 拼路径，字符串不支持。就算把地址转成 `Path` 也不行：

```python
print(repr(Path("https://example.com") / "users"))
```

```text
WindowsPath('https:/example.com/users')
```

`https://` 被压成了 `https:/`。`Path` 是给文件路径用的，会合并连续的斜杠。拼 URL 还是用 Day 20 的 f-string 加两个 strip。

PyCharm 还报了两条提示，性质不同：「未解析的引用 `mock_response`」是真问题，断言缩进跑到了函数外面，你自己发现「把两行代码放到断言之前就可以了」，也就是先准备 Mock、再调用、最后断言的顺序；「找不到引用 `session`」只是编辑器推断不出动态赋值的属性，运行时 `self.session` 是在的。分不清时，跑一遍就知道。

最终版实测三个测试全部通过：

```text
dailypractice/Day22/test_api_client.py::test_success PASSED              [ 33%]
dailypractice/Day22/test_api_client.py::test_post_fail PASSED            [ 66%]
dailypractice/Day22/test_api_client.py::test_call_close PASSED           [100%]
============================== 3 passed in 0.40s ==============================
```

还剩两个小地方：`test_call_close(api_client)` 自己新建了 client，却还留着 `api_client` 参数，fixture 白白创建了一个对象，参数可以删掉；`__init__` 的参数名改成了 `test_key`，它描述的是「谁在用」而不是「它是什么」，和 Day 18 的 `API_KEY_TEST` 是同一个毛病，叫回 `api_key` 就好。

## 加练

- [装饰器](加练/day22_装饰器.md)：`@pytest.fixture` 本身就是装饰器。这一题自己写两个，弄清 `@` 到底做了什么。
- [给测试搭环境](加练/day22_给测试搭环境.md)：用 `yield` fixture、`scope` 和 fixture 依赖 fixture，让整次测试共用一个本机服务，同时保证每个测试拿到干净的状态。
