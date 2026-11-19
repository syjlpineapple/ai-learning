# Day 20 · APIClient 类、Session 复用与分层架构

> **学习日** 2026-11-06（10:18 - 11:24，3 版迭代）
> **对应代码** [`dailypractice/Day20/`](../../../dailypractice/Day20/)（`api_client.py` / `config.py` / `main.py` / 三个 `.env.*`）
> **原始对话** `courseware/_raw/markdown/08_Python每日练习出题 (1).md`（对话里称「Day 20」）

> A 线第一个真正像「项目」的作业：把前 19 天的配置管理、HTTP 请求、日志、异常处理整合成三个各司其职的模块。

## 本节掌握

- `requests.Session()` 的作用：复用 Headers、Cookie、**TCP 连接**
- 为什么 Session 要在 `__init__` 里创建一次
- `rstrip("/")` + `lstrip("/")` 拼 URL，避免双斜杠
- 什么时候该从函数升级成类
- **三层分层架构**：`main.py` / `api_client.py` / `config.py`
- `try/except/finally` 与资源清理
- `except Exception` 唯一合理的使用场景

---

# 第一部分 · 知识讲解

## 1. `requests.Session()` 的作用

前面 5 天都是这样发请求：

```python
response = requests.get(url, timeout=10)
```

这是 requests 的顶层 API，每次调用都是独立的一次性请求。Session 的区别是**在多次请求之间保持状态**：

| 复用的东西 | 收益 |
|---|---|
| **Headers** | 认证信息设一次，之后每个请求自动带上 |
| **Cookie** | 登录后的会话状态自动维持 |
| **连接池（TCP 连接）** | 不用每次重新建连接，**这是性能上的实际收益** |
| 其他配置 | 代理、证书、重试策略等 |

连接复用这一点值得说清楚：HTTPS 请求建立连接要经过 TCP 三次握手加 TLS 握手，这个开销通常比传输数据本身还大。用顶层 `requests.get()` 时每次都要重新握手；Session 靠 HTTP keep-alive 复用已有连接，**连续调用多个接口时差距很明显**。

```python
session = requests.Session()
session.headers.update({"Accept": "application/json"})

response = session.get("https://httpbin.org/get", timeout=10)
```

> 调用大模型 API 的场景正好吃到这个好处：一次对话往往要连续发多个请求，而且每个请求都要带同一个 `Authorization`。

## 2. 为什么 Session 在 `__init__` 里创建

```python
class APIClient:
    def __init__(self, base_url: str, api_key: str):
        self.session = requests.Session()        # ← 整个客户端只建一次
```

**关键在于「一次」。** 如果写在 `post()` 方法里，每次调用都新建一个 Session，连接池和 Headers 都白设了——那就退化成了顶层 API，还多绕了一层。

这正是把它做成**类**的理由：类的实例可以持有状态（这里是 Session 和 base_url），在多次方法调用之间保持。函数做不到——函数每次调用都从零开始。

## 3. 什么时候该从函数升级成类

第一版写的是函数：

```python
def post(url: str, data: dict) -> Any:
    response = requests.post(url, json=data, timeout=30)
```

功能完全正确。但对比一下两种设计的调用方式：

```python
# 函数：每次都要传完整 URL，认证信息每次都要处理
post("https://api.example.com/users", data)
post("https://api.example.com/orders", data)

# 类：初始化时给一次，之后只关心业务
client = APIClient("https://api.example.com", api_key)
client.post("/users", data)
client.post("/orders", data)
```

**判断标准：有没有「需要在多次调用之间保持的状态」。**

| 情况 | 用什么 |
|---|---|
| 纯计算、无状态（如 `check_num()`） | 函数 |
| 需要保持连接、配置、认证（如 API 客户端） | 类 |
| 需要在调用间累积数据 | 类 |

不要因为「类看起来更专业」就用类。Day17 那条原则同样适用：**不要为了显得专业而增加复杂度。** 这里用类是因为真的有状态要保持。

## 4. URL 拼接：两个 strip

```python
self.base_url = base_url.rstrip("/")                      # 去掉右边的 /
url = f"{self.base_url}/{endpoint.lstrip('/')}"           # 去掉左边的 /
```

为什么要这么处理：配置里的 `API_BASE_URL` 可能写成 `https://api.example.com/`（带尾斜杠），调用时 endpoint 可能写成 `/users`（带前斜杠），直接拼就变成：

```text
https://api.example.com//users        ← 双斜杠
```

有些服务器会 404，有些会重定向，有些能容忍——**行为不可预测**，而且这种 bug 只在特定的配置组合下出现。

两边各 strip 一次，然后自己补一个 `/`，结果就稳定了：

| base_url | endpoint | 结果 |
|---|---|---|
| `https://x.com` | `users` | `https://x.com/users` |
| `https://x.com/` | `/users` | `https://x.com/users` |
| `https://x.com//` | `//users` | `https://x.com/users` |

> `rstrip("/")` 去掉的是**所有**尾部斜杠，不只一个。注意 `rstrip` 的参数是字符集合而不是字符串，`"abc".rstrip("cb")` 会得到 `"a"`——这个细节偶尔会坑人。

## 5. 统一设置认证

```python
self.session.headers.update({
    "Authorization": f"Bearer {api_key}",
    "Accept": "application/json",
})
```

设一次，之后所有通过这个 Session 发出的请求都自动带上。

- `Authorization: Bearer <token>` 是最常见的 API 认证格式（OAuth 2.0 规范），大模型 API 基本都用它
- `Accept: application/json` 告诉服务器「我要 JSON 格式的响应」

当时的理解题问得很准：**设置过之后每次 `session.post()` 还要重传 Authorization 吗？** 不需要——这正是 Session 的价值。

> 注意 `Content-Type` 不用手写。用 `json=` 参数时 requests 会自动设成 `application/json`（Day16 学过）。Day20 的代码里手动设了，属于冗余但无害。

## 6. 三层分层架构

```text
main.py          组织业务流程、处理最终异常、管理生命周期
   ↓
api_client.py    HTTP 请求、状态码检查、JSON 解析
   ↓
config.py        提供地址、密钥等配置
```

每个文件只负责一类事：

| 文件 | 职责 | 不该做什么 |
|---|---|---|
| `config.py` | 加载和校验配置 | 不发请求 |
| `api_client.py` | 发请求、解析响应 | **不决定出错后怎么办**、不读 `.env` |
| `main.py` | 组装、决定对策、清理资源 | 不关心 HTTP 细节 |

**分层的实际收益**：如果以后从 `requests` 换成 `httpx`（比如要支持 async），只需要改 `api_client.py`，`main.py` 和业务代码不用动。

这是 Day04「职责分离」和 Day16「异常分层」的综合体现——同一条原则在不同粒度上的应用：从函数级（返回结果 vs 打印）到模块级（谁发请求 vs 谁决定对策）。

## 7. `try / except / finally` 与资源清理

```python
try:
    api_client.post("getUser", data)
except JSONDecodeError:
    logging.exception("参数解析失败")
except RequestException:
    logging.exception("请求失败")
finally:
    api_client.close()        # ← 无论成功失败都会执行
```

`finally` 的语义是：**无论 `try` 块是正常结束、抛了异常、还是执行了 `return`，它都会执行。**

当时的理解题问：`post()` 抛异常时 `finally` 里的 `close()` 还会执行吗？**会。** 这正是 `finally` 的用途——资源清理不能依赖「程序走到了那一行」，因为异常会跳过中间的代码。

Session 持有 TCP 连接和线程池资源，不关闭会泄漏（短时间内不明显，长期运行的服务会累积）。

> 更地道的写法是让 `APIClient` 支持上下文管理器协议（实现 `__enter__` 和 `__exit__`），这样可以写成：
>
> ```python
> with APIClient(base_url, api_key) as client:
>     client.post("/users", data)
> # 退出 with 自动 close()
> ```
>
> 这就是 `with open(...)` 能自动关闭文件的同一个机制（Day11 学过用法，这里是学怎么实现）。
> 仓库 `README.md` 的待办里提到「自己写上下文管理器」，就是这件事。

## 8. `except Exception` 唯一合理的场景

Day12 讲过 `except Exception` 是坏做法——它会把程序自己的 bug 一起吞掉。但有一个例外：

```python
def main():
    try:
        ...
    except Exception:
        logging.exception("程序执行失败")     # 程序入口的最后一道边界
    finally:
        client.close()
```

**程序最外层入口**可以用它。理由是：到了这一层，异常再往上抛就是直接崩溃、打印一堆 traceback 给用户看。在这里统一捕获、记录完整日志、给用户一句友好提示，是合理的。

但两个前提：

1. **必须记录完整异常**（用 `logger.exception()`，不能只 `print("出错了")`），否则还是吞掉了
2. **只在最外层用一次**，内部各层仍然要捕获具体异常

> 区分的关键是「有没有人在你之后处理」。最外层没有下一层了，所以必须兜住；中间层上面还有人，就该把不认识的异常交出去。

---

# 第二部分 · 当天的练习

## 一、题目

实现 `APIClient` 类（含 `__init__` / `get` 或 `post` / `close`）、改写 `main.py` 用 `try/except/finally` 管理生命周期。

四道理解题的回答全部正确：

| 题目 | 答案 |
|---|---|
| `requests.Session()` 的主要作用 | 复用会话配置和连接 |
| `raise_for_status()` 遇到 HTTP 500 | 抛出 `HTTPError` |
| 为什么捕获异常后还要 `raise` | 让调用者知道失败并决定如何处理 |
| 为什么在 `finally` 中 `close()` | 无论成功失败都要释放 Session 资源 |

## 二、第一版：功能对了，但没完成架构练习

```python
# api_client.py
def post(url: str, data: dict) -> Any:
    try:
        response = requests.post(url, json=data, timeout=30)
        response.raise_for_status()
        return response.json()
    except JSONDecodeError:
        logger.exception("JSON解析错误")
        raise
    except requests.RequestException:
        logger.exception("请求失败")
        raise
```

**请求逻辑完全正确**，而且有一点特别值得肯定：

**`except JSONDecodeError` 写在 `except RequestException` 前面——顺序是对的。** 这正是 Day17 学到的教训，这次主动用上了。（`requests.exceptions.JSONDecodeError` 继承自标准库的 `json.JSONDecodeError`，所以用标准库这个类也能捕获它。）

但今天的练习目标是**架构升级**，这一版还是函数，没有 Session、没有状态复用。

### 另外三个问题

**一、`config = config.load_config()` 变量名覆盖了模块名。**

```python
from ... import config
config = config.load_config()      # 这行之后，config 不再是模块，而是字典
```

这次能跑（因为后面不再用模块），但属于隐患——如果后面还要 `config.其他函数()` 就会报 `AttributeError`，而且报错信息会很困惑（「字典没有这个属性」）。

改成名字不冲突：

```python
from ...config import load_config
settings = load_config()
```

**二、`Path(__file__).parent` 少了 `.resolve()`。** 没有 `resolve()` 时拿到的可能是相对路径，行为依赖启动目录（Day18 讲过）。

**三、第二次 `load_dotenv()` 漏了 `override=True`。** 这是 Day19 刚学的——不加的话环境专属配置被基础 `.env` 挡住，配置分层失效。

> 这三个问题有个共同点：**都是前几天学过的东西，在写新代码时漏掉了。** 换个场景（从函数换成项目结构）就容易丢掉已有的习惯。这类遗漏靠记忆防不住，要靠 checklist 或者 lint。

## 三、最终代码

**`api_client.py`：**

```python
import logging
from json import JSONDecodeError
from typing import Any

import requests

logger = logging.getLogger(__name__)


class APIClient:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
            "Accept": "application/json"
        })

    def post(self, endpoint: str, data: dict) -> Any:
        try:
            url = f"{self.base_url}/{endpoint.lstrip('/')}"
            response = self.session.post(url, json=data, timeout=10)
            response.raise_for_status()
            return response.json()
        except JSONDecodeError:
            logger.exception("JSON解析错误")
            raise
        except requests.RequestException:
            logger.exception("请求失败")
            raise

    def close(self) -> None:
        self.session.close()
```

**`main.py`：**

```python
import logging
from json import JSONDecodeError

from requests import RequestException

from dailypractice.Day20.api_client import APIClient
from dailypractice.Day20.config import load_config

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    data = {"name": "jack"}
    setting = load_config()
    api_client = APIClient(setting["api_base_url"], setting["api_key"])
    try:
        api_client.post("getUser", data)
    except JSONDecodeError:
        logging.exception("参数解析失败")
    except RequestException:
        logging.exception("请求失败")
    finally:
        api_client.close()
```

六处做对了：

- **Session 在 `__init__` 创建一次**，多次请求复用
- **Headers 统一设置**，认证信息不用每次传
- **两个 strip 处理 URL**，不会出现双斜杠
- **`except` 顺序正确**，JSON 解析异常不会被 `RequestException` 抢走
- **`logger.exception()` + `raise`**，底层记录、上层决策
- **`finally` 里 `close()`**，异常也不会泄漏资源

## 四、现在回头看

### 一、`post()` 的返回值没有接收

```python
api_client.post("getUser", data)        # 返回的数据被丢掉了
```

请求发出去了、响应解析了，但结果没人要。应该是：

```python
result = api_client.post("getUser", data)
print("响应：", result)
```

这个问题和 Day09 那个 `parse_guess(input_num)` 不接返回值是同一类——**函数算完了，调用方却没拿**。

### 二、`main.py` 曾经 `import post` 导致 ImportError

第二版里写了 `from ...api_client import post, APIClient`，但 `post` 已经变成类的方法了，模块级不存在这个名字——**实测 `ImportError`**。迁移到独立仓库时删掉了这行（仓库 `README.md` 的迁移记录里有）。

> 教训：**把函数改成方法时，所有导入它的地方都要跟着改。** 这类错误在导入时就会炸，算是「好的失败」——至少立刻就能发现。

### 三、`main.py` 用的是 `logging.exception()` 而不是模块 logger

```python
logging.exception("参数解析失败")       # 用的是 root logger
logger.exception("参数解析失败")        # 应该先建模块级 logger
```

`logging.exception()` 直接操作 root logger，日志里不会显示来源模块。`main.py` 里影响不大（它就是入口），但习惯上应该统一用 `logger = logging.getLogger(__name__)`。

### 四、`config.py` 相比 Day19 退了两步

| | Day19 | Day20 |
|---|---|---|
| 返回类型 | `dict[str, str \| bool]` | `dict`（没参数化） |
| 配置文件存在性检查 | 有 `env_file_path.exists()` | **没有** |
| DEBUG 配置 | 有 | 没有 |
| 默认环境 | `development` | `testing` |

**存在性检查丢了最可惜**——Day19 刚学会用它修正 `load_dotenv()` 的静默失败，Day20 又回到了「文件不存在也不报错」的状态。

另外默认环境改成了 `testing`。按 Day19 讨论的原则（默认值选「出错时损害最小」的），`development` 比 `testing` 更合适。

### 五、API Key 在 `main.py` 里曾被硬编码

第二版写的是 `APIClient(setting["api_base_url"], "ABCDEFG")`——第二个参数直接写了字符串。虽然是假值，但这正是 Day18 要避免的模式。最终版改成了 `setting["api_key"]`。

### 六、没有实现上下文管理器

见知识讲解第 7 节。实现 `__enter__` / `__exit__` 之后可以用 `with` 自动关闭，比手写 `finally` 更可靠——因为 `finally` 可能被忘记写，而 `with` 的清理是语法保证的。

## 五、复习自测

1. `requests.Session()` 复用了哪些东西？其中哪一项带来实际的性能收益？
2. 如果把 `requests.Session()` 写在 `post()` 方法里会怎样？
3. 什么情况下该把函数升级成类？判断标准是什么？
4. `base_url.rstrip("/")` 和 `endpoint.lstrip("/")` 分别解决什么问题？
5. Session 设置过 `Authorization` 后，每次 `session.post()` 还要传吗？
6. 三层架构里，`api_client.py` **不该**做什么？
7. `post()` 抛异常时，`finally` 里的 `close()` 会执行吗？
8. `except Exception` 在什么场景下是合理的？有什么前提？
9. `from json import JSONDecodeError` 能捕获 `requests` 的 JSON 解析异常吗？

<details>
<summary>参考答案</summary>

1. 复用 Headers、Cookie、TCP 连接池和其他配置。**连接池**带来实际性能收益——省掉了每次请求的 TCP 和 TLS 握手开销。
2. 每次调用都新建一个 Session，连接池和统一 Headers 都失去意义，退化成顶层 API 的效果，还多绕一层。
3. 当存在「需要在多次调用之间保持的状态」时。纯计算用函数；要保持连接、配置、认证或累积数据就用类。不要因为类看起来专业而用类。
4. `rstrip("/")` 去掉 base_url 末尾的斜杠，`lstrip("/")` 去掉 endpoint 开头的斜杠，然后自己补一个 `/`——避免拼出 `https://x.com//users` 这种双斜杠，它在不同服务器上行为不一致。
5. 不需要。Session 会保存默认 Headers 并应用到后续所有请求，这正是它的价值。
6. 不该决定「出错后怎么办」（那是调用方的职责），也不该自己读 `.env`（那是 `config.py` 的职责）。
7. 会。`finally` 无论 `try` 块正常结束、抛异常还是 `return`，都会执行——这正是用它清理资源的原因。
8. 只在**程序最外层入口**合理。前提是必须用 `logger.exception()` 记录完整异常（否则还是吞掉了），而且只在最外层用一次，内部各层仍要捕获具体异常。
9. 能。`requests.exceptions.JSONDecodeError` 继承自标准库的 `json.JSONDecodeError`，所以用父类可以捕获它。

</details>
