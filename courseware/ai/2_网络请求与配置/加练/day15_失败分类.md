---
kind: problem
outline: [2, 2]
time: 40 分钟
uses: [requests 异常树, 多重继承, isinstance 的顺序, e.response.status_code]
record:
  - text: Day15 异常体系
    link: https://github.com/syjlpineapple/ai-learning/blob/main/courseware/records/python/Day15.md
  - text: Day17 except 顺序修正
    link: https://github.com/syjlpineapple/ai-learning/blob/main/courseware/records/python/Day17.md
---

# 第 7 题 · 失败分类

第 6 题的 `fetch_scores` 失败时抛的是 requests 自己的异常。调用方拿到之后要决定怎么办：

- 超时、连不上、服务端 5xx：等一会儿重试，可能就好了
- 429（请求太频繁）：也该等一会儿再试
- 404、400：请求本身有问题，重试一百次也一样
- URL 写错了：重试没用，该去改配置

这一题写一个分类函数，把异常归到七类里，并据此判断该不该重试。Day14 到 Day17 在 `except` 的顺序上连续踩了四次坑，这一题把所有容易排错的情况都放进了测试里。

## 题目

打开 [`code/m05_http/p07_classify_exercise.py`](../../code/m05_http/p07_classify_exercise.py)，实现两个函数：

| 函数 | 做什么 |
|---|---|
| `classify(exc)` | 返回异常的类别名，类别见下表。不是 requests 的异常（比如 `KeyError`）原样抛出去 |
| `should_retry(exc)` | 这个异常值不值得重试，按 `RETRYABLE` 表查 |

| 类别 | 是什么 | 重试 |
|---|---|---|
| `unreachable` | 连不上服务器，**包括连接阶段就超时** | 是 |
| `slow` | 连上了，等回应时超时 | 是 |
| `rate_limited` | 状态码 429 | 是 |
| `server_error` | 状态码 5xx | 是 |
| `client_error` | 其他 4xx | 否 |
| `bad_response` | 回应不是期望的 JSON（`JSONDecodeError`、第 6 题的 `InvalidJSONError`） | 否 |
| `bad_url` | URL 写错了（`MissingSchema`、`InvalidSchema`、`InvalidURL`） | 否 |

测试会真的发请求，拿到真实的异常对象来考你的函数：对着本机服务请求 `/slow`、`/status/429`、`/html`，对着一个刚关掉的端口发请求，用 `example.com/scores`（漏写 `http://`）这样的地址发请求。

**验证**（在 `code/` 目录下）

```powershell
pytest tests/test_m05.py -k p07 -v
```

现在是 `19 passed, 15 skipped`，全部做完是 `34 passed`。

开始之前，先把这几个异常的继承关系查一遍：

```python
import requests
E = requests.exceptions
for cls in (E.ConnectTimeout, E.ReadTimeout, E.JSONDecodeError, E.MissingSchema):
    print(cls.__name__, [c.__name__ for c in cls.__mro__])
```

::: details 提示：ConnectTimeout 被归成了 slow
看它的 `__mro__`：它同时继承了两个类。你先判断的是哪一个？
:::

::: details 提示：MissingSchema 被归成了 bad_response
你是不是用 `ValueError` 来判断「回应不是 JSON」？`JSONDecodeError` 是 `ValueError`，可 URL 写错时抛的那几个也是。有一个更精确的父类，只包括 JSON 相关的两个异常。
:::

::: details 提示：连接被拒绝被归成了 bad_url，或者干脆没认出来
检查一下你写的是 `ConnectionError` 还是 `requests.exceptions.ConnectionError`。
:::

<Reveal>

## 讲评

### 参考答案

```python
def classify(exc: Exception) -> str:
    if isinstance(exc, E.ConnectionError):          # 包括 ConnectTimeout
        return "unreachable"
    if isinstance(exc, E.Timeout):                  # 走到这里只剩 ReadTimeout
        return "slow"
    if isinstance(exc, E.HTTPError):
        status = exc.response.status_code if exc.response is not None else None
        if status == 429:
            return "rate_limited"
        if status is not None and 400 <= status < 500:
            return "client_error"
        return "server_error"
    if isinstance(exc, E.InvalidJSONError):         # 包括 JSONDecodeError
        return "bad_response"
    if isinstance(exc, (E.MissingSchema, E.InvalidSchema, E.InvalidURL)):
        return "bad_url"
    raise exc


def should_retry(exc: Exception) -> bool:
    return RETRYABLE[classify(exc)]
```

**判断的顺序就是答案。** 这里用的是一串 `isinstance`，和一串 `except` 的道理完全一样：从上往下，第一个匹配上的生效。

### 坑 1：requests 的异常有好几个是「多重继承」

```text
ConnectTimeout   → ConnectionError, Timeout, RequestException, OSError
ReadTimeout      → Timeout, RequestException, OSError                    （不是 ConnectionError）
JSONDecodeError  → InvalidJSONError, RequestException, OSError, json.JSONDecodeError, ValueError
MissingSchema    → RequestException, OSError, ValueError
InvalidSchema    → RequestException, OSError, ValueError
InvalidURL       → RequestException, OSError, ValueError
```

`JSONDecodeError` 同时是 `ValueError`，这件事 Day15 就发现了。Day17 的结论是「`ValueError` 要放在最前面」。可是表里后三个也都是 `ValueError`：URL 写错时抛的异常，也会被 `except ValueError` 接住。实测：

```text
get("example.com/scores")      → MissingSchema   isinstance(e, ValueError) = True
get("127.0.0.1:8765/scores")   → InvalidSchema   isinstance(e, ValueError) = True
get("http://")                 → InvalidURL      isinstance(e, ValueError) = True
```

按 Day17 最终版的写法，漏写 `http://` 时，日志会记成「服务器响应 JSON 解析失败」。**`ValueError` 太宽了。** 精确的写法是 `requests.exceptions.InvalidJSONError`（或者它的子类 `JSONDecodeError`），它只包括「回应不是 JSON」这一种情况。

`ConnectTimeout` 同时是 `ConnectionError` 和 `Timeout`。它表示连接都没建起来，和「连上了但回应太慢」不是一回事，所以要先判断 `ConnectionError`。这在 Windows 上很常见：

```text
对一个已经关掉的端口发请求（本机实测）
timeout=0.5  →  0.52 秒后  ConnectTimeout
timeout=2    →  2.00 秒后  ConnectTimeout
timeout=3    →  2.03 秒后  ConnectionError
```

同一个关掉的端口，`timeout` 短于 2 秒时报的是 `ConnectTimeout`，长于 2 秒才是 `ConnectionError`。Windows 遇到被拒绝的连接会自己重试大约 2 秒才放弃，用 `socket.connect` 直接连也一样是 2.05 秒。Linux 上一般会立刻报拒绝，本机没有实测。如果先判断 `Timeout`，「服务没开」就会在 Windows 上被当成「服务很慢」。

### 坑 2：漏写 `requests.exceptions.`，用的是内置的同名异常

```python
if isinstance(exc, ConnectionError):      # 没有 import，用的是 Python 内置的 ConnectionError
```

```text
issubclass(requests.exceptions.ConnectionError, ConnectionError)   →  False
issubclass(requests.exceptions.Timeout, TimeoutError)              →  False
```

名字一模一样，但它们是两个毫无关系的类。requests 的 `ConnectionError` 继承自 `RequestException`，不是内置的 `ConnectionError`。初稿这样写，「连接被拒绝」一路落到了最后的 `RequestException` 分支，被归成了 `bad_url`。

`except ConnectionError:` 也一样接不住它，而且不会有任何提示。ruff 和 mypy 都不会报，因为内置的 `ConnectionError` 本来就是合法的名字。**用 requests 的异常时，写全 `requests.exceptions.XXX`**，或者像参考答案那样 `E = requests.exceptions`。

### 坑 3：429 是 4xx，但值得重试

```python
return "server_error" if exc.response.status_code >= 500 else "client_error"
```

初稿把 429 归成了 `client_error`，不重试。429 是服务端在说「你太快了，过一会儿再来」，重试本来就是它期望的做法。Day15 说「4xx 是客户端问题，重试没用」，这句话对大多数 4xx 成立，429 是要单独处理的例外。

`exc.response` 是 `raise_for_status()` 抛出 `HTTPError` 时带上的那次响应，状态码和正文都在上面：

```text
e.response.status_code   →  503
e.response.json()        →  {'error': '服务端按要求返回了 503'}
```

自己构造的 `HTTPError("...")` 没有 `response`，是 `None`，所以参考答案先判断了一下。

### 坑 4：不认识的异常不要硬归类

`classify(KeyError(...))` 应该把 `KeyError` 原样抛出去。初稿最后有一个 `raise exc`，这一条过了。如果写成 `return "server_error"` 之类的兜底，一个程序自身的 bug 就会被当成网络问题重试，永远修不好。这和第 1.5 章「`try` 包大了会伪装 bug」是同一件事。

### 典型初稿会被哪些测试抓住

初稿：先判断 `Timeout`、用内置的 `ConnectionError`、用 `ValueError` 判断回应格式、按 `>= 500` 区分 4xx 和 5xx。

```text
FAILED classify[unreachable-0]    ConnectionError 应该归为 unreachable，你归成了 bad_url     坑 2
FAILED classify[unreachable-1]    ConnectTimeout 应该归为 unreachable，你归成了 slow         坑 1
FAILED classify[rate_limited-0]   429 应该归为 rate_limited，你归成了 client_error           坑 3
FAILED classify[bad_response-1]   InvalidJSONError 应该归为 bad_response，你归成了 bad_url
FAILED classify[bad_url-0]        MissingSchema 应该归为 bad_url，你归成了 bad_response      坑 1
FAILED classify[bad_url-1]        InvalidSchema ……
FAILED classify[bad_url-2]        InvalidURL ……
FAILED should_retry               429
8 failed, 7 passed
```

`InvalidJSONError` 那一条是另一个方向的错：第 6 题抛的 `InvalidJSONError` 不是 `ValueError`（只有它的子类 `JSONDecodeError` 是），用 `ValueError` 判断就漏掉了它。**用 `ValueError` 判断回应格式，既会多接，也会漏接。**

## 复盘

::: tip 这题用到的
- **先查 `__mro__`，再排顺序**：多重继承的异常，要在它的每一个父类之前判断
- **`ConnectTimeout` 先于 `Timeout`**：它表示连接没建起来，Windows 上连一个关掉的端口，timeout 短时报的就是它
- **不要用 `ValueError` 判断「回应不是 JSON」**：URL 写错的三个异常也是 `ValueError`，而 `InvalidJSONError` 又不是。用 `requests.exceptions.InvalidJSONError`
- **写全 `requests.exceptions.ConnectionError`**：内置的 `ConnectionError`、`TimeoutError` 和它们同名但无关，工具不会提示
- **`e.response.status_code`** 区分 4xx 和 5xx；429 要单独处理
- **不认识的异常原样抛出**，不要硬归一类
:::

现在能判断「该不该重试」了，下一题就真的去重试：失败了等一会儿再试，最多试几次，每次等多久，日志怎么记才不会刷屏。

## 自测

1. `ConnectTimeout` 为什么要归为「连不上」而不是「太慢」？为什么在 Windows 上这一点尤其重要？
2. Day17 的结论是「`except ValueError` 放最前面」。用这个写法时，URL 漏写了 `http://`，日志会记成什么？为什么？
3. `except ConnectionError:` 能接住 `requests.get` 连接被拒绝时的异常吗？

<details>
<summary>参考答案</summary>

1. `ConnectTimeout` 表示连接阶段就超时了，服务器根本没连上，处理方式和「连不上」一样（检查服务开没开、地址对不对），和「连上了但回应慢」不同。Windows 连一个被拒绝的端口时会自己重试大约 2 秒，`timeout` 短于 2 秒时报的就是 `ConnectTimeout`，先判断 `Timeout` 的话「服务没开」会被当成「服务很慢」。
2. 会记成「服务器响应 JSON 解析失败」。漏写 `http://` 抛的是 `MissingSchema` 或 `InvalidSchema`，它们也继承 `ValueError`，被最前面的 `except ValueError` 先接住了。
3. 不能，除非写的是 `requests.exceptions.ConnectionError`。不加前缀的 `ConnectionError` 是 Python 内置的异常类，requests 的 `ConnectionError` 并不继承它，两者只是同名。

</details>

</Reveal>
