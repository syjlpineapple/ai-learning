---
kind: problem
outline: [2, 2]
time: 40 分钟
uses: [重试与退避, Retry-After, 依赖注入, 裸 raise]
record:
  - text: Day16 异常分层
    link: https://github.com/syjlpineapple/ai-learning/blob/main/courseware/records/python/Day16.md
---

# 第 8 题 · 失败了就重试

第 7 题已经能判断一个异常值不值得重试。这一题真的去重试：失败了等一会儿再来，等的时间一次比一次长，试够次数还不行就放弃，把最后那个异常交给调用方。

## 题目

打开 [`code/m05_http/p08_retry_exercise.py`](../../code/m05_http/p08_retry_exercise.py)，实现两个函数：

```python
def retry_after(exc: Exception) -> float | None: ...

def with_retry(call: Callable[[], T], attempts: int = 3, base_delay: float = 0.5,
               sleep: Callable[[float], None] = time.sleep) -> T: ...
```

`with_retry(lambda: fetch_scores(url))` 调用传进来的函数，失败了按规则重试，成功就返回它的结果。`classify` 和 `should_retry` 用第 7 题的参考答案，已经导入好了。

**要求**

1. 最多调用 `call` 共 `attempts` 次（包括第一次）。都失败了，**把最后一次的异常原样抛出去**
2. 不值得重试的异常（404、URL 写错）立刻抛出；不是 requests 的异常（比如 `KeyError`）也立刻抛出。这两种情况一秒都不等
3. 每次重试前等一会儿：异常是带 `Retry-After` 头（秒数）的 `HTTPError` 时，按头里写的等；否则等 `base_delay × 2^(n-1)`，也就是 0.5 秒、1 秒、2 秒……**最后一次失败之后不用再等**
4. 每次重试前记一条 `WARNING`，写明第几次失败、类别（`classify` 的结果）、要等几秒，比如 `第 1 次失败（server_error），0.5 秒后重试`

`sleep` 参数默认是 `time.sleep`。测试会换成一个只记录、不真等的函数，这样能检查你每次等了多久，测试也不会真的等上好几秒。这是第 1.6 章依赖注入的用法。

**验证**（在 `code/` 目录下）

```powershell
pytest tests/test_m05.py -k p08 -v
```

现在是 `13 passed, 12 skipped`，全部做完是 `25 passed`。

::: details 提示：要求 1，三次都失败了却返回了 None
`for` 循环跑完以后，函数会从哪里返回？想一想最后一次失败时应该做什么。
:::

::: details 提示：要求 3，最后一次失败之后还等了 2 秒
在 `sleep` 之前判断一下：这是不是最后一次？是的话就不用等了，直接抛出去。
:::

::: details 提示：要求 3，Retry-After 读不出来
`exc.response.headers.get("Retry-After")` 拿到的是字符串，比如 `"2"`。它也可能是一个日期，`float()` 转不了的时候返回 `None`。
:::

<Reveal>

## 讲评

### 参考答案

```python
def retry_after(exc: Exception) -> float | None:
    if not isinstance(exc, requests.exceptions.HTTPError) or exc.response is None:
        return None
    value = exc.response.headers.get("Retry-After")
    if value is None:
        return None
    try:
        seconds = float(value)
    except ValueError:
        return None
    return seconds if seconds >= 0 else None


def with_retry(call, attempts=3, base_delay=0.5, sleep=time.sleep):
    for attempt in range(1, attempts + 1):
        try:
            return call()
        except requests.exceptions.RequestException as e:
            if not should_retry(e) or attempt == attempts:
                raise                                       # 原样抛出
            delay = retry_after(e)
            if delay is None:
                delay = base_delay * 2 ** (attempt - 1)
            logger.warning("第 %d 次失败（%s），%.1f 秒后重试", attempt, classify(e), delay)
            sleep(delay)
    raise ValueError(f"attempts 至少是 1，传进来的是 {attempts}")
```

`except` 只接 `RequestException`，`KeyError` 这类程序自己的 bug 根本进不来，直接穿过去。`should_retry` 遇到它不认识的 requests 异常也会原样抛出（第 7 题坑 4）。

### 坑 1：循环跑完，悄悄返回了 `None`

典型初稿：

```python
for i in range(attempts):
    try:
        return call()
    except requests.exceptions.RequestException as e:
        delay = base_delay * 2 ** i
        logger.warning(f"请求失败：{e}，{delay} 秒后重试")
        sleep(delay)
return None
```

服务端连续返回 503，测试的结果：

```text
3 次都失败了，却返回了 None —— 最后一次的异常要抛出来
等待：[0.5, 1.0, 2.0]
```

两个问题。一是调用方拿到 `None`，以为查到了一个「什么都没有」的排行榜，这正是第 5 题讨论的「返回值的语义歧义」。二是第 3 次失败之后还白等了 2 秒才返回。参考答案在 `except` 里判断「这是不是最后一次」，是的话就用裸 `raise` 把这个异常原样抛出，调用方看到的是真正的 `HTTPError: 503`。

### 坑 2：什么都重试

初稿 `except RequestException` 之后不做任何判断，404 也重试了三次：

```text
WARNING 请求失败：404 Client Error: Not Found for url: .../api/scores?limit=10，0.5 秒后重试
WARNING 请求失败：404 Client Error: Not Found for url: .../api/scores?limit=10，1.0 秒后重试
WARNING 请求失败：404 Client Error: Not Found for url: .../api/scores?limit=10，2.0 秒后重试
```

地址写错了，再等多久也不会变对。白等 3.5 秒，日志里多出三条警告，最后调用方拿到的还是 `None`。

### 坑 3：`Retry-After` 是服务端给的等待时间

429 和 503 的响应经常带一个 `Retry-After` 头，告诉你多少秒以后再来。初稿不看这个头，测试里服务端说「等 2 秒」，它只等了 0.5 秒就又来了，这正是服务端返回 429 想要避免的事。

头的值永远是字符串。HTTP 标准还允许它写成一个日期（比如 `Wed, 21 Oct 2026 07:28:00 GMT`），参考答案只处理秒数，遇到看不懂的写法就退回到翻倍的规则。测试把这两种写法都试了。

### 坑 4：重试的日志写什么

初稿的日志是 `f"请求失败：{e}，{delay} 秒后重试"`。它有第 4 题说过的 f-string 问题，而且信息不对路：异常的完整描述很长，真正有用的是「第几次」「什么类别」「等多久」。看日志的人一眼就能分清「偶尔失败一次」和「连续失败到放弃」。

每次重试只记 `WARNING`，不记 `logger.exception`。一次失败、重试成功了，不值得留一整段 traceback。最终放弃时异常会抛给调用方，由调用方决定要不要记 `exception`，这样同一个错误只记一次（Day16 的「只在一个边界记录」）。

### 最坏情况要等多久

`attempts=3`、`timeout=5`、每次都是超时：3 次请求各等 5 秒，中间再等 0.5 秒和 1 秒，一共 16.5 秒。重试会把「一次失败」放大成「好几次失败的时间总和」。给用户点击触发的请求，要把这个总时间和用户愿意等的时间对一下。

## 复盘

::: tip 这题用到的
- **只重试值得重试的**：第 7 题的分类决定重不重试；程序自己的 bug 永远不重试
- **最后一次失败用裸 `raise` 抛出原来的异常**，不要返回 `None`，也不要包成一个看不出原因的新异常
- **退避**：等待时间一次比一次长（0.5、1、2……），给服务端恢复的时间。服务端给了 `Retry-After` 就听它的
- **最后一次失败之后不等**
- **重试记 `WARNING`，不记 traceback**；放弃时交给调用方记一次
- **`sleep` 作为参数传进来**：测试能检查等了多久，又不用真的等
- **最坏耗时 = 次数 × timeout + 所有等待时间**
:::

这一题重试的都是 GET：查询排行榜，查几次结果都一样。下一题上传成绩用的是 POST，重试一次可能就多存一条成绩。

## 自测

1. `for` 循环里 `try: return call()`、`except: sleep(...)`，循环外 `return None`。所有尝试都失败时会发生什么？有哪两个问题？
2. 为什么 404 不该重试，而 503 和 429 该重试？`Retry-After` 是做什么用的？
3. `attempts=3`、`timeout=5`、`base_delay=0.5`，每次都超时，最多要等多久才会失败？

<details>
<summary>参考答案</summary>

1. 函数返回 `None`。问题一：调用方分不清「失败了」和「结果是空的」，真正的异常丢了。问题二：最后一次失败之后还会再 `sleep` 一次，白白多等。应该在最后一次失败时用裸 `raise` 把异常抛出去。
2. 404 说明地址或者请求本身有问题，等多久都不会变；503 是服务端暂时出问题，429 是请求太频繁，过一会儿都可能恢复。`Retry-After` 是服务端告诉客户端「过多少秒再来」，按它等最不会给服务端添乱。
3. 3 次请求各等 5 秒，共 15 秒，中间还要等 0.5 秒和 1 秒，一共 16.5 秒。

</details>

</Reveal>
