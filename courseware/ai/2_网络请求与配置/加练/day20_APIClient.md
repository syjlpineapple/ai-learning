---
kind: problem
outline: [2, 2]
time: 45 分钟
uses: [requests.Session, 认证头, URL 拼接, __enter__ 和 __exit__]
record:
  - text: Day20 APIClient
    link: https://github.com/syjlpineapple/ai-learning/blob/main/courseware/records/python/Day20.md
---

# 第 12 题 · APIClient

M5 的 `fetch_scores`、`upload_score` 每次调用都要传地址，每次都是一个独立的请求。这一题把它们收进一个类：地址、密钥、超时、重试次数在创建时交给它一次（就是第 10 题的 `Settings`），之后只管调用 `client.get_scores()`、`client.upload(...)`。

这一回本机服务开始检查身份：`/scores` 要求请求头 `Authorization: Bearer <密钥>`，不对就返回 401。

## 题目

打开 [`code/m07_client/p12_client_exercise.py`](../../code/m07_client/p12_client_exercise.py)，实现 `APIClient`：

```python
client = APIClient(settings)                 # settings 是第 10 题的 Settings
client.get_scores(player="张三", limit=5)
client.upload("张三", 3)
client.close()

with APIClient(settings) as client:          # 也可以这样用，结束时自动 close
    ...
```

`with_retry`（第 8 题）已经导入好了。

**要求**

1. 一个客户端只用**一个** `requests.Session`，在 `__init__` 里建好（调用方传了 `session` 就用传进来的）。`Authorization: Bearer <api_key>` 在 Session 上设一次，之后每个请求自动带上
2. `url_for(endpoint)`：`base_url` 和 `endpoint` 之间正好一个 `/`。`base_url` 可能带路径，比如 `http://h/api/v1`，这一段不能丢
3. 每个请求都用 `settings.timeout`
4. 失败了用 `with_retry` 重试。`settings.retries=2` 表示失败后最多再试 2 次，一共 3 次。`upload` 重试时同一条成绩不能存两次（第 9 题）
5. 支持 `with`：结束时关掉 Session；`with` 块里出了异常，Session 照样关掉，**异常照样抛出去**
6. 写 `__repr__`：看得到 `base_url`，看不到密钥

**验证**（在 `code/` 目录下）

```powershell
pytest tests/test_m07.py -k p12 -v
```

现在是 `19 passed, 13 skipped`，全部做完是 `32 passed`。

::: details 提示：要求 1，测试说 3 个请求用了 3 条连接
测试数的是服务端看到的客户端端口：同一条 TCP 连接，端口不变。`requests.Session()` 写在哪里会让每个请求都新建一个？
:::

::: details 提示：要求 2，http://h/api/v1 变成了 http://h/api/scores
你是不是用了 `urllib.parse.urljoin`？它按「浏览器里点相对链接」的规则拼，`v1` 后面没有 `/` 时，它会被当成文件名换掉。Day20 用的两个 `strip` 更可靠。
:::

::: details 提示：要求 3，我设了 session.timeout 也没用
`requests.Session` 没有「默认超时」这个设置。`session.timeout = 5` 只是在对象上加了一个属性，requests 根本不读它。
:::

::: details 提示：要求 5，with 块里的异常不见了
`__exit__` 的返回值有特别的含义。返回 `True` 会怎样？
:::

<Reveal>

## 讲评

### 参考答案

```python
class APIClient:
    def __init__(self, settings, session=None, sleep=time.sleep):
        self.settings = settings
        self._sleep = sleep
        self._session = session if session is not None else requests.Session()
        self._session.headers.update({
            "Authorization": f"Bearer {settings.api_key}",
            "Accept": "application/json",
        })

    def url_for(self, endpoint):
        return f"{self.settings.base_url.rstrip('/')}/{endpoint.lstrip('/')}"

    def _request(self, method, endpoint, **kwargs):
        response = self._session.request(method, self.url_for(endpoint),
                                         timeout=self.settings.timeout, **kwargs)
        response.raise_for_status()
        return response.json()

    def _with_retry(self, call):
        return with_retry(call, attempts=self.settings.retries + 1, sleep=self._sleep)

    def get_scores(self, player=None, limit=10):
        params = {"player": player, "limit": limit}
        data = self._with_retry(lambda: self._request("GET", "/scores", params=params))
        ...                                  # 检查是不是列表（第 6 题）

    def upload(self, player, attempts):
        key = uuid.uuid4().hex               # 重试之前生成一次（第 9 题）
        data = self._with_retry(lambda: self._request(
            "POST", "/scores", json={"player": player, "attempts": attempts},
            headers={"Idempotency-Key": key}))
        ...

    def close(self):
        self._session.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()                         # 返回 None：异常照常抛出

    def __repr__(self):
        return f"APIClient(base_url={self.settings.base_url!r}, timeout={self.settings.timeout})"
```

完整代码见 [`p12_client_solution.py`](../../code/m07_client/p12_client_solution.py)。`headers={"Idempotency-Key": key}` 会和 Session 上的请求头合并，两个都会发出去。

### 坑 1：Session 每次都新建，连接没有复用

典型初稿把 Session 写在了 `_request` 里：

```python
def _request(self, method, endpoint, **kwargs):
    with requests.Session() as s:
        s.headers["Authorization"] = ...
        ...
```

服务端记下了每个请求来自哪个客户端端口：

```text
requests.get × 3      →  端口 [59009, 59010, 59011]     三条连接
同一个 Session × 3     →  端口 [59016, 59016, 59016]     一条连接
```

每条新连接都要先握手（HTTPS 还要再加一轮加密握手），连续调用很多次时这笔开销很明显。Day20 讲过「Session 要在 `__init__` 里建一次」，这里是实测的效果。注意本机服务为了支持连接复用，要用 HTTP/1.1 回答（`server.py` 里的 `protocol_version`），默认的 HTTP/1.0 每回答一次就断开。

### 坑 2：`urljoin` 会丢掉最后一段

```text
urljoin("https://x.com/api",  "scores")    →  'https://x.com/scores'       api 没了
urljoin("https://x.com/api/", "/scores")   →  'https://x.com/scores'       api 没了
urljoin("https://x.com/api/", "scores")    →  'https://x.com/api/scores'   只有这种对
```

`urljoin` 是按浏览器里「点一个相对链接」的规则拼的：`/scores` 表示从网站根目录开始，`api` 后面没有 `/` 时被当成一个文件名换掉。拼 API 地址时这两种行为都不是你想要的。Day20 的写法是两边各 `strip` 一次、中间补一个 `/`，不管两边有没有斜杠，结果都一样。

`strip` 还有一个小坑，Day20 讲义提到过：参数是**字符集合**，不是字符串。

```text
"https://x.com/v1".rstrip("/v1")         →  'https://x.com'         去掉的是 /、v、1 这几个字符
"https://x.com/v1".removesuffix("/v1")   →  'https://x.com'
```

两个结果碰巧一样，但 `rstrip("/v1")` 遇到 `https://x.com/api1` 会变成 `https://x.com/api`。想去掉一个固定的后缀，用 `removesuffix`（Python 3.9+）。

### 坑 3：`session.timeout = 5` 不起作用

```python
session = requests.Session()
session.timeout = 0.5
session.get(".../slow?seconds=2")      # 等了整整 2 秒，返回 200
```

不报错，也不生效。`requests.Session` 没有默认超时的设置，requests 不会去读这个属性。初稿就是这样写的，测试里服务端拖 2 秒、`timeout=0.5`，结果照样成功了。每个请求都要自己传 `timeout=`，参考答案把它集中写在 `_request` 里，就不会漏。

### 坑 4：重试次数差一

`settings.retries` 的意思是「失败后再试几次」，`with_retry` 的 `attempts` 是「一共调用几次」。初稿直接传了 `attempts=settings.retries`：

```text
retries=2 时：一共只请求了 2 次（应该是 3 次）
retries=0 时：ValueError: attempts 至少是 1，传进来的是 0
```

第二种情况是第 8 题参考答案专门留的检查：`attempts=0` 时一次都不会调用，与其悄悄返回什么，不如直接报错。

### 坑 5：`__exit__` 返回 `True` 会吞掉异常

```python
def __exit__(self, *exc):
    self.close()
    return True
```

```text
with Swallow():
    raise ValueError("请求失败")
return "with 后面的代码照常执行"      ← 真的执行到了这里
```

`__exit__` 的返回值为真时，Python 认为「异常已经处理好了」，`with` 块里的异常就消失了。测试 `test_p12_with_does_not_swallow` 在 `with` 块里抛了一个 `KeyError`，初稿把它吞了。`__exit__` 默认什么都不返回（`None`，也就是假），异常照常往外抛。只有在你明确想吞掉某种异常时才返回 `True`，比如标准库的 `contextlib.suppress`。

### 坑 6：打印客户端，带出密钥

```text
str(session.headers)  →  "{..., 'Authorization': 'Bearer sk-test-0123...'}"
```

默认的 `repr` 是 `<APIClient object at 0x...>`，看不出连的是哪个服务。自己写 `__repr__` 时，不要图省事把 `session.headers` 或者 `vars(self)` 放进去，Authorization 头里就是完整的密钥。`settings` 的 `repr` 是安全的，第 10 题已经用 `field(repr=False)` 处理过了。

### 典型初稿会被哪些测试抓住

初稿：每个请求新建 Session、`session.timeout = ...`、`urljoin`、`attempts=settings.retries`、`__exit__` 返回 `True`、没写 `__repr__`。

```text
FAILED test_p12_reuses_connection          3 个请求用了 3 条连接（客户端端口 [60411, 60412, 60413]）
FAILED test_p12_url_for                    （3 条）'http://h/api/scores'、'http://h/scores'、'http://scores'
FAILED test_p12_uses_timeout               ValueError: attempts 至少是 1，传进来的是 0
FAILED test_p12_retries                    一共请求了 2 次，应该是 3 次
FAILED test_p12_with_does_not_swallow      DID NOT RAISE KeyError
FAILED test_p12_repr_has_no_secret         '<...APIClient object at 0x000001F2FAC4ACF0>'
8 failed, 5 passed
```

`test_p12_upload_no_duplicates` 这条初稿反而过了，可它的 key 明明写在 lambda 里（第 9 题坑 3）。原因是坑 3 和第 9 题的坑**互相掩盖**：初稿根本没传 `timeout`，上传请求一直等到服务端 2 秒后回答，拿到 201，从来没有触发重试，自然不会重复。实测把初稿的 `timeout` 补上、别的都不改，这条测试立刻失败，服务端存了两条。**一个 bug 让另一个 bug 暂时看不出来**，修好其中一个，另一个才露出来。

## 复盘

::: tip 这题用到的
- **一个客户端一个 Session**，在 `__init__` 里建好：复用连接，请求头设一次
- **Session 没有默认超时**，每个请求自己传 `timeout=`
- **拼 URL 用两个 `strip`**，不用 `urljoin`；去后缀用 `removesuffix`，不用 `rstrip`
- **「重试几次」和「一共几次」差一**，写清楚是哪一个
- **`__enter__` 返回自己，`__exit__` 里 `close()`**，不要返回 `True`
- **`__repr__` 放排查用得上的信息**，不放密钥和请求头
:::

客户端写好了，但谁来创建它、读配置、处理它抛出的各种异常、决定程序最后返回什么？这是程序入口的事，下一题来写。

## 自测

1. 把 `requests.Session()` 写在每个请求的方法里，和写在 `__init__` 里，服务端看到的有什么不同？
2. `urljoin("https://x.com/api", "scores")` 的结果是什么？为什么？
3. `__exit__` 返回 `True` 会怎样？什么时候才应该这样做？

<details>
<summary>参考答案</summary>

1. 写在方法里，每个请求都是一条新的 TCP 连接，服务端看到的客户端端口每次都不一样；写在 `__init__` 里，连续的请求走同一条连接，端口不变，省掉了每次重新握手的开销。
2. `https://x.com/scores`，`api` 被丢掉了。`urljoin` 按相对链接的规则拼：`api` 后面没有 `/`，它被当成一个文件名，换成了 `scores`。
3. `with` 块里的异常会被吞掉，后面的代码照常执行，调用方根本不知道出过错。只有明确想忽略某种异常时才返回 `True`，比如 `contextlib.suppress`；一般的资源清理不该返回任何值。

</details>

</Reveal>
