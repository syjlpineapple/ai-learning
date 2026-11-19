---
kind: lesson
outline: [2, 2]
time: 50 分钟
uses: [requests.Session, 函数还是类, URL 拼接, 三层结构, try / finally]
record:
  - text: 当时的代码 Day20/
    link: https://github.com/syjlpineapple/ai-learning/tree/main/dailypractice/Day20
---

# Day 20：APIClient 与分层

这 19 天你分别学了配置、HTTP 请求、日志、异常。今天把它们拼成一个小项目：一个专门负责和 API 打交道的 `APIClient` 类，加上配置和入口，三个文件各管一摊。

## 一、`requests.Session()`：一条连接用到底

前几天每次都是 `requests.get(...)`，每次都是一个独立的请求。本机服务会记下每个请求来自客户端的哪个端口，同一个端口就是同一条连接。连发三次看看：

```python
for _ in range(3):
    requests.get(base + "/scores?limit=1", timeout=10)
print(srv.state.client_ports)

with requests.Session() as s:
    for _ in range(3):
        s.get(base + "/scores?limit=1", timeout=10)
print(srv.state.client_ports)
```

```text
[50393, 50394, 50395]
[50396, 50396, 50396]
```

（两次打印之间清空过一次记录。）

顶层 `requests.get` 每次都新建一条连接；同一个 `Session` 三次请求走的是同一条。建连接有成本，HTTPS 还要多一轮加密握手，连续调好几个接口时差别就出来了。

`Session` 还会记住请求头。认证信息设一次，之后每个请求自动带上：

```python
self.session.headers.update({
    "Authorization": f"Bearer {api_key}",
    "Accept": "application/json",
})
```

`Authorization: Bearer <密钥>` 是最常见的 API 认证写法，大模型接口基本都用它。

## 二、什么时候把函数升级成类

关键在「一次」：`Session` 要在创建客户端时建一次，之后反复用。写在 `post()` 方法里，每次调用新建一个，连接和请求头就白设了。

函数做不到这一点，函数每次调用都从零开始。类的实例能**记住东西**（这里是 `session` 和 `base_url`），多次调用之间一直在。所以判断标准是：**有没有要在多次调用之间保持的状态？** 有就用类；像 Day 4 的 `check_num()` 那种纯计算，用函数就够了。别因为类看着更专业就用类。

对比一下调用的样子：

```python
# 函数：每次都传完整地址
post("https://api.example.com/users", data)

# 类：地址和密钥交给它一次，之后只关心业务
client = APIClient("https://api.example.com", api_key)
client.post("/users", data)
```

## 三、URL 拼接：两头各去一次斜杠

配置里的地址可能带结尾的 `/`，调用时 endpoint 可能带开头的 `/`，直接拼就成了双斜杠：

```python
print("https://x.com/" + "/users")
```

```text
https://x.com//users
```

有的服务器能容忍，有的直接 404。两头各去一次，再自己补一个：

```python
self.base_url = base_url.rstrip("/")
url = f"{self.base_url}/{endpoint.lstrip('/')}"
```

```text
'https://x.com'      'users'    -> https://x.com/users
'https://x.com/'     '/users'   -> https://x.com/users
'https://x.com//'    '//users'  -> https://x.com/users
```

## 四、三层：配置、请求、入口

```text
main.py          组装、决定出错了怎么办、最后关掉资源
   ↓
api_client.py    发请求、检查状态码、解析 JSON
   ↓
config.py        读配置、校验
```

| 文件 | 管什么 | 不该管什么 |
|---|---|---|
| `config.py` | 加载和校验配置 | 发请求 |
| `api_client.py` | 发请求、解析响应 | 出错后怎么办；读 `.env` |
| `main.py` | 组装各部分、决定对策、清理 | HTTP 细节 |

分层的好处很实在：哪天把 `requests` 换成别的库，只改 `api_client.py`。这也是 Day 16「底层记录、`raise`，上层决定」放大到文件级别。

## 五、`finally`：无论如何都要关

`Session` 占着连接，用完要 `close()`。放在 `finally` 里，成功、失败都会执行：

```python
client = APIClient(base + "/", "demo-key")
try:
    result = client.post("/echo", {"name": "jack"})
    print(result["method"], result["headers"]["Authorization"], result["headers"]["Accept"])
    print(result["body"])
    client.post("status/500", {"name": "jack"})
except requests.RequestException as e:
    print("main 拿到：", type(e).__name__)
finally:
    client.close()
    print("finally：已关闭")
```

这里的 `APIClient` 就是你 Day 20 的最终版，对着本机服务跑：

```text
POST Bearer demo-key application/json
{"name": "jack"}
ERROR dailypractice.Day20.api_client: 请求失败
Traceback (most recent call last):
  ……（省略）
requests.exceptions.HTTPError: 500 Server Error: Internal Server Error for url: http://127.0.0.1:50392/status/500
main 拿到： HTTPError
finally：已关闭
```

服务端收到了 `Authorization` 头，地址结尾的 `/` 和 `status/500` 也拼对了。500 那次，客户端记了日志、`raise`，`main` 接住，`finally` 照样关闭。哪怕 `try` 里是 `return`，`finally` 也会执行：

```python
def demo():
    try:
        return "try 里的 return"
    finally:
        print("finally 照样执行")

print(demo())
```

```text
finally 照样执行
try 里的 return
```

最后说一下 `except Exception`。Day 12 说过它是坏做法，但有一个地方可以用：**程序最外层的入口**。到了这一层，再往上抛就是把一堆 traceback 甩给用户。在这里统一接住，用 `logger.exception()` 把完整信息记下来，再给用户一句看得懂的话。前提是只在最外层用一次，里面各层照样接具体的异常。

## 六、今天的作业

1. `api_client.py`：实现 `APIClient`，`__init__` 接收 `base_url` 和 `api_key`、创建 `Session`、统一设置 `Authorization` 和 `Accept`；实现请求方法（`timeout=10`、`raise_for_status()`、JSON 解析失败和请求失败都记日志并 `raise`）；实现 `close()`
2. `main.py`：调用 `load_config()`，创建 `APIClient`，发请求，用 `try/except/finally` 处理异常并关闭，不打印 API Key

## 七、小测

**1.** `requests.Session()` 的主要作用是？

- A. 自动重试失败的请求
- B. 复用连接和会话配置
- C. 自动解析 JSON

**2.** `Session` 设过 `Authorization` 以后，每次 `session.post()` 还要再传吗？

- A. 要
- B. 不用

**3.** `client.post()` 抛了异常，`finally` 里的 `client.close()` 会执行吗？

- A. 会
- B. 不会

<details>
<summary>答案</summary>

1. B。
2. B。`Session` 记住了默认请求头。
3. A。这正是把清理放进 `finally` 的原因。

</details>

## 讲评（11-06）

代码交了三版，最后还问了一句「整体是否达标、能不能进入下一课」，GPT 的回答是可以：基础语法、异常、配置、HTTP 都已经达到阶段要求，面向对象基本达标，工程意识正在建立。

**第一版**是一个 `post(url, data)` 函数。请求逻辑完全正确，而且 `except JSONDecodeError` 写在了 `except RequestException` 前面，Day 17 的教训你主动用上了。但今天要练的是架构，这一版还是函数，没有 `Session`。`main.py` 里还有一处：

```python
from tests.dailypractice.Day20 import config
config = config.load_config()
```

这一行之后，`config` 就不再是模块，而是一个字典了。这次能跑，以后想调 `config` 里别的函数就会报一个让人摸不着头脑的错。改成 `from ...config import load_config` 加 `settings = load_config()`。

**第二版**升级成了类，用上了 `Session` 和统一的请求头，方向对了。剩下的问题：

- `APIClient(setting["api_base_url"], "ABCDEFG")`，密钥直接写在代码里，正是 Day 18 要避免的。`config.py` 应该读 `API_KEY` 并校验
- 没有 `close()`，`main.py` 也没有 `finally`
- `main.py` 还在 `from ...api_client import post, APIClient`，可模块里已经没有 `post` 这个函数了，这一行一运行就是 `ImportError`。把函数改成方法时，所有导入它的地方都要跟着改

**最终版**全部补齐：`base_url.rstrip("/")`、`timeout=10`、`close()`、`finally`、密钥从配置读。第五节的实测用的就是这一版。

回头看还有几处：

- `api_client.post("getUser", data)` 的返回值没人接，结果被丢掉了，应该 `result = api_client.post(...)`
- `config.py` 比 Day 19 退了两步：`.env.{env}` 是否存在的检查没了（又回到了「找不到也不报错」），默认环境从 `development` 变成了 `testing`。还有第一版漏了 `override=True` 和 `.resolve()`，都是前两天刚学的，换到新场景就忘了。这类遗漏靠记性防不住，要靠检查清单
- 请求头里手动设了 `Content-Type`，用 `json=` 时 requests 会自己设，多余但无害

## 加练

- [APIClient](加练/day20_APIClient.md)：把查询、上传收进一个类，配置在创建时交给它一次；还要让它支持 `with APIClient(...) as client:`，自动关闭，比手写 `finally` 更不容易忘。
- [程序入口](加练/day20_程序入口.md)：写最上面那一层，接收命令、组装各部件、处理各种异常、返回退出码，练的就是第四、五节的「入口该做什么」。
