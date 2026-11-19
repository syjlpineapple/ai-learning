---
kind: lesson
outline: [2, 2]
time: 40 分钟
uses: [requests.post, json= 与 data=, logger.exception 的参数, raise 与 raise e, except 的顺序]
record:
  - text: 当时的完整代码（没存成文件，记在学习记录里）
    link: https://github.com/syjlpineapple/ai-learning/blob/main/courseware/records/python/Day17.md
---

# Day 17：POST 请求

前两天都是「问服务器要数据」，用 GET。今天反过来，「把数据交给服务器」，用 POST。以后给大模型发消息，就是把你的对话内容 POST 过去。

今天还有一件事：Day 14、15、16 连着踩了三次的 `except` 顺序问题，今天终于排对。

## 一、`json=` 和 `data=`

POST 的数据放在请求体里，requests 给了两种放法。用本机服务的 `/echo` 看看服务器实际收到了什么：

```python
user = {"name": "Python", "remark": "你好"}

r = requests.post(base + "/echo", json=user, timeout=10)
print(r.json()["headers"]["Content-Type"])
print(r.json()["body"])

r = requests.post(base + "/echo", data=user, timeout=10)
print(r.json()["headers"]["Content-Type"])
print(r.json()["body"])
```

```text
application/json
{"name": "Python", "remark": "\u4f60\u597d"}
application/x-www-form-urlencoded
name=Python&remark=%E4%BD%A0%E5%A5%BD
```

| 参数 | 请求体 | 自动设置的 `Content-Type` |
|---|---|---|
| `json=` | JSON 文本 | `application/json` |
| `data=`（传字典） | 表单格式 `a=1&b=2` | `application/x-www-form-urlencoded` |

`json=` 做了两件事：把字典变成 JSON 文本，顺手把 `Content-Type` 设好。传错了会怎样？本机服务的上传接口只收 JSON：

```python
r = requests.post(base + "/scores", data={"player": "张三", "attempts": 3}, timeout=10)
print(r.status_code, r.json())
r = requests.post(base + "/scores", json={"player": "张三", "attempts": 3}, timeout=10)
print(r.status_code, r.json())
```

```text
415 {'error': "请求体必须是 JSON，收到的 Content-Type 是 'application/x-www-form-urlencoded'"}
201 {'id': 8, 'player': '张三', 'attempts': 3}
```

用哪个，看 API 文档。大模型的接口一律 `json=`。

## 二、`logger.exception()` 里写什么

`logger.exception()` 自己会把异常的类型、消息和 traceback 记下来。那括号里该写什么？对比一下：

```python
text = "abc"
try:
    int(text)
except ValueError as e:
    logger.exception(e)
    print("-----")
    logger.exception("把用户输入转成整数失败，输入：%r", text)
```

```text
ERROR demo: invalid literal for int() with base 10: 'abc'
Traceback (most recent call last):
  File "demo.py", line 9, in <module>
    int(text)
    ~~~^^^^^^
ValueError: invalid literal for int() with base 10: 'abc'
-----
ERROR demo: 把用户输入转成整数失败，输入：'abc'
Traceback (most recent call last):
  File "demo.py", line 9, in <module>
    int(text)
    ~~~^^^^^^
ValueError: invalid literal for int() with base 10: 'abc'
```

传 `e`，第一行和最后一行说的是同一件事；传一句描述，日志里就多了「程序当时在干什么、对谁干」。所以括号里写**上下文**，比如 `"POST 请求失败，URL: %s", url`。

重新抛出用裸 `raise`，不用 `raise e`。裸 `raise` 原样交出当前异常，不会把抛出点改到这一行。用了 `logger.exception()` 加裸 `raise`，`as e` 也就用不上了，可以不写。

## 三、`logger.setLevel()` 不是配置日志

```python
logger.setLevel(logging.INFO)
logger.info("这条 INFO 能看到吗")
logger.warning("这条 WARNING 能看到吗")
```

```text
这条 WARNING 能看到吗
```

INFO 没出来。`setLevel` 只是把这一个 logger 的门槛调低了，但日志往哪儿输出、什么格式，一个都没配。WARNING 能出来，靠的是 Day 13 见过的那个兜底。入口处要用 `logging.basicConfig(level=logging.INFO, format=...)`。

## 四、`except` 终于排对了

把可能出错的地方都列出来，再按家谱排顺序：

```python
def post_user(url: str, user: dict) -> Any:
    try:
        response = requests.post(url, json=user, timeout=10)
        response.raise_for_status()
        return response.json()
    except ValueError:                                  # ① JSON 解析失败
        logger.exception("服务器响应 JSON 解析失败")
        raise
    except requests.exceptions.Timeout:                 # ② 超时
        logger.exception("请求超时")
        raise
    except requests.exceptions.ConnectionError:         # ③ 连不上
        logger.exception("连接失败")
        raise
    except requests.exceptions.RequestException:        # ④ 其他，兜底
        logger.exception("请求异常")
        raise
```

为什么这么排：

- ① 必须在 ④ 前面。JSON 解析失败抛的异常同时是 `ValueError` 和 `RequestException`，④ 在前就会被它抢走。
- ②、③ 不会被 ① 抢走。它们只是 `RequestException`，不是 `ValueError`。
- ④ 是 ②、③ 的父亲，只能放最后。

服务器返回 500 时，`raise_for_status()` 抛出 `HTTPError`，同一个 `try` 里后面的 `response.json()` **一行都不会执行**，异常直接去找 `except`：①、②、③ 都对不上，④ 接住，记日志，再 `raise` 给调用方。

不过要想一想：四个分支做的事一模一样，只是日志文字不同。**处理方式真的不同时才分开写**，比如超时要重试、连不上要告警。不然合成一个 `RequestException` 就够了，再加一个 `ValueError` 在它前面。

## 五、今天的作业

写 `post_user(url: str, user: dict)`：

1. 用 `requests.post()` 发 JSON，`timeout=10`
2. `raise_for_status()` 检查状态
3. 返回解析后的 JSON
4. 用 `logger.exception()` 记录异常，再 `raise` 往上抛
5. `main()` 里调用，打印服务器返回的数据

## 六、小测

**1.** 要给 AI 接口发一段 JSON 格式的用户消息，用哪个参数？

- A. `json=`
- B. `data=`
- C. `params=`

**2.** 服务器返回 HTTP 500，下面会打印什么？

```python
try:
    response = requests.post(url, json=user, timeout=10)
    response.raise_for_status()
    return response.json()
except ValueError:
    print("A")
except requests.exceptions.HTTPError:
    print("B")
except requests.exceptions.RequestException:
    print("C")
```

- A. A
- B. B
- C. C
- D. ABC

**3.** 函数没法处理网络异常时，应该怎么做？

- A. 直接返回 `None`
- B. 只打印错误
- C. 记录异常并 `raise`

<details>
<summary>答案</summary>

1. A。
2. B。`HTTPError` 不是 `ValueError`，第一条对不上；第二条对上就停，不会再往下看。
3. C。

</details>

## 讲评（11-04）

三道理解题和最后那道 A/B/C 你都答对了。代码改了四版。

**第一版**有五个问题：`requests.post` 漏了 `timeout`（Day 15 刚学过，换成 POST 就忘了）；`logger.exception(e)`；`raise e`；只接了 `HTTPError`，超时和连不上会不记日志就穿出去；入口用的是 `logger.setLevel()`。第二、三节讲的就是其中三条。

**第二、三版**补上了 `timeout`、改成了裸 `raise`，还主动加了超时和连接失败的分支。但写的是 `except TimeoutError` 和 `except ConnectionError`，这是 Python **内置**的两个异常，不是 requests 的。它们之间没有继承关系：

```python
print(issubclass(requests.exceptions.ConnectionError, ConnectionError),
      issubclass(requests.exceptions.Timeout, TimeoutError))
```

```text
False False
```

所以这两个分支一个 requests 的异常也接不住，要写全名 `requests.exceptions.Timeout`、`requests.exceptions.ConnectionError`。

**第四版**全对，而且 `ValueError` 排在了最前面。GPT 的评价是「正确考虑了 JSON 解码异常的多重继承」，Day 14 以来连踩三次的坑，到这里改对了。拿最终版对着本机服务跑四种情况，日志的第一行分别是：

```text
---- post_user：500
ERROR __main__: 请求异常
---- post_user：200 但不是 JSON
ERROR __main__: 参数解析失败
---- post_user：服务已经关了
ERROR __main__: 连接失败
```

（正常的那次直接返回了 `/echo` 的结果，没有日志。每条日志后面都跟着 traceback，这里只留第一行。）

每种失败都进了对的分支。剩下一处措辞：「参数解析失败」容易让人以为是**你传进去的参数**有问题，其实出错的是服务器返回的数据，写成「服务器响应 JSON 解析失败」更准确。日志的文字会直接影响别人往哪个方向排查。

> 注意：GPT 给的参考 `main()` 里，`except RequestException` 又写在了 `except ValueError` 前面，「数据格式错误」那句提示永远不会出现。同一个 bug 在一个文件里出现两次，改的时候要全文搜一遍。

## 加练

[上传成绩](加练/day17_上传成绩.md)：用 POST 往本机服务上传成绩，练 `json=` 和 `data=`、请求头，还会碰到一个 GET 没有的问题：POST 失败后重试，可能把同一条成绩存两次。
