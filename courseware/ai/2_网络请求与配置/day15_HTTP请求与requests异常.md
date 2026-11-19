---
kind: lesson
outline: [2, 2]
time: 45 分钟
uses: [HTTP 状态码, requests.get, timeout, raise_for_status, requests 异常树]
record:
  - text: 当时的代码 Day15/day_15.py
    link: https://github.com/syjlpineapple/ai-learning/blob/main/dailypractice/Day15/day_15.py
---

# Day 15：HTTP 请求与 requests 异常

前 14 天，程序只和本机的文件打交道。从今天起，它要去和别的服务「说话」：发一个请求，拿回一份数据。

以后调大模型也是这一套。GPT、Claude 的接口都是 HTTP API，今天的三行代码会一直用下去。

> 当时练习用的是外网的 httpbin.org。这一页的演示换成了仓库里自带的小服务 `courseware/ai/code/m05_http/server.py`，它只在你自己的电脑上运行，不用联网，还能故意变慢、出错。演示脚本放在 `courseware/ai/code/` 下运行，开头这样起服务：
>
> ```python
> import requests
> from m05_http.server import running_server
>
> with running_server() as srv:
>     base = srv.base_url      # 比如 http://127.0.0.1:63829，端口每次随机
>     ...                      # 在这里发请求，离开 with 服务自动关掉
> ```

## 一、请求和响应

一次 HTTP 调用分两半：你发出**请求**（要哪个地址、带什么参数），服务器回一个**响应**（状态码、响应头、正文）。

状态码记住三类就够了：

| 状态码 | 意思 | 该怎么办 |
|---|---|---|
| 2xx，比如 200 | 成功 | 解析数据 |
| 4xx，比如 400、401、404 | **你的**请求有问题：参数错、没授权、地址错 | 改代码或参数，重试没用 |
| 5xx，比如 500 | **服务器**出问题了 | 等一会儿重试，可能就好了 |

这个区分直接决定出错以后怎么办，后面讲重试时会用上。

`requests` 不是标准库，要先装：`python -m pip install requests`。用 `python -m pip` 而不是直接敲 `pip`，是为了装进**当前这个** Python 里，机器上有好几个 Python 时最容易装错地方。

## 二、三行关键代码

```python
response = requests.get(base + "/scores?limit=3", timeout=10)   # ① 发请求
print(response.status_code)
print(response.headers["Content-Type"])
response.raise_for_status()                                     # ② 检查状态码
data = response.json()                                          # ③ 解析正文
print(type(data).__name__, data)
```

```text
200
application/json; charset=utf-8
list [{'player': '100%', 'attempts': 1}, {'player': '张三', 'attempts': 2}, {'player': '李四', 'attempts': 3}]
```

注意 `data` 是个**列表**。`response.json()` 不保证返回字典，JSON 最外层是什么，它就给你什么。

`raise_for_status()` 在 2xx 时什么也不做，在 4xx / 5xx 时抛 `HTTPError`。换一个不存在的地址试试：

```python
r = requests.get(base + "/nope", timeout=10)
print(r.status_code, r.text)
try:
    r.raise_for_status()
except requests.exceptions.HTTPError as e:
    print(type(e).__name__, e)
```

```text
404 <html><head><title>404 Not Found</title></head><body>Not Found</body></html>
HTTPError 404 Client Error: Not Found for url: http://127.0.0.1:63829/nope
```

顺序为什么是先 ② 后 ③？因为 `response.json()` 根本不看状态码。跳过检查直接对这个 404 调 `r.json()`，接住异常打印出来：

```text
JSONDecodeError Expecting value: line 1 column 1 (char 0)
```

报错说「JSON 解析失败」，真正的原因却是「地址写错了」。先检查状态码，错误信息才会指向对的地方。

`status_code` 和 `raise_for_status()` 的区别也在这里：前者给你一个数字，你得记得自己判断；后者直接抛异常，忘不掉。

## 三、`timeout`：一定要写

requests 默认**永远等下去**。对方不回话，你的程序就一直挂着，没有报错，也没有日志。

服务端的 `/slow?seconds=2` 会等 2 秒才回答，客户端只肯等 0.5 秒：

```python
try:
    requests.get(base + "/slow?seconds=2", timeout=0.5)
except requests.exceptions.Timeout as e:
    print(type(e).__name__, e)
```

```text
ReadTimeout HTTPConnectionPool(host='127.0.0.1', port=63829): Read timed out. (read timeout=0.5)
```

但 `timeout` 不是「整个请求最多这么久」。它管的是「建立连接」和「两次收到数据之间」各自最多等多久。`/trickle?seconds=3` 每 0.5 秒挤出一个字节：

```python
start = time.perf_counter()
r = requests.get(base + "/trickle?seconds=3", timeout=1)
print("trickle", r.status_code, round(time.perf_counter() - start, 1), "秒")
```

```text
trickle 200 2.5 秒
```

设了 1 秒超时，请求却花了 2.5 秒，而且成功了，因为每次等下一个字节都没超过 1 秒。

## 四、requests 的异常树

请求可能在好几个地方失败，requests 给每种失败起了名字，它们有一个共同的祖先 `RequestException`：

```text
RequestException
├── ConnectionError     连不上：地址不对、服务没开、断网
├── Timeout             超时（ReadTimeout 是它的子类）
├── HTTPError           raise_for_status() 在 4xx / 5xx 时抛的
└── JSONDecodeError     response.json() 解析失败
```

所以 `except requests.exceptions.RequestException` 能兜住上面所有情况。

最后一个要特别看一眼它的家谱：

```python
print([c.__name__ for c in requests.exceptions.JSONDecodeError.__mro__])
```

```text
['JSONDecodeError', 'InvalidJSONError', 'RequestException', 'OSError', 'JSONDecodeError', 'ValueError', 'Exception', 'BaseException', 'object']
```

它有两个「爸爸」：既是 `RequestException`，又是 `ValueError`（中间那个 `JSONDecodeError` 是标准库 `json` 里的）。记住这个双重身份，下面的讲评就出在这里。

## 五、今天的作业

写 `fetch_data(url)`：

1. 用 `requests.get()` 请求，设置 `timeout`
2. 检查状态码，成功时解析 JSON 并返回
3. 处理请求异常和 JSON 解析异常，不用 `except Exception`
4. 在 `main()` 里调用并打印结果

当时的测试地址是 `https://httpbin.org/json`。回答三个问题：

1. 为什么调用外部 API 要设 `timeout`？
2. `status_code` 和 `raise_for_status()` 有什么区别？
3. 服务器返回 HTTP 200，但正文不是合法 JSON，会发生什么？

## 六、小测

**1.** 返回 401，最可能是什么问题？重试有用吗？

- A. 服务器挂了，等会儿重试
- B. 身份凭证缺了或不对，重试没用

**2.** `requests.get(url, timeout=10)` 能保证整个请求不超过 10 秒吗？

- A. 能
- B. 不能

**3.** `except requests.exceptions.RequestException` 能接住 `raise_for_status()` 抛的 `HTTPError` 吗？

- A. 能
- B. 不能

<details>
<summary>答案</summary>

1. B。4xx 是请求方的问题，要去检查 API Key。
2. B。它限制的是连接和每次等数据的时间，第三节的 trickle 就花了 2.5 秒。
3. A。`HTTPError` 是 `RequestException` 的子类。

</details>

## 讲评（10-28）

你交的代码：

```python
import requests
from requests import HTTPError

def fetch_data(url:str):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print("请求失败：", e)
        return None
    except ValueError as e:
        print("响应数据无法解析：", e)
        return None
```

主线是对的：设了超时，先检查状态码再解析，也没用 `except Exception`。问题 1、2 的回答方向都对。`from requests import HTTPError` 导入了却没用到，可以删。

问题 3 你答的是「会打印：响应数据无法解析，结果为空」。当时 GPT 判了「基本正确」，其实这里不对。用你的 `fetch_data` 去请求本机服务的 `/html`（状态码 200，正文是 HTML）：

```text
请求失败： Expecting value: line 1 column 1 (char 0)
结果： None
```

打印的是「请求失败」，不是「响应数据无法解析」。原因就是第四节那个双重身份：`JSONDecodeError` 也是 `RequestException`，而 `except` 从上往下比，第一条就对上了。`except ValueError` 那四行一次都不会执行，是死代码。

后果不只是提示文字不对：请求其实完全成功了，是对方给的格式不对，可提示把人引去查网络。改法是把具体的那个放到前面：

```python
except requests.exceptions.JSONDecodeError as e:
    print("响应数据无法解析：", e)
    return None
except requests.exceptions.RequestException as e:
    print("请求失败：", e)
    return None
```

> 注意：当天 GPT 讲课时给的演示代码也是 `RequestException` 在前、`ValueError` 在后，同样是死代码。这是昨天「子类写在前面」那条规则换了个场景又出现，Day 16 还会再遇到一次，Day 17 才改对。

还有一件事明天要解决：`print` 加 `return None` 以后，调用方只拿到 `None`，分不清是超时、404 还是格式不对。而这几种情况该不该重试，答案正好相反。

## 加练

- [查询排行榜](加练/day15_查询排行榜.md)：对本机服务的 `/scores` 发 GET，练 `params`、`timeout`、`raise_for_status` 和 `response.json()`，也就是今天的三行代码。
- [失败分类](加练/day15_失败分类.md)：把各种请求失败分到七类里，判断该不该重试，专门练异常树和多重继承下的判断顺序。
