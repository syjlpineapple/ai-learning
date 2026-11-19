---
kind: lesson
outline: [2, 2]
time: 45 分钟
uses: [单元测试, MagicMock, return_value 与 side_effect, assert_called_once_with, conftest.py]
record:
  - text: 当时的代码 Day21/
    link: https://github.com/syjlpineapple/ai-learning/tree/main/dailypractice/Day21
---

# Day 21：单元测试与 Mock

昨天的 `APIClient` 能用了。今天给它写测试，但有个麻烦：`post()` 里那行 `self.session.post(...)` 一执行，就真的发出去了。

真发请求的测试，网断了会挂，服务器维护会挂，密钥过期也会挂，这些都和你的代码对不对没关系，而且每次都要等网络。可你真正想验证的是：URL 拼对没有、数据是不是用 `json=` 传的、`timeout` 带了没有、500 时会不会抛异常。**这些都不需要联网。**

办法是用一个假对象顶替 `session.post`，它返回什么、抛什么，由你说了算。这个假对象叫 Mock。

## 一、`MagicMock`：一个听话的假对象

`unittest.mock` 是标准库，不用装。`MagicMock` 比 `Mock` 多支持一些特殊方法，平时直接用它就行。

```python
user = Mock()
user.id = 1
user.get_email.return_value = "aaa@gmail.com"
print(user.id)
print(user.get_email())
print(user.get_email.call_count)
```

```text
1
aaa@gmail.com
1
```

`get_email()` 没有执行任何真实逻辑，直接返回你指定的值，而且它记得自己被调用了几次。

两个最常用的设置：

| 设置 | 意思 |
|---|---|
| `return_value` | 被调用时**返回**什么 |
| `side_effect` | 被调用时**做**什么，最常用的是抛异常 |

```python
resp = MagicMock()
resp.raise_for_status.side_effect = requests.exceptions.HTTPError("500 Server Error")
try:
    resp.raise_for_status()
except requests.exceptions.HTTPError as e:
    print("HTTPError:", e)
```

```text
HTTPError: 500 Server Error
```

「让服务器返回 500」你控制不了，「让假响应在检查状态码时抛 500」一行就够。测异常路径全靠 `side_effect`。

## 二、换掉 `session.post`，再检查它是怎么被调用的

```python
client = APIClient("https://example.com", "test_key")

mock_response = MagicMock()
mock_response.json.return_value = {"id": 1, "email": "abc@gmail.com"}
client.session.post = MagicMock(return_value=mock_response)

resp = client.post("/user_info", {"name": "jack"})
```

第三行是关键：把真的 `session.post` 整个换成假的。之后 `client.post()` 里调用的 `self.session.post(...)` 其实是这个 Mock，不会碰网络。

能这么换，是因为 Day 20 把 `Session` 存成了 `self.session`。依赖放在一个能访问到的属性上，测试时才好替换。这是昨天那个设计的另一个好处。

为什么换 `session.post` 而不是 `client.post`？你当天问过这个。因为要测的就是 `client.post` 里的逻辑，把它换掉就什么都没测了。**只换它依赖的外部部分，被测的代码照常运行。**

光检查返回值还不够，还要检查它**是怎么调用依赖的**：

```python
client.session.post.assert_called_once_with(
    "https://example.com/user_info",
    json={"name": "jack"},
    timeout=10,
)
mock_response.raise_for_status.assert_called_once()
```

第一句同时检查了：调用过、只调用了一次、URL 对、用的是 `json=`、带了 `timeout=10`。假如有人把 `timeout` 删了，它会这样报错：

```text
AssertionError: expected call not found.
Expected: mock('https://example.com/user_info', json={'name': 'jack'}, timeout=10)
  Actual: mock('https://example.com/user_info', json={'name': 'jack'})
```

第二句检查「状态码检查做了没有」。只看返回值，这两类错误都发现不了。

MagicMock 有一点要当心：你没设置过的属性，它也照样给你造一个，不报错：

```python
m = MagicMock()
print(type(m.totally_made_up_method()).__name__)
```

```text
MagicMock
```

方法名拼错了，测试可能照样「通过」。好在断言方法拼错它会拦住：`m.assret_called_once` 直接报 `AttributeError: 'assret_called_once' is not a valid assertion.`

## 三、pytest 怎么找测试

`pip install pytest` 之后，在目录里敲 `pytest`。它按名字找：文件叫 `test_*.py`，函数以 `test_` 开头，就会被当成测试执行，断言直接用 `assert`。

你当天碰到一个现象：文件里有 `print(user.id)`，在 PyCharm 里右键运行，却只看到 `collected 1 item ... test_add PASSED`，没有打印。因为文件名是 `test_` 开头，PyCharm 用 pytest 跑的它，而 pytest 默认会把测试里的输出收起来，只在测试失败时才显示。想看就加 `-s`。**没看到 `print` 的输出，不等于代码没执行。**

## 四、今天的作业

用 Day 20 的 `APIClient` 写三个测试：

1. **POST 成功**：Mock `session.post()`，模拟返回 JSON；检查返回值，再检查 URL、`json`、`timeout` 都对
2. **HTTP 失败**：让 `raise_for_status()` 抛 `HTTPError`，检查 `client.post()` 会把它抛出来
3. **关闭**：调用 `close()`，检查 `session.close()` 被调用了一次

## 五、小测

**1.** `mock.post.return_value = response` 是什么意思？

- A. 调用 `mock.post()` 时返回 `response`
- B. 调用 `mock.post()` 时抛出 `response`
- C. 禁止调用 `mock.post()`

**2.** 想让模拟方法被调用时抛出 `HTTPError`，用哪个？

- A. `return_value`
- B. `side_effect`
- C. `assert_called_once`

**3.** `assert_called_once_with(...)` 检查的是什么？

- A. 函数的返回值
- B. 只调用了一次，并且参数和预期一样
- C. 函数执行了多久

<details>
<summary>答案</summary>

1. A。
2. B。
3. B。

</details>

## 讲评（11-09）

这一天代码只有几十行，却花了将近一小时在一个和代码无关的问题上。在 Day21 目录下一跑 `pytest`，报的是：

```text
ImportError while loading conftest 'D:\Lee\AICODE\sell-gen\backend\tests\conftest.py'.
..\..\conftest.py:4: in <module>
    from fastapi.testclient import TestClient
E   ModuleNotFoundError: No module named 'fastapi'
```

你问「pytest 依赖 fastapi 吗」，问得对。不依赖。

pytest 启动时会从测试文件所在目录一层层往上，把每一层的 `conftest.py` 都加载进来。上面某一层的 `conftest.py` 第一行就 `import fastapi`，环境里没装，于是整个收集失败。**报错里出现的库，不一定是你的代码在用**，要顺着「是谁加载了它」往上找。

后来练习代码从那个项目里搬了出来，单独建了现在这个仓库，仓库 README 写的理由正是：练习代码和产品代码共用一套工程配置，会互相干扰。

三个测试写得很完整，成功那个三层都查到了：返回值、调用参数、`raise_for_status` 被调用。URL 那条断言顺便证明了 Day 20 的两个 strip 拼出来没有双斜杠。

问题出在第三个测试，前后两次。第一次交的是：

```python
client = APIClient("https://example.com", "test_key")
client.close()
client.session.close().assert_called_once()
```

`session.close` 没换成 Mock，最后一行调用的是真的 `close()`，它返回 `None`：

```text
AttributeError: 'NoneType' object has no attribute 'assert_called_once'
```

第二次加上了 `client.session.close = MagicMock()`，但最后一行还是 `close()` 多了一对括号，测试失败：

```text
AssertionError: Expected 'mock' to have been called once. Called 0 times.
```

区别就在括号：`close` 是那个 Mock 本身，在它身上问「你被调用过一次吗」才对；`close()` 是**调用**它，拿到的是它的返回值。

> 注意：GPT 说调用 Mock 默认返回 `None`，不对。实测 `client.session.close()` 返回的是一个新的 `MagicMock`，你的断言打在了这个新对象上，它当然一次都没被调用过。
<details>
<summary>怎么看出来的</summary>

报错里的名字是 `'mock'` 而不是 `'close'`，这就是线索：**断言失败时，Mock 的名字和你想的对象对不上，说明断言打在了别的对象上。** 也正因为返回的是 MagicMock，才没有报 `AttributeError`。

</details>

去掉括号以后，三个测试实测全部通过：

```text
dailypractice/Day21/test_api_client.py::test_post_success PASSED         [ 33%]
dailypractice/Day21/test_api_client.py::test_post_fail PASSED            [ 66%]
dailypractice/Day21/test_api_client.py::test_call_close PASSED           [100%]
============================== 3 passed in 0.26s ==============================
```

失败那个测试你用的是 `try` 里 `assert False, "应该抛出 HTTPError"`，能用，你自己也在注释里写了更好的 `pytest.raises()`，明天就用它。

## 加练

[用 Mock 测 APIClient](加练/day21_用Mock测APIClient.md)：给加练里的 `APIClient` 写测试，不开服务、不联网。评测会拿几个故意写错的版本来跑你的测试，每个都必须被你抓住，练的是「测试到底有没有检查到东西」。
