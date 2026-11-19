---
kind: lesson
outline: [2, 2]
time: 45 分钟
uses: [params, dict | None = None, logger.exception, 记录后 raise, except 的顺序]
record:
  - text: 当时的代码 Day16/day_16.py
    link: https://github.com/syjlpineapple/ai-learning/blob/main/dailypractice/Day16/day_16.py
---

# Day 16：请求参数与异常分层

昨天的 `fetch_data()` 出错时 `print` 一句、返回 `None`。调用方拿到 `None`，不知道是超时、404 还是格式不对。

今天做两件事：一是请求时带上参数；二是想清楚，出了错到底该谁来处理。

## 一、`params=`：查询参数交给 requests

地址后面 `?` 跟着的 `q=...&limit=3` 叫查询参数。把它们写成字典交给 `params=`：

```python
r = requests.get(base + "/echo", params={"q": "python 教程", "limit": 3, "tag": "A&B"}, timeout=10)
print(r.url)
print(r.json()["query"])
```

```text
http://127.0.0.1:63973/echo?q=python+%E6%95%99%E7%A8%8B&limit=3&tag=A%26B
{'q': ['python 教程'], 'limit': ['3'], 'tag': ['A&B']}
```

（`/echo` 是本机服务里的一个接口，它把收到的东西原样告诉你。起服务的方法见 Day 15 开头。）

requests 把空格、中文、`&` 都做了编码。如果自己拼地址：

```python
r = requests.get(base + "/echo?q=python 教程&limit=3&tag=A&B", timeout=10)
print(r.json()["query"])
```

```text
{'q': ['python 教程'], 'limit': ['3'], 'tag': ['A'], 'B': ['']}
```

`A&B` 里的 `&` 被当成了参数分隔符，`tag` 变成了 `A`，还凭空多出一个参数 `B`。所以**不要自己拼查询字符串**，交给 `params=`。

顺带认识两个以后天天用的东西：GET 用来查，参数放地址里（`params=`）；POST 用来提交，数据放请求体里（`json=` 或 `data=`，明天细讲）。请求头 `headers` 里常放 `Authorization`，也就是 API Key，Day 18 专门讲它怎么保管。

## 二、`params: dict | None = None` 是什么意思

```python
def fetch_data(url: str, params: dict | None = None) -> Any:
```

拆开读：

| 写法 | 意思 |
|---|---|
| `params: dict` | 这个参数应该是字典 |
| `params: dict \| None` | 可以是字典，**也可以是 `None`** |
| `params: dict \| None = None` | 再加上默认值：不传就是 `None` |

这里的 `|` 在类型标注里，意思是「或者是这个类型」，和 Day 14 表达式里的按位或不是一回事。同一个符号，位置不同，意思不同。

`-> Any`（从 `typing` 导入）表示「返回什么都可能」。`response.json()` 可能是字典、列表、字符串、数字，标 `-> dict` 就是在撒谎。

## 三、出了错，谁来管

`fetch_data()` 只知道「请求超时了」，它不知道这次调用是谁发起的：用户点了按钮，该弹个提示；后台定时任务，该过会儿重试；批量导入，该跳过这条继续。**只有调用方知道该怎么办。**

所以底层函数的职责是：把技术细节记下来，然后把异常原样交出去。

```python
except requests.exceptions.RequestException:
    logger.exception("HTTP 请求失败，URL: %s", url)
    raise
```

`logger.exception()` 只能写在 `except` 里，它除了记你这句话，还会自动把完整的 traceback 记下来。后面的裸 `raise`（Day 14 学过）把异常原样抛给调用方。

三种做法对比：

| 方案 | 做法 | 问题 |
|---|---|---|
| A | 接住、记日志、返回 `None` | 调用方不知道为什么失败 |
| B | 不接，让异常直接上抛 | 日志里没有「是哪个 URL」这种上下文 |
| C | 接住、记日志、`raise` | 两头都照顾到 |

但不是什么都该 `raise`。Day 14 的「文件不存在返回 `[]`」就不用：那个函数知道该怎么办。判断标准只有一句：**这个函数知道怎么处理吗？** 知道就处理掉，不知道就交出去。

还有一条：同一个异常不要每一层都 `logger.exception()` 一遍，否则一个错误在日志里出现三次，看着像出了三次故障。

## 四、`except` 的顺序又出事了

下面是当天的「优化版」`fetch_data`（也就是 `day_16.py`）：

```python
    except requests.exceptions.RequestException:
        logger.exception("HTTP 请求失败，URL: %s", url)
        raise

    except ValueError:
        logger.exception("JSON 数据解析失败，URL: %s", url)
        raise
```

拿它去请求 `/html`（200，正文是 HTML），日志是这样的：

```text
ERROR - dailypractice.Day16.day_16 - HTTP 请求失败，URL: http://127.0.0.1:63973/html
Traceback (most recent call last):
  ……（中间的 traceback 这里省略）
requests.exceptions.JSONDecodeError: Expecting value: line 1 column 1 (char 0)
网络请求失败： Expecting value: line 1 column 1 (char 0)
```

明明是格式不对，日志却记成「HTTP 请求失败」，`main()` 也提示「网络请求失败」。原因和昨天一样：`requests.exceptions.JSONDecodeError` 同时是 `RequestException` 和 `ValueError`，写在前面的 `RequestException` 先接住了。两处 `except ValueError` 都是死代码。

这次后果比昨天更重：**日志是排查线上问题的主要依据**，它记错了，人就会去查网络、查服务器，而真正的原因是对方回了个 HTML 页面。

把具体的提到前面（`main()` 里也一样）：

```python
    except requests.exceptions.JSONDecodeError:
        logger.exception("JSON 数据解析失败，URL: %s", url)
        raise
    except requests.exceptions.RequestException:
        logger.exception("HTTP 请求失败，URL: %s", url)
        raise
```

再跑一次：

```text
ERROR - day16_fixed - JSON 数据解析失败，URL: http://127.0.0.1:52639/html
Traceback (most recent call last):
  ……（省略）
requests.exceptions.JSONDecodeError: Expecting value: line 1 column 1 (char 0)
返回数据格式错误： Expecting value: line 1 column 1 (char 0)
```

每写完一组 `except`，问一句：**后面这条，会不会被前面的抢先接走？**

## 五、今天的作业

写 `fetch_data(url, params=None)`：

1. `requests.get()` 支持查询参数，`timeout=10`
2. `raise_for_status()` 检查状态码，`response.json()` 解析并返回
3. 处理请求异常和 JSON 解析异常，不用 `except Exception`
4. `main()` 里请求 `https://httpbin.org/get`，传 `q=python`、`limit=3`

回答：`params=` 和 `json=` 有什么区别？为什么不自己拼查询字符串？返回 404 时 `raise_for_status()` 做什么？

## 六、小测

**1.** `def f(params: dict | None = None)`，哪些调用是合法的？

- A. 只有 `f({"q": 1})`
- B. `f()` 和 `f({"q": 1})`
- C. `f()`、`f(None)`、`f({"q": 1})` 都合法

**2.** 网络超时了，底层的 `fetch_data()` 最合适的做法是？

- A. 记日志，返回 `None`
- B. 记日志，然后 `raise`
- C. 自己弹个提示框告诉用户

**3.** `logger.exception()` 比 `logger.error()` 多记了什么？

- A. 时间
- B. 完整的 traceback
- C. 什么都没多

<details>
<summary>答案</summary>

1. C。`| None` 允许传 `None`，`= None` 允许不传。
2. B。底层不知道该怎么处理，记下细节交给调用方。
3. B。所以它只能在 `except` 里用，外面没有「当前异常」。

</details>

## 讲评（11-03）

你第一版的 `fetch_data` 已经用上了 `logging`，这是好的开始。但有三个问题：`requests.get()` 和 `raise_for_status()` 放在 `try` 外面，超时、连不上、404 全都没人管；`logger.error("JSON Decode Error")` 没说是哪个 URL；`return None` 写在 `try` 外面，能跑，但读的人要想一下才明白它只在出错时执行。

接着你说「给我下优化后的代码我学习下」，然后围绕这份代码追问了一串问题，每个都问在要害上：

- `| None = None` 是什么意思
- `-> Any` 是不是返回任意类型
- `raise_for_status()` 抛什么异常，会不会被后面接住
- Python 是不是一般都 `logger.exception` 然后 `raise`
- 字典和 JSON 是不是没区别

最后一个的答案是：很像，但不是一回事。字典是内存里的 Python 对象，JSON 是一段文本。JSON 的字符串必须用双引号，键只能是字符串，布尔值写作 `true`。`response.json()` 做的就是把这段文本变成 Python 对象。

需要说清楚的是，第四节那个死代码出在 GPT 给的这份「优化版」里，当天谁都没发现，`main()` 里的 `except ValueError` 也一样永远执行不到。你学的「`logger.exception()` + `raise`」这个模式本身没错，错的只是顺序。

## 加练

[失败了就重试](加练/day16_失败了就重试.md)：失败了等一会儿再试、等的时间越来越长、试够次数就把最后那个异常原样交给调用方。练的正是今天「底层记录、`raise`，上层决定对策」里的「上层」。
