# Day 15 · HTTP 请求与 requests 异常体系

> **学习日** 2026-10-28（15:38 - 16:07，2 轮对话）
> **对应代码** [`dailypractice/Day15/day_15.py`](../../../dailypractice/Day15/day_15.py)
> **原始对话** `courseware/_raw/markdown/03_Python每日练习出题.md`（对话里称「Day 15」）

> A 线从这里开始离开本地，走向网络。后面 Day16-20 都在这条线上加码，最终做出 `APIClient` 类。

## 本节掌握

- API、HTTP、状态码、JSON 四个概念
- `requests.get()`、`raise_for_status()`、`response.json()` 三行关键代码
- `timeout` 的准确含义（**不是**整个请求的总时长上限）
- **requests 的异常继承体系**，以及它导致的一个静默 bug
- `status_code` 和 `raise_for_status()` 的区别
- HTTP 200 不代表正文是合法 JSON

---

# 第一部分 · 知识讲解

## 1. API 是什么

API 是两个程序之间约定好的沟通接口。

举例：程序要查天气，不必自己建气象站，只要按约定格式向天气服务**发请求**，服务**返回数据**。约定包括：请求发到哪个地址、带什么参数、返回什么格式。

对后面的学习来说，重点是：**调用大模型也是调 API**。GPT、Claude 的接口都是 HTTP API，今天学的东西直接用得上。

## 2. HTTP 的请求与响应

一次 HTTP 调用由两部分组成：

- **请求（Request）**：访问哪个资源、用什么方法、带什么数据
- **响应（Response）**：状态码、响应头、响应正文

```python
response = requests.get(url)

response.status_code    # 状态码，如 200
response.headers        # 响应头（字典）
response.text           # 正文的原始文本
response.json()         # 把正文按 JSON 解析
```

## 3. 状态码

| 状态码 | 含义 | 常见情况 |
|---|---|---|
| `200` | 成功 | 请求处理成功 |
| `201` | 已创建 | 成功创建了资源 |
| `400` | 请求错误 | 参数不合法 |
| `401` | 未授权 | 缺少或无效的身份凭证（API Key 不对） |
| `404` | 未找到 | 地址写错了，或资源不存在 |
| `500` | 服务器错误 | 服务端自己出问题了 |

记住三类的分工就够了：

- **2xx 成功**
- **4xx 客户端的问题**——是你请求写错了，重试没有意义，得改代码或改参数
- **5xx 服务器的问题**——不是你的错，重试**可能**有用

这个区分直接决定出错后该怎么办。

## 4. requests 的安装

`requests` 不是标准库，要装：

```bash
python -m pip install requests
```

> 用 `python -m pip` 而不是直接 `pip`，是为了确保装到**当前这个 Python 解释器**的环境里。机器上有多个 Python 版本或虚拟环境时，直接敲 `pip` 很容易装错地方——装完了却 `import` 不到，是新手最常见的困惑之一。

## 5. 三行关键代码

```python
response = requests.get(url, timeout=10)   # ① 发请求
response.raise_for_status()                # ② 检查状态码
data = response.json()                     # ③ 解析正文
```

**顺序不能换。** 先确认 HTTP 层面成功了，再去解析正文——因为 `response.json()` **完全不管状态码**。服务器返回 404 加一段 HTML 错误页时，`json()` 会尝试解析那段 HTML 然后抛异常，错误信息会指向「JSON 解析失败」，而真正的原因是「地址写错了」。

### `timeout` 的准确含义

```python
requests.get(url, timeout=10)
```

常见的误解是「整个请求最多 10 秒」。**实际不是这样**：`timeout` 控制的是**连接建立**和**两次数据接收之间**的等待上限。

所以一个持续缓慢传输的响应（每 9 秒发来一点数据）可以远远超过 10 秒也不触发超时。要严格限制总时长得用别的手段。

但**必须设 `timeout`**。requests 的默认值是**永不超时**，不设就意味着对方不响应时你的程序会一直挂着——没有报错、没有日志，就是卡住。这是真实服务里最难排查的故障之一。

> 需要分别控制时，`timeout` 可以传元组：`timeout=(3, 10)` 表示连接超时 3 秒、读取超时 10 秒。

### `status_code` 和 `raise_for_status()`

| 写法 | 行为 | 适合 |
|---|---|---|
| `if response.status_code == 200:` | 读到一个数字，自己判断 | 需要对不同状态码做不同处理 |
| `response.raise_for_status()` | 4xx/5xx 时抛 `HTTPError`，2xx 时什么都不做 | 「只要不成功就当失败处理」 |

区别在**通知方式**：前者返回数据让你判断，后者用异常机制强制你面对。后者的好处是不会忘——忘了检查 `status_code` 的代码会带着错误数据继续跑，而漏掉的异常会直接崩。

## 6. requests 的异常体系（本节重点）

这是今天最需要记住的部分。实测继承关系（requests 2.34.2）：

```text
HTTPError          HTTPError -> RequestException -> OSError -> Exception
Timeout            Timeout -> RequestException -> OSError -> Exception
ConnectionError    ConnectionError -> RequestException -> OSError -> Exception
JSONDecodeError    JSONDecodeError -> InvalidJSONError -> RequestException -> OSError
                                   -> json.JSONDecodeError -> ValueError -> Exception
```

层次结构：

```text
RequestException          ← 所有 requests 异常的基类
├── ConnectionError       ← 连不上（DNS 失败、拒绝连接、断网）
│   └── ConnectTimeout    ← 连接阶段超时
├── Timeout               ← 超时
│   ├── ConnectTimeout
│   └── ReadTimeout       ← 读取阶段超时
├── HTTPError             ← raise_for_status() 在 4xx/5xx 时抛出
└── InvalidJSONError
    └── JSONDecodeError   ← 正文不是合法 JSON（同时也是 ValueError）
```

两条实用结论：

**一、`except requests.exceptions.RequestException` 能兜住所有网络相关异常。** 想统一处理就捕获它。

**二、`JSONDecodeError` 同时是 `RequestException` 和 `ValueError` 的子类。** 这是个容易踩的设计——它既属于「请求相关异常」，又属于「值错误」。实测：

```python
issubclass(requests.exceptions.JSONDecodeError, requests.exceptions.RequestException)  # True
issubclass(requests.exceptions.JSONDecodeError, ValueError)                            # True
```

这个双重身份会造成一个静默 bug，见下面第二部分。

> 顺带一提：所有 requests 异常都继承自 `OSError`，所以 `except OSError` 也能捕获它们。这个设计是为了和标准库的网络异常保持一致。

## 7. `response.json()` 的边界

两件事它不管：

**一、不管状态码。** 见上面「顺序不能换」。

**二、不保证返回字典。** JSON 顶层可以是数组、字符串、数字、`null`，所以 `response.json()` 的返回值可能是 `list`、`str`、`int`、`None`。

因此给函数标 `-> dict` 是不严谨的，除非你确定那个接口只会返回对象。标 `-> Any` 更诚实（Day16 就是这么做的）。

---

# 第二部分 · 当天的练习

## 一、题目

写 `fetch_data(url)`：用 `requests.get()` 请求、设置 `timeout`、检查状态码、解析 JSON 并返回；处理请求异常和 JSON 解析异常，**不用 `except Exception`**。测试地址 `https://httpbin.org/json`。

另外回答三个问题：

1. 为什么要设置 `timeout`？
2. `response.status_code` 和 `response.raise_for_status()` 有什么区别？
3. 如果服务器返回 HTTP 200，但正文不是合法 JSON，会发生什么？

## 二、代码

```python
import requests
from requests import HTTPError      # ← 导入了但没用到

def fetch_data(url: str):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print("请求失败：", e)
        return None
    except ValueError as e:          # ← 这个分支永远不会执行
        print("响应数据无法解析：", e)
        return None
```

主流程是对的：设了超时、状态检查在解析之前、没用 `except Exception`。但有两个问题。

## 三、坑 1：导入了没用的东西

```python
from requests import HTTPError
```

代码里没有任何地方用到 `HTTPError`——捕获用的是 `requests.exceptions.RequestException`。

> 这一行至今还在 `day_15.py` 里，是仓库 `README.md` 提到的「`ruff check .` 的 14 个告警」之一。无用导入的危害不只是难看：它会让读代码的人以为这里会单独处理 `HTTPError`，产生误解。

## 四、坑 2：`except ValueError` 是死代码（当时没发现）

这是本节最值得记住的发现。**这个 bug 当时没被发现，连代码评审也判了「基本通过」。**

问题 3 的答案是：

> 问题 3：会打印：响应数据无法解析 结果为空

**实际不是这样。** 实测模拟「HTTP 200 + 正文是 HTML」：

```python
resp = requests.Response()
resp.status_code = 200
resp._content = b"<html>not json</html>"

try:
    resp.raise_for_status()
    data = resp.json()
except requests.exceptions.RequestException as e:
    print(f"走进了第一个分支「请求失败」: {type(e).__name__}")
except ValueError as e:
    print(f"走进了第二个分支「响应数据无法解析」: {type(e).__name__}")

# 输出：走进了第一个分支「请求失败」: JSONDecodeError
```

原因就是知识讲解第 6 节那个双重继承：`JSONDecodeError` **既是** `ValueError` **也是** `RequestException`。而 `except` 按书写顺序匹配，`RequestException` 写在前面，所以它先接住了 JSON 解析错误。

后果是：

- `except ValueError` 这四行是**死代码**，一次都不会执行
- JSON 解析失败时，用户看到的提示是「**请求失败**」——而请求其实完全成功了，是正文格式不对
- 排查时会被带向「网络/服务端问题」，而真正的原因是「响应格式不符合预期」

### 怎么修

**方法一：把具体的异常放前面。**

```python
except requests.exceptions.JSONDecodeError as e:    # 子类在前
    print("响应数据无法解析：", e)
    return None
except requests.exceptions.RequestException as e:   # 父类在后
    print("请求失败：", e)
    return None
```

**方法二：不用 `ValueError`，直接捕获明确的类型。** 如果要兼容老版本 requests（2.27 之前 `json()` 抛的是标准库的 `json.JSONDecodeError`），可以写成元组：

```python
except (requests.exceptions.JSONDecodeError, json.JSONDecodeError) as e:
```

> **通用规律：多个 `except` 分支时，具体的异常必须写在宽泛的异常前面。** 顺序错了，后面的分支会变成死代码，而 Python **不报错、不警告**。
>
> 这和 Day14 的发现是同一个问题的两次出现——那边是 `json.JSONDecodeError` 和 `ValueError`，这边是 `requests.exceptions.JSONDecodeError` 和 `RequestException`。**只要用到异常继承，就要确认捕获顺序。**

## 五、三个问题的回答与修正

**问题 1：为什么设 `timeout`？**

> 设置 timeout 是为了让程序达到一定时间后中断，免得一直卡死

方向对。补充两点：requests 默认**永不超时**，所以不设就真的会无限等；另外它限制的是连接和读取的等待时间，不是整个请求的总时长。

**问题 2：`status_code` 和 `raise_for_status()` 的区别？**

> 一个是获取状态，一个是抛出异常

对。更精确的说法是：前者返回一个数字交给你判断，后者在 4xx/5xx 时主动抛 `HTTPError`。区别在于通知方式——后者不会被忘记。

**问题 3：HTTP 200 但正文不是合法 JSON 会怎样？**

> 会打印：响应数据无法解析 结果为空

**这条是错的**，见上面第四节。实际会打印「请求失败」，因为走的是 `RequestException` 分支。返回 `None` 这部分是对的。

## 六、现在回头看

### 一、`print` + `return None` 丢掉了错误信息

```python
except requests.exceptions.RequestException as e:
    print("请求失败：", e)
    return None
```

调用方只拿到 `None`，无法区分是超时、404、断网还是 JSON 格式不对。这是 Day13 讨论过的「返回值语义歧义」在网络场景的重演——而且网络场景下**重试策略依赖于错误类型**（5xx 可以重试，4xx 重试没用），信息丢了就没法做正确决策。

Day16 会改成 `logger.exception()` + `raise`。

### 二、`fetch_data()` 没有返回类型标注

应该标上。但不要标 `-> dict`——JSON 顶层可能是数组。标 `-> Any` 更诚实。

### 三、`main()` 里把返回值命名为 `response`

```python
response = fetch_data(url)
```

`fetch_data()` 返回的是**解析后的数据**，不是 `Response` 对象。叫 `response` 会让人以为能接着调 `.status_code`。叫 `data` 或 `result` 更准确。

## 七、复习自测

1. 4xx 和 5xx 分别代表什么？哪一类重试可能有用？
2. 为什么 `raise_for_status()` 要写在 `response.json()` 之前？
3. `timeout=10` 是「整个请求不超过 10 秒」吗？不设 `timeout` 会怎样？
4. `requests.exceptions.RequestException` 能捕获 `HTTPError` 和 `Timeout` 吗？
5. `requests.exceptions.JSONDecodeError` 继承自哪两个重要基类？
6. 下面这段代码，HTTP 200 但正文是 HTML 时会打印哪一句？

   ```python
   except requests.exceptions.RequestException as e:
       print("请求失败：", e)
   except ValueError as e:
       print("响应数据无法解析：", e)
   ```
7. 多个 `except` 分支的书写顺序有什么规则？写错了 Python 会提示吗？
8. 为什么 `fetch_data()` 不该标 `-> dict`？

<details>
<summary>参考答案</summary>

1. 4xx 是客户端问题（请求写错了），重试没有意义，必须改代码或参数；5xx 是服务器问题，重试**可能**有用。
2. 因为 `response.json()` 完全不检查状态码。返回 404 加 HTML 错误页时，`json()` 会解析失败并抛异常，错误信息指向「JSON 解析失败」，掩盖了真正的原因「地址写错了」。
3. 不是。它限制的是连接建立和两次数据接收之间的等待上限，一个持续缓慢的响应可以远超 10 秒。不设 `timeout` 时 requests **永不超时**，对方不响应程序就会一直挂着，没有报错也没有日志。
4. 能。它是所有 requests 异常的基类，`HTTPError`、`Timeout`、`ConnectionError`、`JSONDecodeError` 都继承自它。
5. 同时继承 `RequestException`（通过 `InvalidJSONError`）和 `ValueError`（通过 `json.JSONDecodeError`）。
6. 打印「**请求失败**」。因为 `JSONDecodeError` 也是 `RequestException` 的子类，而它写在前面先匹配上了。`except ValueError` 是死代码。
7. 具体的异常必须写在宽泛的异常之前，否则后面的分支永远不会执行。Python **不报错也不警告**，这是个静默的逻辑错误。
8. 因为 JSON 顶层可以是数组、字符串、数字或 `null`，`response.json()` 的返回值不保证是字典。标 `-> Any` 更诚实。

</details>
