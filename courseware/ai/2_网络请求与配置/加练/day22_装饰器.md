---
kind: problem
outline: [2, 2]
time: 40 分钟
uses: [闭包, "@ 语法糖", functools.wraps, 带参数的装饰器, 叠放顺序]
record:
  - text: Day22 Fixture
    link: https://github.com/syjlpineapple/ai-learning/blob/main/courseware/records/python/Day22.md
---

# 第 15 题 · 装饰器

第 8 题的 `with_retry` 每次都得这样用：`with_retry(lambda: fetch_scores(url))`。调用的地方一多，到处都是 lambda。这一题把它做成装饰器，写在函数定义上面一次，以后直接调用函数就会自动重试。顺手再写一个记录调用的 `@logged`。

`@pytest.fixture`、`@pytest.mark.parametrize`、`@dataclass` 都是装饰器，前面一直在用。写完这一题，你就知道 `@` 到底做了什么。

## 题目

在 [`code/m08_testing/p15_decorators_exercise.py`](../../code/m08_testing/p15_decorators_exercise.py) 里实现两个装饰器：

1. **`retrying`**：被装饰的函数调用时按第 8 题的规则重试（直接调用 `with_retry`）。两种写法都要能用：
   - `@retrying` 不带括号，用默认参数
   - `@retrying(attempts=5, sleep=delays.append)` 带参数
2. **保留原函数的样子**：被装饰以后，`__name__`、`__doc__`、参数签名和原来一样。被装饰的 pytest 测试函数，fixture 照样能注入
3. **`logged(logger)`**：调用前记一条 DEBUG（带函数名），成功后记一条 DEBUG（带耗时，「秒」）；出错时记一条 WARNING（带异常的类名，不带 traceback），然后**把同一个异常原样抛出去**
4. **叠放顺序**：`@logged` 写在 `@retrying` 上面时，重试最后成功了，`logged` 不记 WARNING

```python
@logged(logger)
@retrying(attempts=3)
def get_scores(base_url: str) -> list[dict]:
    ...
```

**验证**（在 `code/` 目录下）

```powershell
pytest tests/test_m08.py -k p15 -v
```

现在是 `19 passed, 12 skipped`，全部做完是 `31 passed`。

::: details 提示：@ 到底做了什么
下面每组的两种写法完全一样：

```python
@d                          #   def f(): ...
def f(): ...                #   f = d(f)

@d(3)                       #   def f(): ...
def f(): ...                #   f = d(3)(f)
```

`d` 收到原来的 `f`，返回什么，`f` 这个名字以后就指向什么。通常返回一个新函数 `wrapper`，它在里面调用原来的 `f`，前后加点东西。
:::

::: details 提示：带参数和不带参数怎么区分
`@retrying` 时，Python 调用 `retrying(f)`，第一个参数 `fn` 就是函数。`@retrying(attempts=5)` 时，Python 先调用 `retrying(attempts=5)`，这时 `fn` 是 `None`，你要返回一个「接收函数的装饰器」。所以签名里 `attempts` 这些参数前面有一个 `*`：它们只能用关键字传，不会和 `fn` 混在一起。
:::

::: details 提示：wrapper 怎么写
`def wrapper(*args, **kwargs)` 接住所有参数，再原样交给原函数：`func(*args, **kwargs)`。交给 `with_retry` 的是 `lambda: func(*args, **kwargs)`。要求 2 用 `@functools.wraps(func)` 装饰 `wrapper`。
:::

<Reveal>

## 讲评

### 参考答案

```python
def retrying(fn=None, *, attempts=3, base_delay=0.5, sleep=time.sleep):
    def decorate(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return with_retry(lambda: func(*args, **kwargs), attempts=attempts,
                              base_delay=base_delay, sleep=sleep)
        return wrapper

    if fn is not None:          # @retrying
        return decorate(fn)
    return decorate             # @retrying(...)


def logged(logger):
    def decorate(func):
        name = func.__qualname__

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            logger.debug("调用 %s", name)
            started = time.perf_counter()
            try:
                result = func(*args, **kwargs)
            except Exception as e:
                logger.warning("%s 失败：%s", name, type(e).__name__)
                raise
            logger.debug("%s 用了 %.3f 秒", name, time.perf_counter() - started)
            return result
        return wrapper
    return decorate
```

带类型标注的版本见 [`p15_decorators_solution.py`](../../code/m08_testing/p15_decorators_solution.py)。`wrapper` 能用到外面的 `func`、`attempts`、`logger`，是因为闭包：内层函数记住了它定义时外层的变量，外层函数返回以后也还在。

一个典型的初稿（没用 `wraps`；`retrying` 只支持带括号；`logged` 用 `logger.exception` 记完就结束）跑这一题的测试，**7 个失败**。下面逐个说。

### 坑 1：没有 `functools.wraps`，函数「换了个人」

```python
def no_wraps(fn):
    def wrapper(*args, **kwargs):
        return fn(*args, **kwargs)
    return wrapper
```

```text
no_wraps(sample).__name__              'wrapper'
no_wraps(sample).__doc__               None
inspect.signature(no_wraps(sample))    (*args, **kwargs)
```

装饰以后，`sample` 这个名字指向的是 `wrapper`。日志里、报错里、`pytest -v` 的列表里看到的全是 `wrapper`。更麻烦的是 pytest：它看测试函数的签名，决定要注入哪些 fixture。签名变成了 `(*args, **kwargs)`，它就不知道要注入 `player`：

```text
TypeError: test_x() missing 1 required positional argument: 'player'
```

`@functools.wraps(func)` 把 `func` 的 `__name__`、`__qualname__`、`__doc__`、`__module__` 等属性抄到 `wrapper` 上，再留下 `wrapper.__wrapped__ = func`。`inspect.signature` 会顺着 `__wrapped__` 找到原函数的签名，pytest 用的就是它。**写装饰器，`wrapper` 上面一定加 `@functools.wraps(func)`。**

### 坑 2：`@retrying` 不带括号，函数被当成了参数

初稿只考虑了带括号的写法，`retrying(...)` 永远返回 `decorate`。写成 `@retrying` 时，`retrying(get_scores)` 返回的是 `decorate`，于是 `get_scores` 变成了 `decorate`：

```text
get_scores()   →  TypeError: retrying.<locals>.decorate() missing 1 required positional argument: 'func'
```

套在 pytest 测试上，报错更让人摸不着头脑。pytest 看到测试函数的参数叫 `func`，去找一个叫 `func` 的 fixture：

```text
fixture 'func' not found
```

参考答案用 `fn=None` 加一个 `*` 同时支持两种写法。如果你的装饰器**只**支持带括号，比如 `def factory(attempts: int = 3)`，有类型标注的话，忘了写括号 mypy 能查出来：

```text
error: Argument 1 to "factory" has incompatible type "Callable[[str, int], list[str]]"; expected "int"
```

### 坑 3：记了日志就不抛，失败的测试也能通过

初稿的 `logged`：

```python
try:
    return func(*args, **kwargs)
except Exception:
    logger.exception("%s 失败", func.__name__)       # 没有 raise
```

出错时 `wrapper` 执行到末尾，返回 `None`。调用方拿到 `None`，以为成功了，接着 `for row in get_scores()` 才报 `TypeError: 'NoneType' object is not iterable`，离真正出错的地方已经很远了。

套在测试上更危险。`assert` 失败抛的 `AssertionError` 也是 `Exception`，被这个装饰器接住了：

```python
@swallowing
def test_always_wrong():
    assert 1 + 1 == 3
```

```text
1 passed
```

一个永远错的测试，pytest 报告通过。**装饰器记日志的时候，记完要 `raise`，让异常继续往外走。** 它不知道调用方想怎么处理这个错误，没资格替调用方决定。

参考答案用的是 `logger.warning` 而不是 `logger.exception`：这里只说一句「它失败了」，traceback 留给最终处理这个异常的地方去记（第 13 题的 `main`）。每一层都记 traceback，同一个错误会在日志里出现好几遍。

### 坑 4：叠放顺序决定谁看到什么

```python
@logged(logger)        # 第二个装上，在最外面
@retrying              # 第一个装上，贴着函数
def get_scores(): ...
```

装的时候**从下往上**：`get_scores = logged(logger)(retrying(get_scores))`。调用的时候**从外往里**：先进 `logged`，再进 `retrying`，最后才是 `get_scores`。

前两次失败、第三次成功时：

```text
@logged 在外、@retrying 在里     logged 的 WARNING：0 条    logged 只看到最终结果：成功
@retrying 在外、@logged 在里     logged 的 WARNING：2 条    每一次尝试都经过 logged
```

两种都有用。想知道「这个操作最后失败了没有」，`logged` 放外面；想看每一次尝试，`logged` 放里面。只是要清楚自己选的是哪一种。

### 坑 5：装饰器和默认参数都在 `def` 的那一刻执行

```python
seen = []

def register(fn):
    seen.append(fn.__name__)
    return fn

@register
def get_scores(): ...

seen    →  ['get_scores']        # get_scores 一次都没调用，register 已经执行了
```

`@` 那一行是 `def` 语句的一部分，模块被 import 的时候就执行。所以 `decorate` 里只能做「准备」（比如参考答案里取 `func.__qualname__`），真正干活的事要放在 `wrapper` 里，每次调用才做。测试里专门检查了装饰的时候不能调用原函数。

同样在 `def` 那一刻求值的还有**默认参数**。`retrying` 的默认值 `sleep=time.sleep` 在定义的时候就取好了那个函数，之后再替换 `time.sleep` 对它没有影响：

```text
time.sleep = delays.append        # 和 monkeypatch.setattr(time, "sleep", ...) 一样
@retrying 的函数失败一次          →  还是真的等了 0.50 秒，delays 仍然是 []
```

这就是为什么前面几题都把 `sleep` 做成参数，测试直接传 `sleep=delays.append` 进去，而不是事后去替换 `time.sleep`。

## 复盘

::: tip 这题用到的
- **`@d` 就是 `f = d(f)`**，`@d(x)` 就是 `f = d(x)(f)`；装饰器返回什么，函数名就指向什么
- **闭包**：`wrapper` 记住了外层的 `func`、`attempts`、`logger`
- **`wrapper(*args, **kwargs)` + `func(*args, **kwargs)`**：接住任意参数原样转交，方法的 `self` 也在 `args` 里
- **`@functools.wraps(func)`**：保住名字、文档、签名；pytest 靠签名注入 fixture
- **同时支持 `@d` 和 `@d(...)`**：`fn=None` 加 `*`，判断第一个参数是不是函数
- **记日志的装饰器记完要 `raise`**：吞掉异常会让调用方拿到 `None`，还会让失败的测试通过
- **叠放从下往上装、从外往里执行**：外层只看到里层的最终结果
- **`def` 时执行的**：装饰器本身、默认参数；**调用时执行的**：`wrapper` 的函数体
:::

## 自测

1. 下面的 `get_scores` 最后指向什么？调用它会怎样？

   ```python
   def retrying(attempts=3):
       def decorate(func): ...
       return decorate

   @retrying
   def get_scores(): ...
   ```

2. 不加 `functools.wraps`，一个被装饰的 pytest 测试 `def test_x(player)` 为什么会报 `missing 1 required positional argument`？
3. `@retrying` 在外、`@logged` 在里，重试两次后成功，`logged` 会记几条 WARNING？换个顺序呢？

<details>
<summary>参考答案</summary>

1. `retrying(get_scores)` 把函数当成了 `attempts`，返回的是 `decorate`，所以 `get_scores` 指向 `decorate`。调用 `get_scores()` 报 `TypeError: ... decorate() missing 1 required positional argument: 'func'`。
2. pytest 根据测试函数的签名决定注入哪些 fixture。没有 `wraps`，签名是 `wrapper` 的 `(*args, **kwargs)`，pytest 看不到 `player`，就不传参数直接调用，`wrapper` 再调用原函数时少了 `player`。`wraps` 留下的 `__wrapped__` 让 `inspect.signature` 找到原函数的签名。
3. `logged` 在里面时，每次尝试都经过它，两次失败记 2 条 WARNING。`logged` 在外面时，它只看到 `retrying` 的最终结果，成功了就是 0 条。

</details>

</Reveal>
