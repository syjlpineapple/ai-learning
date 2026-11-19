# Day 21 · 单元测试与 Mock

> **学习日** 2026-11-09（13:32 - 15:26，含一长段环境排查）
> **对应代码** [`dailypractice/Day21/`](../../../dailypractice/Day21/)（`demo.py` / `test_api_client.py`）
> **原始对话** `courseware/_raw/markdown/10_Python每日练习出题 (2).md`（对话里称「Day 21」）

> 这一节给 Day20 的 `APIClient` 写测试，是 A 线从「手写 assert」转向「真正的单元测试」的节点。
> 另外这天花了近一小时排查环境问题，那段过程本身很有价值，单列在第三部分。

## 本节掌握

- 为什么单元测试要隔离外部依赖
- 单元测试 / 集成测试 / 端到端测试的分界
- `Mock` 与 `MagicMock`；`return_value` 与 `side_effect`
- 替换真实依赖：`client.session.post = MagicMock(...)`
- `assert_called_once_with()` 验证调用行为
- **MagicMock 的静默特性**，以及它对断言方法做的特殊保护
- **pytest 会捕获输出**——`print` 没显示不等于没执行
- `conftest.py` 的向上查找机制

---

# 第一部分 · 知识讲解

## 1. 为什么需要 Mock

Day20 的 `APIClient.post()` 里有这一行：

```python
response = self.session.post(url, json=data, timeout=10)
```

直接测它就会**真的发 HTTP 请求**，于是测试会因为这些原因失败：

- 网络断了
- 服务器挂了或在维护
- API Key 过期
- 对方限流

而且慢——每个测试都要等一次网络往返。

但今天真正想验证的是：

1. URL 拼接对不对？
2. 有没有把正确的数据传给 POST？
3. `timeout` 设了吗？
4. HTTP 500 时会不会正确抛异常？
5. JSON 解析失败能不能正确处理？

**这五件事全都不需要真的联网。** Mock 的作用就是用一个可控的假对象替代真实依赖，让测试只关注「我的代码逻辑对不对」。

## 2. 三种测试的分界

| 类型 | 测什么 | 访问真实外部系统 |
|---|---|---|
| 单元测试 | 单个函数或类的行为 | 不访问 |
| 集成测试 | 多个模块协作是否正确 | 可能访问 |
| 端到端测试 | 完整业务流程 | 通常访问真实或测试环境 |

对照本节：

- 测 `APIClient.post()` 有没有正确调用 `session.post()` → **单元测试**
- 测 `APIClient` 和真实测试服务器能否通信 → 集成测试

两种都需要，但比例不同：单元测试应该最多（快、稳定、定位准），端到端最少（慢、脆弱，但能发现集成层面的问题）。

## 3. pytest 的发现规则

```bash
pip install pytest
pytest
```

pytest 靠**命名约定**自动发现测试，不需要注册：

| 对象 | 约定 |
|---|---|
| 文件 | `test_*.py` 或 `*_test.py` |
| 函数 | `test_` 开头 |
| 类 | `Test` 开头（类里的方法也要 `test_` 开头） |

这就解释了 Day10 那个「测试一个都没跑」的现象——那个文件的断言包在 `if __name__ == "__main__"` 里，没有任何 `test_` 开头的函数，pytest 自然收集到 0 个。

断言直接用 Python 的 `assert`，不需要 `assertEqual` 这类方法。pytest 会重写断言、在失败时打印出两边的实际值。

## 4. Mock 与 MagicMock

```python
from unittest.mock import Mock, MagicMock
```

标准库自带，不用安装。

| 对象 | 区别 |
|---|---|
| `Mock` | 基础的模拟对象 |
| `MagicMock` | 额外支持魔术方法（`__len__`、`__iter__`、`__enter__` 等） |

实践中**默认用 `MagicMock`** 就行——它能应付更多情况，比如被测代码对返回值做 `len()` 或用在 `with` 语句里。

基本用法：

```python
user = Mock()

user.id = 1                                      # 设置属性
user.get_email.return_value = "aaa@gmail.com"    # 设置方法的返回值

print(user.id)           # 1
print(user.get_email())  # aaa@gmail.com
```

**核心思想：你可以规定这个假对象的任何行为。** `user.get_email()` 不会执行任何真实逻辑，直接返回你指定的值。

## 5. `return_value` 与 `side_effect`

| 属性 | 作用 |
|---|---|
| `return_value` | 调用时**返回**什么 |
| `side_effect` | 调用时产生什么**副作用**——最常用的是抛异常 |

```python
# 让 json() 返回指定数据
mock_response.json.return_value = {"id": 1, "name": "jack"}

# 让 raise_for_status() 抛出 HTTPError（模拟服务器 500）
mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("500 Server Error")
```

`side_effect` 还可以传一个列表（每次调用依次返回其中一项，用于模拟「第一次失败、第二次成功」的重试场景），或者传一个函数（根据参数动态决定行为）。

> **`side_effect` 是测试异常路径的关键。** 没有它就只能靠真实触发错误——而「让服务器返回 500」这件事你没法控制。

## 6. 替换真实依赖

```python
client.session.post = MagicMock(return_value=mock_response)
```

这一行是整个测试的核心：**把真实的 `session.post` 方法整个换成一个假的。** 之后执行 `client.post("/users", data)` 时，内部调用的 `self.session.post(...)` 实际上调的是这个 Mock，不会碰网络。

能这样做的前提是 Day20 把 Session 存成了实例属性 `self.session`——**可替换性来自于依赖是「可访问的属性」而不是写死在方法里**。如果 Day20 在 `post()` 方法里直接调 `requests.post(...)`，就只能用 `unittest.mock.patch` 去替换模块级函数，麻烦得多。

> 这是 Day20「Session 存在 `__init__` 里」的意外收益：不仅复用了连接，还顺带让代码变得可测试。**好的结构往往同时带来多个好处。**

## 7. `assert_called_once_with()`：验证调用行为

```python
client.session.post.assert_called_once_with(
    "https://example.com/user_info",
    json={"name": "jack"},
    timeout=10,
)
```

这一个断言同时检查了四件事：

- `session.post` **被调用过**
- **只调用了一次**
- 位置参数是那个拼好的 URL
- 关键字参数是 `json={"name": "jack"}` 和 `timeout=10`

**这比只检查返回值强得多。** 只断言返回值的话，下面这些 bug 都发现不了：URL 拼错、`timeout` 忘了传、数据传成了 `data=` 而不是 `json=`、同一个请求被发了两次。

常用的几个断言方法：

| 方法 | 验证什么 |
|---|---|
| `assert_called_once()` | 只被调用了一次（不管参数） |
| `assert_called_with(...)` | **最后一次**调用的参数 |
| `assert_called_once_with(...)` | 只调用一次**且**参数符合 |
| `assert_not_called()` | 从未被调用 |
| `mock.call_count` | 被调用的次数（属性，不是断言） |

还可以验证「状态检查有没有做」：

```python
mock_response.raise_for_status.assert_called_once()
```

如果被测代码忘了写 `raise_for_status()`，这个断言会失败——**测的是「有没有做该做的事」，而不只是「结果对不对」**。

## 8. MagicMock 的静默特性与它的保护

这是用 Mock 最需要警惕的地方：**MagicMock 对任何属性访问都返回一个新的 MagicMock，不会报 `AttributeError`。**

实测：

```python
m = MagicMock()
m.close                      # MagicMock
m.close()                    # MagicMock
m.totally_made_up_method     # MagicMock  ← 完全不存在的方法也照单全收
```

所以如果被测对象的方法改名了、或者你把方法名拼错了，Mock 不会提示，测试可能照样「通过」——**但其实什么都没验证**。

### 好消息：断言方法有特殊保护

实测发现标准库做了专门的防御：

```python
m.assret_called_once          # 故意拼错
# AttributeError: 'assret_called_once' is not a valid assertion.
#                 Did you mean: 'assert_called_once'?
```

**以 `assert` 形似开头的属性名会被检查**，拼错会立刻报错并给出建议。这挡住了最危险的一类失误——如果断言方法拼错也静默通过，那测试就是彻底的假测试了。

### 防御手段：`spec`

想让 Mock 也检查普通方法名，可以用 `spec`：

```python
mock_response = MagicMock(spec=requests.Response)
mock_response.jsno()          # AttributeError，因为 Response 没有 jsno 方法
```

`spec` 让 Mock 只接受真实对象拥有的属性。代价是写起来啰嗦一点，收益是「被测对象改了接口，测试会立刻失败」而不是假装通过。

## 9. pytest 会捕获输出

这是当时的一个疑问：代码里有 `print(user.id)`，但用 pytest 跑却看不到输出，「为什么没有打印，而是执行了单元测试」。

**实测结论：`print` 执行了，只是输出被 pytest 捕获了。**

```text
$ pytest demo.py -q
.                                      [100%]
1 passed in 0.10s                      ← 看不到 print

$ pytest demo.py -q -s
1
aaa@gmail.com                          ← print 的输出出现了
.
1 passed in 0.09s
```

pytest 默认捕获所有 stdout/stderr，**只在测试失败时才把捕获的内容打出来**（因为那时输出对排查有用）。测试通过时就丢掉，保持输出整洁。

关闭捕获的两种写法：

```bash
pytest -s                # 简写
pytest --capture=no      # 完整写法
```

> 两个推论：
>
> 1. **不要用「print 没显示」判断代码没执行到。** 这和 Day13 那个「不要用日志判断代码是否执行」是同一类误判。
> 2. 模块级代码（`print`、`Mock()` 的创建）在 pytest **导入**该文件时就会执行——这是 Day10 学的 import 机制。pytest 收集测试必须先导入文件。

---

# 第二部分 · 当天的练习

## 一、三个测试

### 测试 1：POST 成功路径

```python
def test_post_success():
    client = APIClient("https://example.com", "test_key")
    try:
        mock_response = MagicMock()
        mock_response.json.return_value = {"id": 1, "email": "abc@gmail.com"}

        client.session.post = MagicMock(return_value=mock_response)

        resp = client.post("/user_info", {"name": "jack"})

        assert resp == {"id": 1, "email": "abc@gmail.com"}

        # 校验请求地址、请求参数、timeout 是否符合预期
        client.session.post.assert_called_once_with(
            "https://example.com/user_info",
            json={"name": "jack"},
            timeout=10,
        )

        # 验证是否检查了 HTTP 状态码
        mock_response.raise_for_status.assert_called_once()
    finally:
        client.close()
```

三层验证都到位了：返回值对、调用参数对、状态检查做了。而且 `finally` 里关 Session（Day20 的习惯延续）。

**注意 URL 那个断言的价值**：它验证了 `base_url.rstrip("/")` 加 `endpoint.lstrip("/")` 的拼接结果是 `https://example.com/user_info`，没有双斜杠。Day20 写的那两个 strip，在这里被测到了。

### 测试 2：HTTP 失败路径

```python
def test_post_fail():
    client = APIClient("https://example.com", "test_key")
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = (
        requests.exceptions.HTTPError("500 Server Error")
    )
    client.session.post = MagicMock(return_value=mock_response)
    try:
        client.post("/users", {"name": "jack"})
        assert False, "应该抛出 HTTPError"
    except requests.exceptions.HTTPError:
        pass
    finally:
        client.close()
```

用 `side_effect` 模拟服务器 500，验证异常会向上传播（Day16 学的 `logger.exception()` + `raise` 的效果）。

`assert False, "应该抛出 HTTPError"` 是手写的「预期异常」模式——如果 `client.post()` 居然没抛异常，就会执行到这一行让测试失败。这和 Day09 的 `try/except/else` 是同一个思路的变体。

代码里自己留了注释，写明了更好的写法：

```python
try:
    with pytest.raises(requests.exceptions.HTTPError):
        client.post("/users", {"name": "jack"})
finally:
    client.close()
```

`pytest.raises()` 比手写 `assert False` 清楚：意图直接写在 `with` 上，而且不会因为漏写 `assert False` 而变成假测试。Day22 会正式用上它。

### 测试 3：close 被调用

```python
def test_call_close():
    client = APIClient("https://example.com", "test_key")
    client.session.close = MagicMock()
    client.close()
    client.session.close.assert_called_once()
```

验证 `APIClient.close()` 真的把 Session 关了，而不是个空方法。

## 二、那个多余的括号

这个测试最初写成了：

```python
client.session.close().assert_called_once()        # ← 多了一对 ()
```

报错：

```text
FAILED test_api_client.py:66 (test_call_close)
```

实测确认了原因：

```text
正确写法 session.close.assert_called_once()
  → 通过

错误写法 session.close().assert_called_once()
  → 失败: Expected 'mock' to have been called once. Called 0 times.
```

**加了括号之后，断言的对象变了：**

| 写法 | 实际在做什么 |
|---|---|
| `client.session.close` | 拿到那个 Mock 对象本身 |
| `client.session.close.assert_called_once()` | 在它身上断言「你被调用过一次吗」✅ |
| `client.session.close()` | **调用**它，得到返回值（又是一个新 MagicMock） |
| `client.session.close().assert_called_once()` | 在**返回值**身上断言——而那个 Mock 从没被调用过 ❌ |

一句话记法：

- `mock_method()` —— **执行**模拟方法
- `mock_method.assert_called_once()` —— **验证**模拟方法被调用过

> 报错信息里有个线索：`Expected 'mock' to have been called once`，名字是 `'mock'` 而不是 `'close'`。
> **断言失败时如果 Mock 的名字和你预期的对象不一致，说明断言打在了错的对象上。**
>
> 这个 bug 之所以能悄悄出现，正是因为 MagicMock 的静默特性——`close()` 返回的新 Mock 照样有
> `assert_called_once` 方法，不会报 `AttributeError`。

---

# 第三部分 · 环境排查（这天最花时间的部分）

代码只写了几十行，但有近一小时花在一个和代码无关的问题上。这段过程很值得记。

## 一、现象

在 `Day21/` 目录下执行 `pytest`：

```text
ImportError while loading conftest 'D:\...\backend\tests\conftest.py'.
..\..\conftest.py:4: in <module>
    from fastapi.testclient import TestClient
ModuleNotFoundError: No module named 'fastapi'
```

当时的疑问很自然：**「Pytest 依赖 fastapi 吗，还是什么原因」**

## 二、根因：`conftest.py` 的向上查找

**pytest 本身完全不依赖 FastAPI。** 问题出在项目结构：

```text
backend/
├── app/
├── tests/
│   ├── conftest.py              ← 这个文件 import 了 fastapi
│   └── dailypractice/
│       └── Day21/
│           └── test_api_client.py
└── pyproject.toml
```

`conftest.py` 的内容：

```python
import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture()
def client() -> TestClient:
    return TestClient(app)
```

**pytest 启动时会从测试文件所在目录逐级向上查找所有 `conftest.py` 并加载它们**（这是它的 fixture 共享机制）。所以即使在 `Day21/` 里跑一个和 FastAPI 毫无关系的测试，上层那个 `conftest.py` 也会被导入，而它第一行就 `import fastapi`——环境里没装，整个测试收集直接失败。

依赖链是这样的：

```text
pytest  →  自动加载 conftest.py  →  import fastapi  →  环境里没有 → 收集失败
```

## 三、这里学到的概念：直接依赖与间接依赖

| 类型 | 含义 | 本例 |
|---|---|---|
| 直接依赖 | 你的代码明确使用的库 | `pytest`、`requests` |
| 间接依赖 | 你用的工具/配置又需要的库 | `fastapi`（被 `conftest.py` 需要） |

**报错里出现的库名，不一定是你的代码在用。** 这类问题的排查思路是顺着「谁加载了它」往上找，而不是去怀疑 `pytest` 自己需要 FastAPI。

当时的排查动作是对的：看 `conftest.py` 的内容、看 `pyproject.toml` 的依赖声明、`pip show fastapi` 确认装没装。**先收集证据再下结论**（Day11 那套方法）。

## 四、两个解法

| 方案 | 做法 | 适用 |
|---|---|---|
| A | `python -m pip install -e ".[dev]"` 装齐项目依赖 | 在现有项目里学习，用项目统一的依赖配置 |
| B | 把练习挪到独立目录和独立虚拟环境 | 希望练习完全独立于主项目 |

当时选了 A。**而这个仓库后来做的正是方案 B**——把 `dailypractice/` 和 `nlp/` 从 `sell-gen` 迁出成独立仓库。仓库 `README.md` 里写了迁出的理由：

> 学习代码和产品代码共用一套工程配置会互相干扰：产品代码要 `mypy strict`，练习代码本来就该允许写得不漂亮，这两件事无法共存在同一份配置里。

**这一天遇到的 `conftest.py` 冲突，就是那个「互相干扰」的早期信号。**

## 五、顺带发现的另一件事

迁移时还修了这个文件的导入路径（仓库 `README.md` 的迁移记录）：原来写的是裸导入或 `tests.dailypractice.Day20.api_client`，迁出后包路径变了，改成了 `dailypractice.Day20.api_client`。

值得注意的是 **Day21 的测试导入的是 Day20 的 `APIClient`**，而不是自己复制一份。好处是不重复；代价是两节之间产生了耦合——改 Day20 的代码会让 Day21 的测试失败。当时题目本意是「把 Day20 的 APIClient 复制过来」，实际做法是直接导入。

---

## 复习自测

1. 为什么单元测试不该真的发 HTTP 请求？
2. `return_value` 和 `side_effect` 分别用在什么场景？
3. `client.session.post = MagicMock(...)` 这一行为什么能阻止真实请求？它依赖 Day20 的什么设计？
4. `assert_called_once_with()` 同时验证了哪几件事？只断言返回值会漏掉哪些 bug？
5. `MagicMock` 访问一个不存在的方法会报错吗？断言方法拼错会报错吗？
6. `spec=` 参数解决什么问题？
7. 用 pytest 跑测试时看不到 `print` 输出，是因为代码没执行吗？怎么看到？
8. `client.session.close()` 和 `client.session.close` 在断言里有什么区别？
9. 在子目录跑 `pytest` 却报 `No module named 'fastapi'`，是 pytest 需要 FastAPI 吗？

<details>
<summary>参考答案</summary>

1. 因为测试会受网络、服务器状态、API Key 有效期、限流的影响而失败，这些都和被测代码的正确性无关；而且每个测试都要等网络往返，很慢。
2. `return_value` 指定调用时返回什么；`side_effect` 指定调用时的副作用，最常用的是抛异常——这是测试异常路径的关键，因为你没法让真实服务器按需返回 500。
3. 因为它把 `session.post` 这个属性整个替换成了 Mock，被测代码内部调用的 `self.session.post(...)` 实际调的是 Mock。它依赖 Day20 把 Session 存成了实例属性 `self.session`——依赖是可访问的属性才容易替换。
4. 验证了：被调用过、只调用一次、位置参数正确、关键字参数正确。只断言返回值会漏掉 URL 拼错、`timeout` 没传、用了 `data=` 而不是 `json=`、同一请求发了两次。
5. 访问不存在的方法**不会**报错，返回一个新的 MagicMock（静默特性）。但断言方法拼错**会**报 `AttributeError` 并提示正确拼写——标准库对此做了专门保护。
6. `spec=` 让 Mock 只接受真实对象拥有的属性，访问不存在的方法会报错。解决的是「被测对象接口改了，Mock 却假装一切正常」的问题。
7. 不是。`print` 执行了，输出被 pytest 捕获了（只在测试失败时才显示）。加 `-s` 或 `--capture=no` 可以看到。
8. `close` 是 Mock 对象本身，在它上面断言才是检查「它被调用过吗」；`close()` 是调用它，返回一个新 Mock，在新 Mock 上断言永远会失败，因为那个对象从没被调用过。
9. 不是。pytest 会从测试文件目录逐级向上加载所有 `conftest.py`，而上层的 `conftest.py` 里 `import fastapi`。报错里的库名不一定是你的代码在用，要顺着「谁加载了它」往上查。

</details>
