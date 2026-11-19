---
kind: problem
outline: [2, 2]
time: 35 分钟
uses: [requests.post, json= 和 data=, headers, 幂等性]
record:
  - text: Day16 json= 与 data=
    link: https://github.com/syjlpineapple/ai-learning/blob/main/courseware/records/python/Day16.md
  - text: Day17 POST 请求
    link: https://github.com/syjlpineapple/ai-learning/blob/main/courseware/records/python/Day17.md
---

# 第 9 题 · 上传成绩

查排行榜是 GET：问几次，答案都一样。上传成绩是 POST：每发一次，服务端就多存一条。第 8 题的重试放到 POST 上，会出一个 GET 没有的问题。

本机服务的上传接口：

```text
POST /scores
请求体：JSON {"player": "张三", "attempts": 3}
成功：201 {"id": 8, "player": "张三", "attempts": 3}
请求体不是 JSON：415；字段不对：400 {"error": "..."}
带了 Idempotency-Key 头、而且这个 key 用过：不再新增，返回上次的结果
```

## 题目

打开 [`code/m05_http/p09_upload_exercise.py`](../../code/m05_http/p09_upload_exercise.py)，实现两个函数：

| 函数 | 做什么 |
|---|---|
| `upload_score(base_url, player, attempts, key=None, timeout=5)` | 上传一条成绩，返回服务端的回答 |
| `upload_with_retry(base_url, player, attempts, timeout=5)` | 失败时用第 8 题的 `with_retry` 重试，**同一条成绩不能存两次** |

**要求**

1. 请求体发 JSON；`key` 不为 `None` 时放进请求头 `Idempotency-Key`；记得 `timeout`
2. 状态码不是 2xx 时抛 `HTTPError`（服务端拒绝的原因在 `e.response.json()["error"]` 里）
3. `upload_with_retry`：测试会让服务端**存好成绩之后拖 2 秒才回答**，客户端 0.5 秒就超时了，以为失败，于是重试。重试之后，服务端只能有这一条成绩

**验证**（在 `code/` 目录下）

```powershell
pytest tests/test_m05.py -k p09 -v
```

现在是 `8 passed, 5 skipped`，全部做完是 `13 passed`。

::: details 提示：要求 1，服务端返回 415
`requests.post` 有两个参数都能放请求体：`data=` 和 `json=`。Day16 讲过它们的区别。
:::

::: details 提示：要求 3，服务端存了两条
第一次请求其实成功了，只是回答没赶上。服务端靠什么认出「第二次请求和第一次是同一条成绩」？这个东西是在重试之前生成，还是每次重试都生成一个新的？
:::

<Reveal>

## 讲评

### 参考答案

```python
def upload_score(base_url, player, attempts, key=None, timeout=5):
    headers = {"Idempotency-Key": key} if key is not None else {}
    response = requests.post(
        f"{base_url}/scores",
        json={"player": player, "attempts": attempts},
        headers=headers,
        timeout=timeout,
    )
    response.raise_for_status()
    data = response.json()
    if not isinstance(data, dict):
        raise requests.exceptions.InvalidJSONError(
            f"期望 JSON 对象，实际是 {type(data).__name__}", response=response)
    return data


def upload_with_retry(base_url, player, attempts, timeout=5):
    key = uuid.uuid4().hex                   # 重试之前生成一次
    return with_retry(lambda: upload_score(base_url, player, attempts, key=key, timeout=timeout))
```

### 坑 1：`data=` 发的是表单

```python
requests.post(url, data={"player": "张三", "attempts": 3})
```

```text
服务端收到的请求体：player=%E5%BC%A0%E4%B8%89&attempts=3
POST /scores 的回答：415 {"error": "请求体必须是 JSON，收到的 Content-Type 是 'application/x-www-form-urlencoded'"}
```

`data=` 传字典时按网页表单的格式编码，`json=` 才会把它变成 JSON，并设好 `Content-Type: application/json`。Day16、Day17 都讲过这一点，口诀是「`json=` 发 JSON，`data=` 发表单」。调大模型的 API 一律用 `json=`。

### 坑 2：重试 POST，成绩存了两条

`with_retry` 直接套在 `upload_score` 上，不带 key：

```text
第 1 次请求：服务端存好了成绩，但 2 秒后才回答 → 客户端 0.5 秒超时，ReadTimeout
第 8 题的规则：ReadTimeout 值得重试 → 等 0.5 秒，第 2 次请求
第 2 次请求：服务端又存了一条，回答 201
服务端最后有 2 条一模一样的成绩
```

测试 `test_p09_review_no_key_duplicates` 实测确认了这件事。**超时不等于失败**：客户端只知道「没等到回答」，不知道服务端到底做没做。GET 重试没关系，因为它只读不写，做几次结果都一样，这叫**幂等**。POST 不是幂等的，盲目重试就会重复。

解决办法是给每一条成绩一个唯一的编号，放在 `Idempotency-Key` 请求头里。服务端记住用过的编号，同一个编号再来就不再新增，直接返回上次的结果。很多支付、下单类的 API 都是这么做的，具体的头名称和规则以对方的文档为准。

### 坑 3：key 在 lambda 里生成，等于没有

第二份典型初稿改对了 `json=`，key 也加了，但写在了 lambda 里：

```python
return with_retry(lambda: upload_score(base_url, player, attempts, key=uuid.uuid4().hex))
```

```text
FAILED test_p09_retry_does_not_duplicate    服务端存了 2 条
1 failed, 4 passed
```

lambda 里的代码在每次调用时才执行，每次重试都生成一个新的 `uuid`。服务端看到的是两个不同的 key，当然存两条。key 要在重试之前生成一次，lambda 只引用它。

这一点很容易看漏，因为其他 4 条测试都过了：只要不出现「请求成功但回答超时」这种情况，有没有 key、key 在哪生成，结果都一样。

### 典型初稿会被哪些测试抓住

第一份初稿用的是 `data=`，key 也在 lambda 里生成：

```text
FAILED test_p09_upload                    HTTPError: 415
FAILED test_p09_validation_error          状态码是 415，不是 400
FAILED test_p09_idempotency_key           HTTPError: 415
FAILED test_p09_retry_does_not_duplicate  HTTPError: 415
FAILED test_p09_upload_with_retry_normal  HTTPError: 415
5 failed
```

`json=` 改对之后只剩坑 3 那一条。

## 复盘

::: tip 这题用到的
- **`requests.post(url, json=..., headers=..., timeout=...)`**：`json=` 发 JSON，`data=` 发表单
- **请求头用 `headers=` 字典传**；`Content-Type` 交给 `json=` 自动设置
- **超时不等于失败**：服务端可能已经做完了，只是回答没赶上
- **幂等**：做一次和做多次结果一样。GET 天然幂等，可以放心重试；POST 不是
- **重试 POST 要带一个唯一编号**（`Idempotency-Key`），而且要在重试之前生成，每次重试都用同一个
:::

M5 到这里就结束了：查询、分类、重试、上传。现在 `fetch_scores`、`upload_score` 都把服务地址作为参数传进来，测试传的是本机服务的地址。真实项目里地址、密钥放在哪？开发、测试、生产三套环境怎么切换？这是下一个模块 M6 配置管理的内容。

## 自测

1. `requests.post(url, data={"a": 1})` 和 `requests.post(url, json={"a": 1})` 发出去的请求体和 `Content-Type` 分别是什么？
2. 客户端上传成绩时遇到 `ReadTimeout`，能断定服务端没有存这条成绩吗？直接重试会怎样？
3. 下面这样写，`Idempotency-Key` 能防止重复吗？为什么？

   ```python
   with_retry(lambda: upload_score(url, "张三", 3, key=uuid.uuid4().hex))
   ```

<details>
<summary>参考答案</summary>

1. `data=` 发表单：请求体是 `a=1`，`Content-Type` 是 `application/x-www-form-urlencoded`。`json=` 发 JSON：请求体是 `{"a": 1}`，`Content-Type` 是 `application/json`。
2. 不能。`ReadTimeout` 只说明客户端没等到回答，服务端可能已经存好了。直接重试会再存一条，出现重复成绩。
3. 不能。lambda 里的代码每次调用时才执行，每次重试都会生成一个新的 key，服务端认为是不同的成绩，照样存两条。key 要在调用 `with_retry` 之前生成一次。

</details>

</Reveal>
