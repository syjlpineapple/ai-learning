# Day 17 · POST 请求与异常捕获顺序的修正

> **学习日** 2026-11-03 出题 / 2026-11-04 交作业（4 版迭代）
> **对应代码** 无——`dailypractice/Day17/` 下只有 `__init__.py`，这一天的代码没有存成文件
> **原始对话** `courseware/_raw/markdown/03_Python每日练习出题.md`（对话里称「第 17 天」）

> **这一节是 A 线异常处理的修正点。** `except` 顺序的坑在 Day14、Day15、Day16 连续踩了三次，
> Day17 终于被正面指出并改对。课件里给出了完整的最终代码，因为没有文件可对照。

## 本节掌握

- `requests.post()` 与 `json=` 的配合
- **`ValueError` 必须放在 `RequestException` 之前**，以及为什么
- `logger.exception("描述")` 而不是 `logger.exception(e)`
- 裸 `raise` 而不是 `raise e`
- `logger.setLevel()` 和 `logging.basicConfig()` 不是一回事
- 异常粒度的权衡：什么时候该分别捕获，什么时候该合并

---

# 第一部分 · 知识讲解

## 1. POST 与 `json=`

```python
response = requests.post(
    "https://httpbin.org/post",
    json={"name": "Tom", "age": 25},
    timeout=10,
)
```

`json=` 做两件事：把字典序列化成 JSON、自动设置 `Content-Type: application/json`。

和 `data=` 的区别在 Day16 讲过：`data=` 传字典时按表单编码。记忆方式是 **`json=` 发 JSON，`data=` 发表单**。

调用大模型 API 时固定用 `json=`，因为对话内容必须作为 JSON 请求体提交。

## 2. 核心修正：`ValueError` 要放在最前面

这是本节最重要的一条，它纠正了前面三节的错误。

```python
try:
    response = requests.post(url, json=user, timeout=10)
    response.raise_for_status()
    return response.json()

except ValueError:                               # ① JSON 解析失败
    logger.exception("服务器响应 JSON 解析失败")
    raise

except requests.exceptions.Timeout:              # ② 超时
    logger.exception("请求超时")
    raise

except requests.exceptions.ConnectionError:      # ③ 连不上
    logger.exception("连接失败")
    raise

except requests.exceptions.RequestException:     # ④ 其他请求异常兜底
    logger.exception("请求异常")
    raise
```

**为什么 `ValueError` 必须在最前面：**

`requests.exceptions.JSONDecodeError` 同时继承 `ValueError` 和 `RequestException`（Day15 实测过的继承链）。`except` 按书写顺序匹配，所以：

- `ValueError` 在前 → JSON 解析失败走 ① ✅
- `RequestException` 在前 → JSON 解析失败走 ④，日志记成「请求异常」❌

**为什么 ②③ 不会被 ① 抢走：**

`Timeout` 和 `ConnectionError` 只继承 `RequestException`，**不是** `ValueError` 的子类，所以第一个分支接不住它们。

**为什么 ④ 必须在最后：**

它是 ②③ 的父类，放前面会让 ②③ 变成死代码。

### 这四个分支的顺序总结

| 顺序 | 分支 | 为什么在这个位置 |
|---|---|---|
| ① | `ValueError` | `JSONDecodeError` 的双重身份，必须抢在 `RequestException` 之前 |
| ② | `Timeout` | 具体异常，要在父类之前 |
| ③ | `ConnectionError` | 具体异常，要在父类之前 |
| ④ | `RequestException` | 父类兜底，必须最后 |

> **通用规则：排 `except` 顺序时，画一下继承关系，子类一律在父类之前。** 遇到多重继承（像 `JSONDecodeError` 这样同时继承两条线），要确认它不会被任何一个父类分支提前截走。

## 3. `logger.exception()` 的参数该传什么

```python
logger.exception(e)                      # 不推荐
logger.exception("POST 请求失败")         # 推荐
```

`logger.exception()` **本来就会自动记录当前异常的类型、消息和完整堆栈**。所以参数的作用是补充「程序当时在做什么」这个上下文，而不是重复异常自身的信息。

传 `e` 的结果是日志里异常信息出现两遍，而「当时在干什么」这个最有价值的信息反而没有。

更好的做法是带上关键参数：

```python
logger.exception("POST 请求失败，URL: %s", url)
```

这样日志同时有：在做什么（POST 请求）、对谁做（URL）、出了什么错（自动记录的异常和堆栈）。

## 4. 裸 `raise` 而不是 `raise e`

```python
except requests.exceptions.HTTPError as e:
    logger.exception("...")
    raise e            # 不推荐
    raise              # 推荐
```

两者都会重新抛出异常，但**裸 `raise` 保留原始的异常传播链和完整堆栈**。`raise e` 会把当前这一行作为新的抛出点，traceback 里原始出错位置的信息可能变得不完整。

另外写 `raise e` 还得先 `as e` 把异常绑定到变量，而如果后面没用到 `e`，就会留下一个无用变量——**这正是仓库 `README.md` 提到的 ruff 告警之一**：

```python
except ValueError as e:      # as e 之后没用到 e，ruff 会报
    logger.exception("...")
    raise
```

规律：`logger.exception()` 自己会带异常信息，所以**用了 `logger.exception()` + 裸 `raise` 的 `except` 子句通常不需要 `as e`**。

## 5. `logger.setLevel()` 不等于配置日志

第一版写的是：

```python
if __name__ == '__main__':
    logger.setLevel(logging.INFO)     # ← 不够
```

区别：

| 写法 | 做了什么 |
|---|---|
| `logger.setLevel(logging.INFO)` | 只设置**这一个 logger** 的级别阈值 |
| `logging.basicConfig(level=logging.INFO)` | 给 **root logger 配置 handler**，决定日志去哪、什么格式 |

只设级别不配 handler 时，日志仍然没有正式的输出通道——WARNING 以上靠 `lastResort` 勉强输出（Day13 实测过），INFO 直接丢掉。

所以入口要用 `basicConfig()`，而且通常带格式：

```python
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s"
)
```

## 6. 异常粒度：分开还是合并

最终版分别捕获了 `Timeout`、`ConnectionError`、`RequestException`，三个分支做的事完全一样（记日志 + `raise`）。

这种情况下**可以合并**：

```python
except requests.exceptions.RequestException:
    logger.exception("POST 请求失败")
    raise
```

什么时候该分开：**只有当处理方式真的不同时。** 比如：

- `Timeout` → 重试（可能只是网络抖动）
- `ConnectionError` → 告警（可能服务挂了）
- `HTTPError` → 看状态码，4xx 不重试、5xx 重试

> 一条值得记住的原则：**不要为了代码看起来专业而增加不必要的复杂度。** 三个分支做同一件事，就是三倍的维护成本和零收益。等真的要区分处理时再拆开。

## 7. 思考题：服务器返回 500 时会发生什么

```python
response.raise_for_status()
return response.json()
```

1. **`response.json()` 还会执行吗？** 不会。`raise_for_status()` 在 500 时抛出 `HTTPError`，当前 `try` 块的后续代码直接跳过。
2. **会被哪个 `except` 捕获？** `HTTPError` 是 `RequestException` 的子类，所以会被 `except requests.exceptions.RequestException` 捕获（如果没有更具体的 `except HTTPError` 在它前面）。
3. **`raise` 之后异常去哪？** 继续沿调用栈向上传播，直到遇到能处理它的 `except`；一路没人接就终止程序并打印 traceback。

> 第一问是本节的要点：**`raise_for_status()` 抛异常后，同一个 `try` 块里后面的代码一行都不会执行。** 这就是「状态检查必须在 JSON 解析之前」能起作用的机制——不是「解析会被跳过」这么模糊，而是异常直接中断了整个代码块。

---

# 第二部分 · 当天的练习

## 一、题目

写 `post_user(url: str, user: dict)`：用 `requests.post()` 发 JSON、设 `timeout=10`、`raise_for_status()` 检查状态、返回解析后的 JSON、用 `logger.exception()` 记录异常并 `raise` 向上抛。

三道理解题的回答全部正确：

> 1. `json=`　2. 序列化 JSON 并设置合适的 Content-Type　3. 记录异常并 raise

## 二、第一版的五个问题

```python
def post_user(url: str, user: dict) -> Any:
    try:
        response = requests.post(url, json=user)      # ① 漏了 timeout
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        logger.exception(e)                           # ② 参数传了异常对象
        raise e                                       # ③ 用了 raise e
    except ValueError as e:
        logger.exception(e)
        raise e
    # ④ 没有 RequestException 兜底

if __name__ == '__main__':
    logger.setLevel(logging.INFO)                     # ⑤ 只设级别，没配 handler
```

| 问题 | 后果 |
|---|---|
| ① 漏了 `timeout` | 对方不响应时程序无声挂住（Day15 学过又忘） |
| ② `logger.exception(e)` | 异常信息记两遍，缺少「在做什么」的上下文 |
| ③ `raise e` | 丢失原始传播链 |
| ④ 只捕获 `HTTPError` | `Timeout`、`ConnectionError` 不会被记录就穿透出去 |
| ⑤ `logger.setLevel()` | 没有 handler，INFO 日志实际不输出 |

> ① 值得单独说一句：`timeout` 在 Day15 刚学过、Day16 一直带着，Day17 换成 POST 就漏了。
> **换一个 API 时容易丢掉上一个 API 的配套要求**——这类遗漏靠记忆防不住，要靠检查清单或者 lint 规则。

## 三、最终代码

因为这一天没有留下文件，完整代码记在这里：

```python
import logging
from typing import Any

import requests

logger = logging.getLogger(__name__)


def post_user(url: str, user: dict) -> Any:
    try:
        response = requests.post(url, json=user, timeout=10)
        response.raise_for_status()
        return response.json()
    except ValueError:
        logger.exception("服务器响应 JSON 解析失败")
        raise
    except requests.exceptions.Timeout:
        logger.exception("请求超时")
        raise
    except requests.exceptions.ConnectionError:
        logger.exception("连接失败")
        raise
    except requests.exceptions.RequestException:
        logger.exception("请求异常")
        raise


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s"
    )

    url_path = "https://httpbin.org/post"
    user = {"name": "Python", "remark": "你好"}

    try:
        resp = post_user(url_path, user)
        print("响应：", resp)
    except requests.exceptions.RequestException:
        print("网络请求失败，请稍后重试")
    except ValueError:
        print("服务器返回的数据格式错误")


if __name__ == "__main__":
    main()
```

> 注意 `main()` 里的 `except` 顺序：这里 `RequestException` 在 `ValueError` 前面，
> 所以「服务器返回的数据格式错误」这句**仍然不会出现**——JSON 解析失败会走第一个分支。
> 这个位置的顺序问题在当时没有被指出，和 Day16 的 `main()` 是同一个毛病。
> 要修就把两个分支调换位置。

## 四、四版迭代的轨迹

| 版本 | 改动 | 剩余问题 |
|---|---|---|
| 10:41 第一版 | 基本结构完成 | 五个问题（见上） |
| 10:45 第二版 | 补上 `timeout`、改用裸 `raise` | 异常类型名写错 |
| 10:47 第三版 | 继续修异常类型 | 还有两处类型名不对 |
| 10:49 最终版 | **`ValueError` 提到最前，四个分支顺序正确** | `as e` 未使用；日志描述可更准确 |

最终版被明确肯定的一点是：

> `ValueError` 放在 `RequestException` 前面：正确考虑了 JSON 解码异常的多重继承

**这正是 Day14-16 连续踩了三次的坑，在这里修对了。**

## 五、现在回头看

### 一、`except ValueError as e:` 的 `e` 没用到

```python
except ValueError as e:        # as e 之后，e 没有被使用
    logger.exception("参数解析失败")
    raise
```

`logger.exception()` 自己会带异常信息，`raise` 也不需要 `e`，所以 `as e` 是多余的。**这是仓库 `README.md` 里那 14 个 ruff 告警的主要来源。**

### 二、日志描述不准确

```python
logger.exception("参数解析失败")       # 容易误解成「用户传入的参数有问题」
logger.exception("服务器响应 JSON 解析失败")   # 准确
```

出错的是**服务器返回的数据**，不是调用方传入的参数。日志文案会直接影响排查方向——这和 Day15/Day16 那个「把格式错误记成请求失败」是同一类问题，只不过这次是文字不准，上次是分支不对。

### 三、`main()` 的 `except` 顺序没改

见上面代码里的注释。`fetch_data` 层修对了，`main` 层漏了。**同一个问题在同一个文件的两个位置，只改了一处**——这类遗漏很常见，所以修 bug 时应该全局搜一遍同样的模式。

### 四、这一天的代码没有存成文件

`dailypractice/Day17/` 只有 `__init__.py`。往后复习时，Day17 的内容只能靠这份课件和原始对话。

> 建议：**练习代码即使不完美也要落盘。** Day15、Day16 的文件都在，Day17 断了一天，整条 A 线的代码演进就缺了一环——而这一天恰好是异常顺序修正的关键节点。

## 六、复习自测

1. `json=` 和 `data=` 分别发送什么格式的请求体？
2. 为什么 `except ValueError` 必须写在 `except RequestException` 前面？
3. `Timeout` 和 `ConnectionError` 会被 `except ValueError` 捕获吗？为什么？
4. `logger.exception(e)` 和 `logger.exception("POST 请求失败")` 哪个更好？为什么？
5. `raise` 和 `raise e` 有什么区别？
6. `logger.setLevel(logging.INFO)` 和 `logging.basicConfig(level=logging.INFO)` 的区别？
7. 三个 `except` 分支做同样的事，该合并还是保留？什么情况下该分开？
8. 服务器返回 500 时，`raise_for_status()` 后面的 `response.json()` 会执行吗？
9. 用了 `logger.exception()` 和裸 `raise` 的 `except` 子句，还需要 `as e` 吗？

<details>
<summary>参考答案</summary>

1. `json=` 把字典序列化成 JSON 并自动设 `Content-Type: application/json`；`data=` 传字典时按表单格式编码（`application/x-www-form-urlencoded`）。
2. 因为 `requests.exceptions.JSONDecodeError` 同时继承 `ValueError` 和 `RequestException`。如果 `RequestException` 在前，JSON 解析失败会被它先捕获，日志记成「请求失败」，而 `except ValueError` 成为死代码。
3. 不会。它们只继承 `RequestException`，不是 `ValueError` 的子类。
4. 后者。`logger.exception()` 本来就会自动记录异常类型、消息和完整堆栈，参数应该补充「程序当时在做什么」这个上下文。传 `e` 会让异常信息重复，而真正有价值的上下文反而缺失。
5. 裸 `raise` 原样重抛当前异常，保留完整的原始传播链；`raise e` 会把当前行作为新的抛出点，原始出错位置的信息可能不完整。
6. 前者只设置一个 logger 的级别阈值；后者给 root logger 配置 handler，决定日志输出到哪、用什么格式。只设级别不配 handler，INFO 日志实际不会输出。
7. 该合并——三个分支做同一件事就是三倍维护成本零收益。只有处理方式真的不同时才分开，比如 `Timeout` 重试、`ConnectionError` 告警、`HTTPError` 按状态码决定。
8. 不会。`raise_for_status()` 抛出 `HTTPError` 后，当前 `try` 块里后续代码一行都不执行。
9. 不需要。`logger.exception()` 自动带异常信息，裸 `raise` 也不需要引用异常对象，`as e` 是多余的，ruff 会告警。

</details>
