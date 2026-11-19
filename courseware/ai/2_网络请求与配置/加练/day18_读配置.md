---
kind: problem
outline: [2, 2]
time: 40 分钟
uses: [环境变量都是字符串, 必填与可选, 一次报全所有错, "field(repr=False)"]
record:
  - text: Day18 环境变量与密钥
    link: https://github.com/syjlpineapple/ai-learning/blob/main/courseware/records/python/Day18.md
  - text: Day19 bool('false') 是 True
    link: https://github.com/syjlpineapple/ai-learning/blob/main/courseware/records/python/Day19.md
---

# 第 10 题 · 读配置

M5 的 `fetch_scores`、`upload_score` 都把服务地址作为参数传进来，测试传的是本机服务的地址。真实程序里，这个地址、API 密钥、超时时间、要不要开调试，都应该写在代码外面，通过环境变量交给程序。这一题把它们读进来，变成一个类型正确、校验过的 `Settings` 对象。

## 题目

打开 [`code/m06_config/p10_settings_exercise.py`](../../code/m06_config/p10_settings_exercise.py)，实现 `load_settings(environ)`：

```python
@dataclass(frozen=True)
class Settings:
    api_key: str
    base_url: str
    timeout: float
    retries: int
    debug: bool
```

`environ` 是一个「名字 → 字符串」的映射。平时调用 `load_settings(os.environ)`，测试传一个普通字典，就不用真的去改环境变量了（第 8 题 `sleep` 参数也是这个思路）。

| 变量 | 必填 | 类型 | 默认 | 规则 |
|---|---|---|---|---|
| `API_KEY` | 是 | `str` | | |
| `API_BASE_URL` | 是 | `str` | | 以 `http://` 或 `https://` 开头；末尾的 `/` 去掉 |
| `TIMEOUT` | 否 | `float` | `5` | 大于 0 |
| `RETRIES` | 否 | `int` | `3` | 0 到 10 |
| `DEBUG` | 否 | `bool` | `False` | 认 `true/false/1/0/yes/no/on/off`，不分大小写；其他写法报错 |

**要求**

1. 值是空字符串、或者只有空格，当作没设（必填的就是缺失，可选的就用默认值）
2. 值不对时抛 `ConfigError`（已经定义好了，继承 `ValueError`），消息里写出是哪一项、实际的值（用 `!r`）
3. **一次把所有问题都报出来**，而不是遇到第一个就停
4. `Settings` 的每个字段都是对的类型：`timeout` 是 `float`、`retries` 是 `int`、`debug` 是 `bool`
5. **打印 `Settings`、把它拼进字符串时，不能出现密钥**；报错消息里也不能出现密钥

**验证**（在 `code/` 目录下）

```powershell
pytest tests/test_m06.py -k p10 -v
```

现在是 `38 passed, 31 skipped`，全部做完是 `69 passed`。

::: details 提示：要求 1，API_KEY= 没被当成缺失
`environ.get("API_KEY")` 在 `.env` 里写了 `API_KEY=`（等号后面什么都没有）时返回的是 `""`，不是 `None`。`os.getenv("X", "默认")` 也一样：变量存在、值为空时，默认值不生效。
:::

::: details 提示：要求 3，怎么一次报全
不要一发现问题就 `raise`。准备一个列表，每发现一个问题就 `append` 一句话，全部检查完再看列表是不是空的。
:::

::: details 提示：要求 5，repr 里有密钥
dataclass 自动生成的 `__repr__` 会列出所有字段。`dataclasses.field()` 有一个参数能让某个字段不出现在 `repr` 里。
:::

<Reveal>

## 讲评

### 参考答案

```python
@dataclass(frozen=True)
class Settings:
    api_key: str = field(repr=False)
    base_url: str
    timeout: float
    retries: int
    debug: bool


def load_settings(environ: Mapping[str, str]) -> Settings:
    problems: list[str] = []

    def get(name: str) -> str | None:
        value = environ.get(name, "").strip()
        return value or None

    api_key = get("API_KEY")
    base_url = get("API_BASE_URL")
    missing = [n for n, v in (("API_KEY", api_key), ("API_BASE_URL", base_url)) if v is None]
    if missing:
        problems.append(f"缺少 {', '.join(missing)}")
    ...                                  # TIMEOUT、RETRIES、DEBUG 同样：转换失败就 append，不 raise
    if problems or api_key is None or base_url is None:
        raise ConfigError(f"配置有 {len(problems)} 处问题：{'；'.join(problems)}")
    return Settings(api_key=api_key, base_url=base_url.rstrip("/"), ...)
```

完整代码见 [`p10_settings_solution.py`](../../code/m06_config/p10_settings_solution.py)。

### 坑 1：`KEY=` 的值是空字符串，默认值不生效

```text
os.getenv("PE_EMPTY", "默认")      →  ''         变量存在、值为空
os.getenv("PE_EMPTY") or "默认"    →  '默认'
```

`.env` 里写了 `API_KEY=` 却忘了填值，`os.getenv("API_KEY")` 拿到的是 `""`。用 `is None` 判断「没设」就会漏掉它。可选项也一样：`TIMEOUT=` 时 `float(os.getenv("TIMEOUT", "5"))` 拿到的是 `float("")`，报 `ValueError`，而不是用默认的 5。参考答案先 `.strip()`，再把空字符串当成没设。

### 坑 2：环境变量永远是字符串

```text
bool("false")             →  True
os.environ["X"] = 10      →  TypeError: str expected, not int
```

Day19 已经发现了 `bool("false")` 的问题。这一题多认了几种写法，**认不出来的直接报错**：`DEBUG=ture`（拼错了）如果悄悄当成 `False`，你会以为调试开着，其实没开。典型初稿用的是 `.lower() == "true"`，`DEBUG=1`、`DEBUG=yes`、`DEBUG=On` 都被当成了 `False`，`DEBUG=ture` 也没有任何提示。

`TIMEOUT=nan` 能被 `float()` 转换成功，`nan > 0` 是 `False`，所以「必须大于 0」这条规则顺便把它挡住了。

### 坑 3：遇到一个错就停

典型初稿：

```python
api_key = environ.get("API_KEY")
if api_key is None:
    raise ConfigError("缺少 API_KEY")
base_url = environ.get("API_BASE_URL")
if base_url is None:
    raise ConfigError("缺少 API_BASE_URL")
timeout = float(environ.get("TIMEOUT", "5"))
```

配置里有三处错时，你要改一处、启动一次、看到下一个错，来回三遍。部署时这意味着发布三次。参考答案收集所有问题，一次报出来：

```text
ConfigError: 配置有 4 处问题：缺少 API_KEY, API_BASE_URL；TIMEOUT 必须是数字，实际是 'ten'；
RETRIES 必须在 0-10 之间，实际是 '-1'；DEBUG 只能是 true/false/1/0/yes/no/on/off，实际是 'ture'
```

初稿还有一个问题：`float("ten")` 抛的是普通的 `ValueError: could not convert string to float: 'ten'`，消息里没有说是哪个配置项。

### 坑 4：dataclass 的 repr 会带出密钥

```python
@dataclass(frozen=True)
class Leaky:
    api_key: str
```

```text
repr(Leaky("sk-test-0123..."))               →  Leaky(api_key='sk-test-0123...')
raise ValueError(f"配置不对：{settings}")      →  ValueError: 配置不对：S(api_key='sk-test-0123...')
```

Day18 说「不要打印密钥」，可是你不一定会直接打印它。日志里一句 `logger.info("配置：%s", settings)`、一条把对象拼进去的报错消息，密钥就进了日志文件，而日志会被收集、转发、长期保存。`field(repr=False)` 让 `api_key` 不出现在 `repr` 里，其他字段照常显示：

```text
Settings(base_url='https://scores.example.com', timeout=5.0, retries=3, debug=False)
```

它只管 `repr`，`settings.api_key` 照样能读到，`vars(settings)` 里也还有。它防的是「不小心打印出来」，不是加密。

### 坑 5：`.env` 文件的几个写法

用 `dotenv_values` 实测（python-dotenv 1.2.4）：

```text
INLINE=value # 注释         →  'value'           # 前面有空格才算注释
HASH=abc#def                →  'abc#def'
QUOTED="a # b"              →  'a # b'
export EXP=yes              →  'yes'              export 前缀会被去掉
URL=http://${HOST}/api      →  'http:///api'      HOST 定义在下一行，展开时还是空的
```

最后一条值得记住：`${...}` 只能引用前面已经出现过的变量，否则会被换成空字符串，不报错。

### 典型初稿会被哪些测试抓住

```text
FAILED test_p10_defaults                 末尾的 / 要去掉
FAILED test_p10_debug_words[1/yes/On]    （3 条）
FAILED test_p10_required[empty/spaces]   （4 条）API_KEY= 没有被当成缺失
FAILED test_p10_bad_values               （8 条）没有校验范围；转换失败抛的是普通 ValueError
FAILED test_p10_all_problems_at_once
FAILED test_p10_secret_not_in_repr       密钥出现在了 "Settings(api_key='sk-test-…', …)" 里
FAILED test_p10_secret_not_in_error
19 failed, 13 passed
```

## 复盘

::: tip 这题用到的
- **环境变量只有字符串**：数字、布尔值都要自己转，转不了要报错，报错要写出是哪一项、什么值
- **空值也是没设**：`KEY=` 时 `os.getenv("KEY", 默认)` 返回 `""`，默认值不生效
- **布尔值认几种明确的写法**，认不出来就报错，不要悄悄当成 `False`
- **一次报全**：把问题收集到列表里，最后统一抛出
- **`field(repr=False)`**：密钥不进 `repr`，打印、日志、报错消息都不会带出来
- **函数接收 `environ` 参数**，而不是在里面读 `os.environ`：调用方决定配置从哪来，测试不用改真的环境变量
:::

现在配置只有一个来源。下一题有三套环境（开发、测试、生产），每套一个 `.env` 文件，再加上部署平台注入的环境变量，谁覆盖谁？

## 自测

1. `.env` 里写了 `TIMEOUT=`，`float(os.getenv("TIMEOUT", "5"))` 的结果是什么？
2. `DEBUG=ture`（拼错了）用 `os.getenv("DEBUG", "false").lower() == "true"` 判断，结果是什么？为什么说这比直接报错更糟？
3. `@dataclass` 里的 `api_key: str = field(repr=False)` 能防止什么？不能防止什么？

<details>
<summary>参考答案</summary>

1. 抛 `ValueError: could not convert string to float: ''`。变量存在、值是空字符串，`os.getenv` 的默认值不生效，拿到的是 `""`。
2. 结果是 `False`。拼写错误被悄悄当成了「关闭调试」，没有任何提示，你会以为配置生效了。直接报错的话，启动时就能发现写错了。
3. 能防止打印对象、把对象拼进日志或报错消息时带出密钥。不能防止直接访问 `settings.api_key`、`vars(settings)` 或者有人专门把它打印出来，它不是加密。

</details>

</Reveal>
