---
kind: problem
outline: [2, 2]
time: 50 分钟
uses: [MagicMock, side_effect, call_args, 真的 Response, spec 的边界]
record:
  - text: Day21 Mock
    link: https://github.com/syjlpineapple/ai-learning/blob/main/courseware/records/python/Day21.md
  - text: Day22 Fixture
    link: https://github.com/syjlpineapple/ai-learning/blob/main/courseware/records/python/Day22.md
---

# 第 14 题 · 用 Mock 测 APIClient

M5 到 M7 的测试都开着一个本机服务，还要让它「故意出错」。真实项目里，你没法让对方的服务器配合你返回 503、拖 2 秒。这一题不开服务、不联网：把 `APIClient` 用的 Session 换成一个假的，由你决定它每次返回什么，再检查 `APIClient` 是怎么调用它的。

**这一题是你写测试。** 评测不看你的测试长什么样，只看它有没有用：先用正确的 `APIClient` 跑一遍，必须全部通过；再换成 8 个**故意写错的版本**，每一个都必须让你的测试失败。这是第 2.3 章的变异测试。

## 题目

在 [`code/m08_testing/p14_mock_exercise.py`](../../code/m08_testing/p14_mock_exercise.py) 里写 `test_` 开头的函数，测第 12 题的 `APIClient`。要测的行为：

1. 每个请求都带上 `settings.timeout`
2. 状态码 500 时，`get_scores` 抛 `requests.exceptions.HTTPError`
3. 请求的 URL 是 `base_url` + `/` + `endpoint`，没有 `//`（`base_url` 可以带 `/api` 这样的路径）
4. 请求头里有 `Authorization: Bearer <api_key>`
5. `upload` 发的是 JSON（`json=`），不是表单
6. `upload` 第一次超时、第二次成功时，两次请求带的 `Idempotency-Key` 是同一个
7. `retries=2` 时，一直失败的话一共请求 3 次
8. `with` 块里出了异常，异常照样抛出来

**规则**：不能发真实的网络请求（评测会把网络断掉），也不能开本机服务。

**用得上的东西**

```python
from unittest.mock import MagicMock
from m08_testing.p14_target import APIClient, fake_response
from m06_config.p10_settings_solution import Settings

APIClient(settings, session=..., sleep=...)    # 第 12 题留的两个口子
fake_response(500, {"error": "x"})             # 造一个真的 requests.Response
```

`APIClient` 所有的请求都走 `session.request(method, url, **kwargs)` 这一个方法。

**验证**（在 `code/` 目录下）

```powershell
pytest tests/test_m08.py -k p14 -v
```

现在是 `18 passed, 9 skipped`，全部做完是 `27 passed`。哪个写错的版本没抓住，报错里会告诉你它错在哪。

::: details 提示：从哪下手
`session = requests.Session()`，然后 `session.request = MagicMock(...)`。这样 `headers` 这些属性都是真的，只有发请求那一步是假的。`MagicMock(side_effect=[...])` 让它每次调用返回列表里的下一个，列表里是异常就抛出来。
:::

::: details 提示：怎么检查它被调用时传了什么
`mock.call_args.args` 是位置参数，`mock.call_args.kwargs` 是关键字参数；`mock.call_args_list` 是每一次调用的记录。`mock.call_count` 是调用次数。
:::

::: details 提示：sleep 传什么
一个只记录、不等待的函数。`delays = []`，然后传 `sleep=delays.append`。
:::

<Reveal>

## 讲评

### 参考答案

```python
def make_client(*responses, retries=2, base_url="http://h/api", timeout=4.0):
    session = requests.Session()
    session.request = MagicMock(side_effect=list(responses))
    delays = []
    settings = Settings(api_key="sk-test", base_url=base_url, timeout=timeout,
                        retries=retries, debug=False)
    return APIClient(settings, session=session, sleep=delays.append), session.request, delays


def test_get_scores_sends_timeout_and_url():
    client, request, _ = make_client(fake_response(200, SCORES))

    result = client.get_scores(limit=5)

    assert result == SCORES
    request.assert_called_once()
    method, url = request.call_args.args
    assert (method, url) == ("GET", "http://h/api/scores")          # 行为 3
    assert request.call_args.kwargs["timeout"] == 4.0                # 行为 1


def test_server_error_raises():
    client, request, _ = make_client(*[fake_response(500, {"error": "x"})] * 3)
    with pytest.raises(E.HTTPError):                                 # 行为 2
        client.get_scores()
    assert request.call_count == 3                                   # 行为 7


def test_upload_sends_json_and_same_key():
    client, request, delays = make_client(E.ReadTimeout("回答太慢"),
                                          fake_response(201, {"id": 8}))

    assert client.upload("张三", 3) == {"id": 8}

    first, second = request.call_args_list
    assert first.kwargs["json"] == {"player": "张三", "attempts": 3}   # 行为 5
    keys = [c.kwargs["headers"]["Idempotency-Key"] for c in (first, second)]
    assert keys[0] == keys[1]                                        # 行为 6
```

完整的 5 个测试见 [`p14_mock_solution.py`](../../code/m08_testing/p14_mock_solution.py)。每个测试都是 Day22 讲的三段：准备（造假 Session 和回答）、执行（调一次）、验证（看结果和调用记录）。

**为什么这一题根本不需要 `patch`**：第 12 题的 `APIClient` 允许从外面传 `session` 和 `sleep` 进来，测试直接把假的交给它就行。这就是第 1.6 章依赖注入的回报。代码里如果写死了 `requests.get(...)`，就只能用 `unittest.mock.patch` 去替换，还得注意替换的是「使用它的那个模块里的名字」：被测模块写的是 `from requests import get` 时，`patch("requests.get")` 替换不到它。

### 坑 1：MagicMock 当 Response，503 也不会报错

```python
fake = MagicMock()
fake.status_code = 503
fake.raise_for_status()     # 返回一个 MagicMock，不抛异常
fake.json()                 # 也是一个 MagicMock，不是列表
```

MagicMock 的每一个方法都「什么都不做，返回另一个 MagicMock」。`status_code` 设成 503 只是在它身上贴了个数字，`raise_for_status()` 根本不看。想测「500 时抛 `HTTPError`」，就得自己写 `fake.raise_for_status.side_effect = HTTPError(...)`，而这等于你替被测代码决定了它该怎么反应。

参考答案用的 `fake_response` 是一个**真的** `requests.Response`，只是没有真的发请求：

```text
真 Response 503 raise_for_status()    →  HTTPError: 503 Server Error: None for url: None
真 Response 200 正文是 HTML 的 json()   →  JSONDecodeError: Expecting value: line 1 column 1 (char 0)
```

它的行为和真实的回应完全一样。**只把「发请求」那一步换成假的，其他的能用真的就用真的。**

### 坑 2：只断言返回值，等于什么都没测

评测里有一个对照用的「弱测试」，它把整个 Session 换成 MagicMock，只检查 `get_scores()` 的返回值：

```python
session = MagicMock()
session.request.return_value.json.return_value = [{"player": "x", "attempts": 1}]
assert APIClient(s, session=session).get_scores() == [{"player": "x", "attempts": 1}]
```

8 个写错的版本，**它一个都没抓住**，全部通过。没带 timeout、URL 有 `//`、没有认证头、发的是表单，返回值都一样。要发现这些，必须检查 Session **被怎么调用了**：`call_args`、`call_args_list`、`call_count`。Day21 说过「`assert_called_once_with` 比只检查返回值强得多」，这一题用变异测试把它量化了。

### 坑 3：MagicMock 对拼错的名字很宽容

```text
assert m.caled                       通过（called 拼错了，m.caled 是一个 MagicMock，真值为 True）
m.asssert_called_once()              通过（三个 s，什么都没检查）
m.assert_called_onse()               AttributeError: 'assert_called_onse' is not a valid assertion.
                                     Use a spec for the mock if 'assert_called_onse' is meant to be an attribute.
```

Python 对 `assert`、`assret`、`asert`、`aseert`、`assrt` 这几个开头的拼写错误有保护，会直接报错。但保护只覆盖这几种开头，三个 `s` 的 `asssert_` 就漏过去了。用 `.called` 这样的属性时更没有保护。所以检查次数时，参考答案用的是 `assert request.call_count == 3`：写错了属性名会得到一个 MagicMock，`MagicMock == 3` 是 `False`，测试会失败而不是悄悄通过。

> Day21 讲义说报错里会有 `Did you mean: 'assert_called_once'?`。这一句不是 mock 生成的，是 Python 打印未捕获异常时追加的提示，`str(e)` 里没有它。

### 坑 4：`spec` 的几个边界

`spec` 让 Mock 只接受真实对象有的属性，Day21 讲过。实测它有几个不那么直观的地方：

```text
MagicMock(spec=requests.Session).headers       AttributeError   headers 是 __init__ 里才创建的
MagicMock(spec=requests.Session()).headers     可以              传的是实例，看得到实例属性
MagicMock(spec=requests.Session).pots = 1      可以              spec 只拦读，不拦写
MagicMock(spec_set=requests.Session).pots = 1  AttributeError   spec_set 读写都拦
MagicMock(spec=requests.Session).request()     可以              不检查参数
create_autospec(requests.Session, instance=True).request()
                                               TypeError: missing a required argument: 'method'
```

第一条直接影响这一题：用 `MagicMock(spec=requests.Session)` 当 session 传给 `APIClient`，构造函数里的 `session.headers.update(...)` 就报 `AttributeError`。参考答案的做法是用真的 Session、只换 `request` 方法，`headers` 是真的字典，测试里可以直接检查它。

### 坑 5：`side_effect` 列表用完了

```text
MagicMock(side_effect=[1, ReadTimeout("慢"), 3]) 连续调用 4 次
  →  1、抛 ReadTimeout、3、抛 StopIteration
```

列表里的异常会被抛出，列表用完以后再调用，抛的是 `StopIteration`。如果被测代码多请求了一次（比如重试次数多了一），你看到的是一个莫名其妙的 `StopIteration`，而不是「请求次数不对」。参考答案在列表里放的回答数量正好等于预期的请求次数，再用 `call_count` 明确断言次数。

`assert_called_with` 只看**最后一次**调用，前面的调用参数对不对它不管：

```text
m("a", x=1); m("b", x=2)
m.assert_called_with("a", x=1)    →  AssertionError: expected call not found.
m.call_args_list                  →  [call('a', x=1), call('b', x=2)]
```

要检查每一次，用 `call_args_list`。

## 复盘

::: tip 这题用到的
- **只把边界换成假的**：Session 是真的，只有 `request` 是 MagicMock；回应用真的 `requests.Response`，`raise_for_status()`、`json()` 都按真实规则工作
- **`side_effect`**：传列表就是按顺序返回；列表里的异常会被抛出；用完了抛 `StopIteration`
- **检查调用，不只是检查结果**：`call_args.args`、`call_args.kwargs`、`call_args_list`、`call_count`
- **`assert_called_with` 只看最后一次**；数次数用 `call_count == n`，比 `assert_called_*` 系列更不怕拼错
- **`spec` 传类看不到实例属性**；`spec` 拦读不拦写，`spec_set` 都拦；检查参数签名要 `create_autospec`
- **依赖注入让测试不需要 `patch`**；需要 `patch` 时，替换「使用它的那个模块里的名字」
- **测试有没有用，拿写错的版本试一试**：只断言返回值的测试，8 个错误一个都抓不住
:::

## 自测

1. `fake = MagicMock(); fake.status_code = 500`，被测代码调用 `fake.raise_for_status()` 会怎样？为什么参考答案用真的 `Response`？
2. 只断言 `client.get_scores()` 的返回值，为什么抓不住「没带 timeout」这种错误？要怎么检查？
3. `MagicMock(spec=requests.Session)` 传给 `APIClient` 为什么会在构造时就报错？

<details>
<summary>参考答案</summary>

1. 什么都不会发生，它返回一个 MagicMock，不抛异常。MagicMock 不会根据 `status_code` 做任何判断。真的 `Response` 的 `raise_for_status()` 会按状态码真的抛出 `HTTPError`，不需要测试替被测代码决定行为。
2. 返回值只取决于假回应里放了什么，和请求怎么发出去无关。要检查假 Session 被调用时收到的参数：`request.call_args.kwargs["timeout"]`。
3. `spec` 传的是类，只看得到类上定义的属性；`headers` 是 `requests.Session.__init__` 里才创建的实例属性，所以 `session.headers` 报 `AttributeError`，而 `APIClient` 的构造函数要更新它。改成传实例（`spec=requests.Session()`），或者用真的 Session、只替换 `request` 方法。

</details>

</Reveal>
