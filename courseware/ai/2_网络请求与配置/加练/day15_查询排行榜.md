---
kind: problem
outline: [2, 2]
time: 35 分钟
uses: [requests.get, params, timeout, raise_for_status, response.json]
record:
  - text: Day15 第一次调 API
    link: https://github.com/syjlpineapple/ai-learning/blob/main/courseware/records/python/Day15.md
  - text: Day16 请求参数
    link: https://github.com/syjlpineapple/ai-learning/blob/main/courseware/records/python/Day16.md
---

# 第 6 题 · 查询排行榜

M4 把成绩存在本机。这个模块把排行榜放到服务器上，先从查询开始。

当时学习用的是 httpbin.org。这一题换成代码仓里自带的一个小服务 [`m05_http/server.py`](../../code/m05_http/server.py)，它只在你自己的电脑上运行，不需要联网，还能按测试的需要故意变慢、出错、返回奇怪的东西。

```powershell
python -m m05_http.server        # 开着这个终端，然后在浏览器里打开下面的地址
```

```text
http://127.0.0.1:8765/scores?limit=3
[{"player": "100%", "attempts": 1}, {"player": "张三", "attempts": 2}, {"player": "李四", "attempts": 3}]
```

## 题目

打开 [`code/m05_http/p06_fetch_exercise.py`](../../code/m05_http/p06_fetch_exercise.py)，实现：

```python
def fetch_scores(base_url: str, player: str | None = None, limit: int = 10,
                 timeout: float = 5) -> list[dict[str, Any]]:
```

请求 `GET {base_url}/scores`，返回成绩列表。`player` 为 `None` 时不传这个参数。

**要求**

1. 名字里有 `&`、`#`、`%`、中文都要能查到（服务里有 `A&B`、`C#`、`100%` 这几个玩家）
2. `timeout` 参数要真的传给 `requests`
3. 状态码不是 2xx 时抛 `requests.exceptions.HTTPError`。注意 `base_url` 写错时，服务器返回的是 404 和一段 HTML
4. 状态码是 200、正文也是合法 JSON，但不是数组时，抛 `requests.exceptions.InvalidJSONError`

**验证**（在 `code/` 目录下，测试会自己开一个服务，不用先手动启动）

```powershell
pytest tests/test_m05.py -k p06 -v
```

现在是 `15 passed, 11 skipped`，全部做完是 `26 passed`。

::: details 提示：要求 1，查 A&B 什么都没查到
你是不是把参数拼进了 URL 字符串？`requests.get` 有一个参数专门放查询参数，它会帮你编码。
:::

::: details 提示：要求 3，抛的是 JSONDecodeError 不是 HTTPError
`raise_for_status()` 和 `json()` 的顺序。404 页面的正文是 HTML，先解析它会报什么错？
:::

::: details 提示：要求 4，怎么抛 InvalidJSONError
它和别的异常一样，`raise requests.exceptions.InvalidJSONError("说明")` 就行。还可以传 `response=response`，让调用方拿得到这次响应。
:::

<Reveal>

## 讲评

### 参考答案

```python
def fetch_scores(base_url: str, player: str | None = None, limit: int = 10,
                 timeout: float = 5) -> list[dict[str, Any]]:
    params = {"player": player, "limit": limit}       # 值为 None 的参数，requests 会直接丢掉
    response = requests.get(f"{base_url}/scores", params=params, timeout=timeout)
    response.raise_for_status()
    data = response.json()
    if not isinstance(data, list):
        raise requests.exceptions.InvalidJSONError(
            f"期望 JSON 数组，实际是 {type(data).__name__}", response=response)
    return data
```

`player` 不用单独判断：`params` 里值为 `None` 的键不会被发出去。实测 `params={"n": None}` 时，服务端收到的查询参数是 `{}`。

### 坑 1：自己拼 URL

典型初稿是这样拼的：

```python
url = f"{base_url}/scores?limit={limit}"
if player:
    url += f"&player={player}"
```

用 `/echo` 接口看服务端到底收到了什么：

```text
手拼 ?player=A&B     →  {'player': ['A'], 'B': ['']}        & 把它切成了两个参数
手拼 ?player=C#      →  {'player': ['C']}                    # 后面的根本没发出去
params={"player": "A&B", "x": ["1", "2"]}
                     →  URL 是 ...?player=A%26B&x=1&x=2
```

`#` 在 URL 里表示「页面内的位置」，它后面的部分浏览器和 requests 都不会发给服务器，实测发出去的 URL 是 `...?player=C`。`params` 会把 `&` 编码成 `%26`，传列表会生成重复的键。`100%` 和中文在这个服务上手拼也碰巧没出错，但 `%` 本来是编码用的字符，不能指望每个服务器都这么宽容。

### 坑 2：先 `json()` 再看状态码

`base_url` 少写了一段（比如服务其实在 `/api` 下面），服务器返回 404 和一个 HTML 页面：

```text
response.json()              →  JSONDecodeError: Expecting value: line 1 column 1 (char 0)
response.raise_for_status()  →  HTTPError: 404 Client Error: Not Found for url: http://127.0.0.1:.../api/scores
```

先 `json()` 的话，你看到的是「JSON 格式不对」，会去查服务端返回的数据，而真正的问题是地址写错了。`raise_for_status()` 的报错信息里直接带着状态码和 URL。Day15 说过「顺序不能换」，这是它的实际后果。

### 坑 3：`timeout` 不是整个请求的时间上限

服务端的 `/trickle` 每 0.5 秒发一个字节，一共发 3 秒：

```text
requests.get(".../trickle?seconds=3", timeout=1)   →  200，整个请求花了约 2.5 秒
```

`timeout=1` 从来没有触发过。它限制的是「连接要多久建好」和「两次收到数据之间最多等多久」，每次都只等了 0.5 秒。想限制整个请求的总时长，requests 本身做不到。

不写 `timeout` 时，默认是一直等下去。初稿把 `timeout=10` 写死在 `requests.get` 里，函数的 `timeout` 参数成了摆设：测试里服务端拖了 2 秒，`fetch_scores(..., timeout=0.5)` 照样成功返回。

### 坑 4：`raise_for_status()` 只管 400 到 599

```text
/status/304  →  不抛
/status/429  →  HTTPError: 429 Client Error: Too Many Requests
```

429 表示「请求太频繁」。它是 4xx，但通常应该等一会儿再重试，调大模型 API 时很常见。学习记录 Day15 说「4xx 是客户端问题，重试没用」，429 是个例外，第 7 题会用到。

### 典型初稿会被哪些测试抓住

```text
FAILED test_p06_special_characters[A&B]      查 'A&B' 什么都没查到
FAILED test_p06_special_characters[C#]
FAILED test_p06_uses_timeout                 服务端拖了 2 秒，timeout=0.5 却成功返回了
FAILED test_p06_wrong_path_is_http_error     抛的是 JSONDecodeError
FAILED test_p06_not_a_list                   返回了 {'player': '张三', 'attempts': 5}
5 failed, 6 passed
```

## 复盘

::: tip 这题用到的
- **`requests.get(url, params=..., timeout=...)`**：查询参数交给 `params`，它负责编码；值为 `None` 的参数会被丢掉，列表会生成重复的键
- **`timeout` 每次都要写**，而且要用调用方传进来的那个。它限制的是连接和每次读取的等待时间，不是总时长
- **`raise_for_status()` 在 `json()` 之前**；它只在 400 到 599 时抛 `HTTPError`，异常上的 `e.response` 能拿到状态码和正文
- **`json()` 只保证是合法 JSON**，是不是你要的结构要自己检查（M4 第 3 题的道理）
:::

这一题里的失败都直接抛了 requests 自己的异常。可是调用方拿到异常以后该怎么办？超时可以重试，404 重试一百次也没用，429 要等一会儿。下一题把这些失败分门别类。

## 自测

1. `requests.get(f"{url}?player={name}")` 在 `name` 是 `A&B` 和 `C#` 时，服务端分别收到什么？
2. 服务器返回 404 和一段 HTML 时，先调 `json()` 会看到什么报错？为什么说它会误导排查？
3. `timeout=1` 时，一个每 0.5 秒发一个字节、总共要 3 秒的回应会超时吗？

<details>
<summary>参考答案</summary>

1. `A&B`：服务端收到两个参数，`player=A` 和一个空的 `B`。`C#`：`#` 后面的部分不会被发出去，服务端只收到 `player=C`。用 `params=` 就不会有这些问题。
2. `JSONDecodeError: Expecting value: line 1 column 1 (char 0)`。它让人以为是返回的数据格式有问题，其实是地址写错了，服务器回了一个 404 页面。先 `raise_for_status()`，报错里直接有状态码和 URL。
3. 不会。`timeout` 限制的是两次收到数据之间的等待，每次只等 0.5 秒，不超过 1 秒，整个请求花了约 2.5 秒照样成功。

</details>

</Reveal>
