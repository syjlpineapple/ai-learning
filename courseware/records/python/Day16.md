# Day 16 · 请求参数、类型标注与异常分层

> **学习日** 2026-10-29 出题 / 2026-11-03 交作业（7 轮追问）
> **对应代码** [`dailypractice/Day16/day_16.py`](../../../dailypractice/Day16/day_16.py)
> **原始对话** `courseware/_raw/markdown/03_Python每日练习出题.md`（对话里称「Day 16」）

> 这一节是 A 线异常处理的分水岭：从 `print` + `return None` 转向 `logger.exception()` + `raise`。

## 本节掌握

- GET 与 POST；`params=` / `json=` / `data=` 三者的区别
- `headers` 的作用：`Content-Type` 和 `Authorization`
- `dict | None = None` 的三层含义；**`|` 在类型标注里不是按位或**
- `-> Any` 和 `-> object` 的区别
- `logger.exception()` 比 `logger.error()` 多了什么
- **异常处理的分层职责**，以及 `logger.exception()` + `raise` 模式
- 为什么不该在每一层都记录异常
- 字典和 JSON 到底是不是一回事

---

# 第一部分 · 知识讲解

## 1. GET 与 POST

| | GET | POST |
|---|---|---|
| 用途 | 获取数据 | 提交数据 |
| 例子 | 查天气、搜商品 | 创建订单、**给大模型发消息** |
| 参数位置 | URL 查询字符串 | 请求体 |
| requests 参数 | `params=` | `json=` 或 `data=` |

GET 和 POST 的区别不只是「读」和「写」——具体语义由 API 设计者决定。惯例是 GET 用于安全、可重复的读取（多调用几次没有副作用），POST 用于提交数据或触发处理。

调用大模型 API 几乎都是 POST，因为要把对话内容放进请求体。

## 2. `params=`：查询参数

```python
params = {"q": "python", "limit": 3}
response = requests.get(url, params=params, timeout=10)
```

requests 会自动把字典编码成 URL 查询字符串：

```text
https://httpbin.org/get?q=python&limit=3
```

**不要自己拼接 URL。** 原因是参数值里可能有空格、中文、`&`、`=`、`#` 这些字符，必须做 URL 编码（百分号编码）。手动拼接要么漏掉编码导致请求出错，要么编码错导致参数被截断。`params=` 把这件事完整处理掉了。

## 3. `json=` 与 `data=`：两种请求体

```python
requests.post(url, json=payload)    # JSON 请求体
requests.post(url, data=payload)    # 表单编码
```

| 参数 | 编码方式 | `Content-Type` |
|---|---|---|
| `json=` | 序列化成 JSON | 自动设为 `application/json` |
| `data=`（传字典） | 表单编码 `a=1&b=2` | 自动设为 `application/x-www-form-urlencoded` |
| `data=`（传字符串） | 原样发送 | 不自动设置 |

**传错会导致服务器解析失败**，而且报错信息通常很难懂（服务端会说「参数缺失」而不是「格式不对」）。判断依据只有一个：看 API 文档要求哪种。大模型 API 一律用 `json=`。

`json=` 的另一个好处是**自动设置 `Content-Type`**，不用手写。

## 4. `headers`：请求头

```python
headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer YOUR_API_KEY",
}
```

- `Content-Type`：告诉服务器请求体是什么格式
- `Authorization`：身份凭证，调用任何需要付费或鉴权的 API 都要带

用 `json=` 时不必手写 `Content-Type`（requests 会设），但 `Authorization` 必须自己带。

> API Key 绝不能写进代码。Day 18-19 专门学怎么用环境变量和 `.env` 文件管理它。

## 5. `dict | None = None` 的三层含义

这是当时专门追问的一个点，拆成三层看：

```python
def fetch_data(url: str, params: dict | None = None) -> Any:
```

| 写法 | 含义 |
|---|---|
| `params: dict` | 这个参数预期是字典 |
| `params: dict \| None` | 可以是字典，**也可以是 `None`** |
| `params: dict \| None = None` | 可以是字典或 None，**默认值是 None** |

所以三种调用方式都合法：

```python
fetch_data(url, {"q": "Python"})   # 传字典
fetch_data(url, None)              # 显式传 None
fetch_data(url)                    # 不传，params 自动取 None
```

### `|` 在这里不是按位或

**这一点非常重要，而且正好和 Day14 的 bug 对照。**

```python
if 100 < item | item < 1:          # Day14：这里的 | 是按位或运算符
def f(params: dict | None = None): # Day16：这里的 | 是类型联合
```

同一个符号在两个位置含义完全不同：在**表达式**里是按位或，在**类型标注**里是类型联合（union）。Python 3.10 开始支持这种写法。

更早的版本要用 `typing.Optional`：

```python
from typing import Optional
params: Optional[dict] = None      # 等价于 dict | None = None
```

两者表达同一个意思，`dict | None` 是现代写法。

> 顺带提醒：`Optional[dict]` 的名字容易误解——它的意思是「可以是 None」，**不是**「这个参数可以省略」。参数能不能省略由有没有默认值决定。

## 6. `-> Any`

```python
from typing import Any

def fetch_data(url: str) -> Any:
    return response.json()
```

用 `Any` 是因为 `response.json()` 的返回类型真的不确定：`dict`、`list`、`str`、`int`、`float`、`bool`、`None` 都可能。标 `-> dict` 是在撒谎（Day15 讨论过）。

### `Any` 和 `object` 的区别

两者都表示「任意类型」，但对**类型检查器**的含义相反：

```python
def f(data: Any):
    print(data["name"])       # 类型检查器放行

def g(data: object):
    print(data["name"])       # 类型检查器报错
```

- `Any`：**放弃检查**。检查器不再对这个值的任何操作提意见。
- `object`：**最严格的类型**。所有类型都是它的子类，所以它只支持所有对象都有的操作（比如 `str()`），用下标、调方法之前必须先收窄类型。

所以 `Any` 是「我知道我在干什么，别管我」，`object` 是「我确实不知道这是什么，请强制我检查」。

> 注意：类型标注不做运行时检查（Day12 的教训）。`-> Any` 只影响静态检查工具的行为。

## 7. `logger.exception()` 与 `logger.error()`

```python
except requests.exceptions.RequestException:
    logger.error("请求失败")        # 只记消息
    logger.exception("请求失败")    # 消息 + 完整的异常堆栈
```

`logger.exception()` 会自动把当前异常的 traceback 一起写进日志。**它只能在 `except` 块里用**（外面没有「当前异常」）。

差别在排查效率上：`logger.error("请求失败")` 看到了也不知道哪一行出的问题、什么原因；`logger.exception()` 会告诉你完整的调用栈和异常类型。

> 等价写法是 `logger.error("请求失败", exc_info=True)`，`exception()` 是它的快捷方式。

## 8. 异常处理的分层职责

这是本节最重要的概念。

| 层级 | 职责 |
|---|---|
| API 客户端（`fetch_data`） | 发请求、解析数据 |
| 异常处理层 | 记录错误、**传播**异常 |
| 应用入口（`main`） | 决定提示用户、重试还是终止 |
| 日志配置 | 由入口统一控制 |

关键认识：**底层函数不知道该怎么处理错误。**

`fetch_data()` 只知道「请求超时了」，它不知道这次调用是用户点按钮触发的（该弹提示）、还是后台定时任务（该重试）、还是批量导入的一部分（该跳过继续）。**只有调用方知道上下文，所以只有调用方能决定怎么办。**

这正是 Day04 那个 A/B 设计题的升级版：当时是「函数该不该自己 print」，现在是「函数该不该自己决定如何处理错误」，答案一致——交给调用方。

## 9. `logger.exception()` + `raise` 模式

```python
def fetch_data(url, params=None):
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException:
        logger.exception("HTTP 请求失败，URL: %s", url)
        raise                                    # ← 记录后原样抛出
```

执行流程：底层**记录诊断信息**（它最清楚技术细节：哪个 URL、什么异常），然后把异常**原样抛给上层**，由上层**决定对策**。

这就是当时讨论的三个方案里的 C：

| 方案 | 做法 | 问题 |
|---|---|---|
| A | 捕获、记日志、返回 `None` | 调用方拿到 `None`，不知道为什么失败 |
| B | 不捕获，直接让异常上抛 | 日志里缺少底层的上下文（哪个 URL） |
| **C** | 捕获、记日志、`raise` 重抛 | 兼顾两者 |

注意必须用**裸 `raise`**，不要 `raise e`——裸 `raise` 保留原始的异常类型和完整 traceback（Day14 学过）。

### 什么情况不该 raise

**当前函数有能力合理处理时就不要抛。**

```python
except FileNotFoundError:
    logger.warning("历史记录文件不存在")
    return []                  # 首次运行是正常的，函数有明确对策
```

判断标准是一句话：**这个函数知道该怎么办吗？** 知道就处理掉，不知道就往上抛。

| 场景 | 做法 |
|---|---|
| 当前函数无法处理 | 记录（视情况）并 `raise` |
| 当前函数能合理恢复 | 处理掉，返回结果 |
| 可预期的非错误情况 | 按业务规则处理，不必记 ERROR |
| 程序最外层入口 | 记录完整异常并给用户反馈 |

### 不要每一层都记录

```python
# 底层
except RequestException:
    logger.exception("请求失败")
    raise
# 中层
except RequestException:
    logger.exception("处理数据失败")      # ← 同一个异常记第二遍
    raise
# 入口
except RequestException:
    logger.exception("操作失败")          # ← 第三遍
```

一个错误在日志里出现三遍，而且三条的 traceback 几乎一样。排查时很干扰，还会让人误以为发生了三次故障。

**通常只在一个边界记录完整堆栈**：要么底层记一次（它知道技术细节）、上层只处理不再记；要么底层只抛、入口统一记录。选一种并保持一致。

## 10. 字典和 JSON 不是一回事

当时的疑问：「python 中字典和 json 是不是基本没区别」。

**很像，但不是一回事：**

- **Python 字典**：Python 内存里的一种**数据结构**
- **JSON**：一种与语言无关的**文本格式**，用于交换数据

| 内容 | Python 字典 | JSON |
|---|---|---|
| 布尔值 | `True` / `False` | `true` / `false` |
| 空值 | `None` | `null` |
| 字符串引号 | 单引号或双引号都行 | **必须双引号** |
| 键的类型 | 任何可哈希对象（含整数、元组） | **必须是字符串** |
| 注释 | 可以写 | 标准 JSON 不支持 |
| 存在形式 | 内存中的对象 | 文本 |

转换靠 `json` 模块的四个方法（Day11 学过，带 `s` 的处理字符串）：

| 方法 | 方向 |
|---|---|
| `json.dumps()` | Python 对象 → JSON **字符串** |
| `json.loads()` | JSON **字符串** → Python 对象 |
| `json.dump()` | Python 对象 → **文件** |
| `json.load()` | **文件** → Python 对象 |

`response.json()` 做的就是 `json.loads(response.text)` 这件事。

---

# 第二部分 · 当天的练习

## 一、题目

写 `fetch_data(url, params=None)`：支持查询参数、设 `timeout=10`、检查状态码、解析 JSON；处理请求异常和 JSON 解析异常，不用 `except Exception`。在 `main()` 里请求 `https://httpbin.org/get`，传 `q=python` 和 `limit=3`。

## 二、第一版：漏了请求异常

```python
def fetch_data(url: str, params=None):
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()           # ← 这两行都可能抛异常，没人管
    try:
        data = response.json()
        return data
    except JSONDecodeError:
        logger.error("JSON Decode Error")  # ← 没记具体原因
    return None
```

三个问题：

**一、`requests.get()` 和 `raise_for_status()` 的异常完全没处理。** 这两行可能抛 `Timeout`、`ConnectionError`、`HTTPError`，全部会直接穿透出去。

**二、日志没带上下文。** `logger.error("JSON Decode Error")` 既没说是哪个 URL，也没带异常详情。改成 `logger.exception("JSON 解析失败：%s", url)` 才有诊断价值。

**三、`return None` 在 `try` 外面。** 解析成功时 `return data` 已经返回了，所以这行只在异常时执行——能跑，但控制流不直观，放进 `except` 块里更清楚。

## 三、优化版：方案 C

```python
import logging
from typing import Any

import requests

logger = logging.getLogger(__name__)


def fetch_data(url: str, params: dict | None = None) -> Any:
    """
    发送 GET 请求并返回 JSON 数据。

    Args:
        url: API 地址
        params: URL 查询参数

    Returns:
        API 返回的 JSON 数据

    Raises:
        requests.exceptions.RequestException: 请求失败
        ValueError: JSON 解析失败
    """
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException:
        logger.exception("HTTP 请求失败，URL: %s", url)
        raise

    except ValueError:
        logger.exception("JSON 数据解析失败，URL: %s", url)
        raise


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
    )
    try:
        data = fetch_data("https://httpbin.org/get", {"q": "Python", "limit": 3})
        print("请求结果：", data)
    except requests.exceptions.Timeout:
        print("请求超时，请稍后重试")
    except requests.exceptions.HTTPError as e:
        print("HTTP 状态错误：", e)
    except requests.exceptions.RequestException as e:
        print("网络请求失败：", e)
    except ValueError as e:
        print("返回数据格式错误：", e)
```

这一版的四个进步：

- **`logger.exception()` + `raise`**：底层记录技术细节，上层决定对策
- **完整的 docstring**：`Args` / `Returns` / **`Raises`**——把「这个函数会抛什么异常」写进文档，调用方才知道该捕获什么
- **`logging.basicConfig()` 在 `main()` 里**，带 `format`（Day13 的原则：模块记录、入口配置）
- **`main()` 分层捕获**：`Timeout` 和 `HTTPError` 单独处理，`RequestException` 兜底

> `format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"` 四个字段分别是时间、级别、logger 名（也就是模块路径）、消息。生产环境通常还会加 `%(filename)s:%(lineno)d` 定位到行。

## 四、现在回头看：`except` 顺序的问题还在

**这一版的两处 `except ValueError` 仍然是死代码**，原因和 Day15 完全一样——`requests.exceptions.JSONDecodeError` 同时继承 `RequestException` 和 `ValueError`，而 `RequestException` 写在前面。

**在 `fetch_data()` 里：**

```python
except requests.exceptions.RequestException:
    logger.exception("HTTP 请求失败，URL: %s", url)     # ← JSON 解析失败也会记成这条
    raise
except ValueError:
    logger.exception("JSON 数据解析失败，URL: %s", url)  # ← 永远不执行
    raise
```

后果比 Day15 更糟：**日志会把「响应格式不对」记成「HTTP 请求失败」**。而日志是排查生产问题的唯一依据，记错了会直接把人带到错误的方向——去查网络、查服务端，而真正的原因是对方返回了一个 HTML 错误页。

**在 `main()` 里：**

前三个分支顺序是对的（`Timeout`、`HTTPError` 具体在前，`RequestException` 兜底在后），但最后那个 `except ValueError` 同样不会执行，所以「返回数据格式错误」这句提示永远不会出现——用户看到的是「网络请求失败」。

### 修法

把 JSON 解析异常提到 `RequestException` **之前**：

```python
    except requests.exceptions.JSONDecodeError:
        logger.exception("JSON 数据解析失败，URL: %s", url)
        raise
    except requests.exceptions.RequestException:
        logger.exception("HTTP 请求失败，URL: %s", url)
        raise
```

> **这是同一个坑在 A 线的第三次出现**（Day14 的 `json.JSONDecodeError` vs `ValueError`、Day15、Day16）。
> 而且这次它出现在「优化版参考代码」里——说明**异常继承的捕获顺序是个容易被所有人忽略的盲区**。
>
> 可操作的检查方法：每写完一组 `except`，问一句「后面这些分支，有没有可能被前面的分支抢先捕获？」只要涉及继承关系就得查一下 `__mro__`。

### 另外两处小问题

**一、docstring 里的 `Raises` 写的是 `ValueError`。** 更精确的是 `requests.exceptions.JSONDecodeError`。文档写宽了，调用方可能写出同样顺序错误的 `except`。

**二、`main()` 里 `logging.basicConfig()` 之后才 `try`。** 这是对的——配置必须在任何日志产生之前完成。但如果 `fetch_data` 在模块导入阶段就被调用，日志仍会丢失。

## 五、复习自测

1. `params=`、`json=`、`data=` 三者分别怎么编码请求？
2. 为什么不该自己拼接 URL 查询字符串？
3. `params: dict | None = None` 的三层含义分别是什么？
4. `|` 在 `100 < item | item < 1` 和 `dict | None` 里分别是什么含义？
5. `Any` 和 `object` 作为类型标注有什么区别？
6. `logger.exception()` 比 `logger.error()` 多记了什么？它能在 `except` 块外面用吗？
7. 为什么底层函数不该自己决定如何处理错误？
8. `logger.exception()` + `raise` 这个模式解决了方案 A 和方案 B 各自的什么问题？
9. 为什么不该在每一层都 `logger.exception()`？
10. Python 字典和 JSON 有哪几处具体差异？
11. 下面这段代码，响应正文不是合法 JSON 时，日志会记成哪一条？

    ```python
    except requests.exceptions.RequestException:
        logger.exception("HTTP 请求失败")
        raise
    except ValueError:
        logger.exception("JSON 数据解析失败")
        raise
    ```

<details>
<summary>参考答案</summary>

1. `params=` 编码成 URL 查询字符串；`json=` 序列化成 JSON 请求体并自动设 `Content-Type: application/json`；`data=` 传字典时按表单编码（`application/x-www-form-urlencoded`），传字符串时原样发送。
2. 参数值可能含空格、中文、`&`、`=` 等字符，必须做 URL 编码。手动拼接容易漏掉编码或编码错误，导致参数被截断或请求失败。
3. `dict` 是预期类型；`| None` 表示也允许传 `None`；`= None` 表示有默认值，调用时可以不传这个参数。
4. 表达式里是**按位或**运算符（优先级高于比较运算符，Day14 的 bug 根源）；类型标注里是**类型联合**，等价于 `Optional[dict]`。
5. `Any` 是放弃检查，检查器不再对该值的任何操作提意见；`object` 是最严格的类型，只允许所有对象共有的操作，用下标或调方法前必须先收窄类型。
6. 多记了完整的异常 traceback。**不能**在 `except` 块外面用——外面没有「当前异常」可记。
7. 因为它不知道调用上下文。同一个超时，在用户点击场景下该弹提示、在后台任务里该重试、在批量处理中该跳过——只有调用方知道该怎么办。
8. 方案 A 的问题是调用方拿到 `None` 不知道原因；方案 B 的问题是日志缺少底层上下文（哪个 URL）。方案 C 让底层记录技术细节、上层决定对策，两者都解决了。
9. 同一个异常会在日志里重复出现多次，traceback 几乎一样，干扰排查，还会让人误以为发生了多次故障。应该只在一个边界记录完整堆栈。
10. 布尔值（`True` vs `true`）、空值（`None` vs `null`）、字符串必须用双引号、键必须是字符串、不支持注释；本质区别是字典是内存中的数据结构，JSON 是文本格式。
11. 记成「**HTTP 请求失败**」。因为 `requests.exceptions.JSONDecodeError` 也是 `RequestException` 的子类，写在前面的分支先匹配上了，`except ValueError` 是死代码。

</details>
