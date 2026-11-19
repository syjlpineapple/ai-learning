# Day 19 · 多环境配置与加载优先级

> **学习日** 2026-11-04（14:04 - 16:45，6 版迭代）
> **对应代码** [`dailypractice/Day19/`](../../../dailypractice/Day19/)（`config.py` 与三个 `.env.*` 文件）
> **原始对话** `courseware/_raw/markdown/08_Python每日练习出题 (1).md`（对话里称「Day 19」）

> Day18 单环境 → **Day19 多环境** → Day20 `APIClient` 类。

## 本节掌握

- 为什么需要多环境配置
- `APP_ENV` 约定，以及它自己从哪里来
- **两段式加载**：先通用 `.env`，再环境专属 `.env.{env}`
- **`override` 决定谁覆盖谁**——这是本节的核心设计选择
- **环境变量读出来永远是字符串**，`bool("false")` 是 `True`
- 环境名白名单校验、配置文件存在性检查
- 为什么生产环境不能默认开 Debug

---

# 第一部分 · 知识讲解

## 1. 为什么需要多环境配置

同一个应用在不同阶段需要不同配置：

| 配置项 | 开发环境 | 测试环境 | 生产环境 |
|---|---|---|---|
| API 地址 | 开发 API | 测试 API | 正式 API |
| 数据库 | 本地库 | 测试库 | 生产库 |
| Debug | True | True | **False** |
| API Key | 开发密钥 | 测试密钥 | 正式密钥 |

如果配置写死在代码里，会有两个后果：**切换环境要改代码**，以及更危险的——**容易把测试配置误用到生产，或者把生产密钥带到本地**。

目标是：代码一份不变，靠一个环境变量决定加载哪套配置。

## 2. `APP_ENV` 约定

```python
app_env = os.getenv("APP_ENV", "development")
```

三个约定值：

```text
development   开发
testing       测试
production    生产
```

这个命名是社区惯例（Django、Rails、Node 生态都类似），用全称而不是 `dev` / `prod` 缩写，因为缩写容易写错且不同项目的缩写不统一。

### `APP_ENV` 自己从哪来

这里有个容易绕进去的点：**`APP_ENV` 本身也是配置，它怎么读到？**

三种来源，按实际优先级：

1. **系统环境变量**——部署时由平台注入，这是生产环境的正路
2. **基础 `.env` 文件**——本地开发时写 `APP_ENV=development`
3. **代码里的默认值**——`os.getenv("APP_ENV", "development")` 兜底

所以加载顺序必须是：先把基础 `.env` 读进来 → 再读 `APP_ENV` → 再根据它决定加载哪个环境文件。**不能颠倒**，否则 `APP_ENV` 还没加载就被使用了。

> 默认值选 `development` 而不是 `production` 是有意的：**万一环境变量漏配，退化成开发环境比误用生产配置安全得多。** 默认值要选「出错时损害最小」的那个。

## 3. 两段式加载

```python
BASE_DIR = Path(__file__).resolve().parent

# 第一段：基础配置（含 APP_ENV）
dotenv.load_dotenv(BASE_DIR / ".env")

# 读出当前环境
env = os.getenv("APP_ENV", "development")

# 第二段：环境专属配置
env_file_path = BASE_DIR / f".env.{env}"
dotenv.load_dotenv(env_file_path, override=True)
```

目录结构：

```text
Day19/
├── .env                 通用配置 + APP_ENV
├── .env.development
├── .env.testing
├── .env.production
└── config.py
```

**分工**：`.env` 放所有环境都一样的东西（日志级别、超时时长）和 `APP_ENV`；`.env.{env}` 放因环境而异的东西（API 地址、密钥、Debug 开关）。

这样新增一个环境只要加一个文件，不动代码。

## 4. 核心：`override` 决定谁覆盖谁

两段加载里如果有同名变量，谁生效完全由 `override` 决定。

| 第二次加载的写法 | 结果 |
|---|---|
| `load_dotenv(env_file)` （默认 `override=False`） | **先加载的赢**——`.env` 的值保留，环境专属配置无效 |
| `load_dotenv(env_file, override=True)` | **后加载的赢**——环境专属配置覆盖基础配置 |

**这里必须用 `override=True`。** 因为设计意图就是「环境专属配置覆盖通用配置」，如果用默认值，`.env.production` 里的生产密钥会被 `.env` 里的通用值挡住——配置分层就失效了。

### 实测：`override=True` 的实际作用

同一个进程里连续调用两次 `load_config()`，切换环境：

```python
# 第一次：不设 APP_ENV，走默认值 development
{'app_env': 'development', 'debug': True, 'api_key': 'dev-123456', 'api_base_url': 'https://dev.demo.com'}

# 第二次：设 APP_ENV=testing
{'app_env': 'testing', 'debug': True, 'api_key': 'test-123456', 'api_base_url': 'https://test.demo.com'}
```

`api_key` 从 `dev-123456` 变成了 `test-123456`。**这个切换只有在 `override=True` 时才会发生**——第二次加载时，环境变量里已经存在 `API_KEY=dev-123456` 了（第一次加载留下的），默认的 `override=False` 会保留它，于是你会拿到开发环境的密钥却以为自己在测试环境。

> 注意这和 Day18 的结论**不矛盾**，两者是不同层面的事：
>
> - **系统环境变量 vs `.env` 文件** → 用 `override=False`，让部署注入的值优先
> - **环境专属 `.env.{env}` vs 基础 `.env`** → 用 `override=True`，让分层配置生效
>
> 所以严谨的写法是：第一段用默认（不覆盖系统变量），第二段用 `override=True`（覆盖基础文件）。
> 但这带来一个副作用——第二段的 `override=True` 也会覆盖系统环境变量。真实项目通常改用
> `pydantic-settings` 之类的库，由它统一处理「系统变量 > 环境文件 > 默认值」的优先级。

## 5. 环境变量永远是字符串

```python
debug = os.getenv("DEBUG", "false").lower() == "true"
```

为什么要这么绕？因为 **`os.getenv()` 返回的一定是字符串（或 `None`）**，`.env` 文件里写 `DEBUG=false`，读出来是字符串 `"false"`，不是布尔值 `False`。

而 Python 里**所有非空字符串都是真值**。实测：

```python
bool('true')  = True
bool('false') = True      # ← 坑在这里
bool('False') = True
bool('0')     = True
bool('no')    = True
bool('')      = False     # 只有空字符串是假值
```

所以这样写是**错的**：

```python
debug = bool(os.getenv("DEBUG"))        # DEBUG=false 时也会得到 True
```

正确做法是**显式比较字符串内容**：

```python
debug = os.getenv("DEBUG", "false").lower() == "true"
```

`.lower()` 是为了容忍 `True` / `TRUE` / `true` 三种写法。实测这份代码能正确处理 `.env.development` 里的 `DEBUG=True`（首字母大写）。

> 同理，数字也要显式转换：`timeout = int(os.getenv("TIMEOUT", "10"))`。
> 忘了转的话，`timeout` 会是字符串 `"10"`，传给 `requests` 时可能引发奇怪的类型错误。
>
> **这是「外部数据不可信」原则的又一次出现**（Day11 校验 JSON、Day12 讲类型注解不做运行时检查）。环境变量也是外部输入。

## 6. 两道防线：白名单与存在性检查

```python
if env not in ["development", "testing", "production"]:
    raise ValueError("不支持的运行环境")

env_file_path = BASE_DIR / f".env.{env}"
if not env_file_path.exists():
    raise FileNotFoundError(f"不存在的路径：{env_file_path}")
```

**白名单校验**挡住 typo。如果不校验，`APP_ENV=prodution`（少个 c）会让程序去找 `.env.prodution`，找不到就静默什么都不加载，最后报「缺少 API_KEY」——排查方向完全错了。实测设成 `staging` 会立刻抛 `ValueError`。

**存在性检查**正好修正了 Day18 的那个静默失败：`load_dotenv()` 找不到文件时只返回 `False` 不报错。这里提前用 `.exists()` 判断并抛 `FileNotFoundError`，错误信息直接带上完整路径，一眼能看出问题。

> 这两道防线体现的原则是：**配置错误要尽早、明确地失败**（fail fast）。配置问题在启动时暴露，代价是程序起不来；拖到运行时才暴露，代价可能是用错了环境的密钥。

## 7. 生产环境不要开 Debug

```env
DEBUG=false      # 生产环境必须明确设为 false
```

Debug 模式通常会输出：内部文件路径、完整的异常堆栈、配置项、SQL 语句，有时还有请求/响应的完整内容。这些信息对攻击者很有价值——路径泄露了部署结构，异常堆栈泄露了依赖版本和代码结构。

所以 `.env.production` 里 `DEBUG=False`，而且代码的默认值也是 `"false"`——**漏配时退化到安全的那一侧**。

---

# 第二部分 · 当天的练习

## 一、题目

基于 Day18 的代码做多环境配置：用 `APP_ENV` 决定加载哪个 `.env`，默认 `development`，只允许三种环境，非法则抛 `ValueError`，读取 `API_KEY` / `API_BASE_URL` / `DEBUG`，把 `DEBUG` 转成真正的布尔值，返回四项配置。

三道理解题的回答全部正确：

| 题目 | 答案 |
|---|---|
| `os.getenv("APP_ENV", "development")` 第二个参数是什么 | 默认值 |
| `os.getenv("DEBUG")` 返回什么类型 | `str` 或 `None` |
| 系统和 `.env.testing` 都有 `API_KEY`，默认用哪个 | 操作系统中的值 |

## 二、第一版：三个问题叠加成一个误导性报错

```python
BASE_DIR = Path(__file__).resolve().parent
print(BASE_DIR)
dotenv.load_dotenv(BASE_DIR)              # ① 传的是目录，不是文件

env = os.getenv("APP_ENV")                # ② 没有默认值
print(env)
if env not in ["dev", "prod"]:            # ③ 环境名和约定不一致
    raise ValueError("不支持的运行环境")
```

运行结果：

```text
D:\...\Day19
None
ValueError: 不支持的运行环境
```

**三个问题叠加，而报错信息指向了第三个。**

| 问题 | 实际后果 |
|---|---|
| ① `load_dotenv(BASE_DIR)` 传了目录 | 静默失败，什么都没加载（Day18 讲过的行为） |
| ② `os.getenv("APP_ENV")` 无默认值 | 返回 `None` |
| ③ 白名单写的是 `["dev", "prod"]` | `None` 不在里面，抛「不支持的运行环境」 |

报错说「环境不支持」，容易让人去检查 `APP_ENV` 的拼写；而真正的根因是**配置文件根本没加载进来**。

> 这是个典型的**错误信息指向下游**的案例。排查方法还是 Day11 那套：先确认每一步的实际值。
> 代码里的两个 `print` 其实已经给出了线索——`env` 打印出 `None`，说明问题在读取之前。

### 修法

```python
dotenv.load_dotenv(BASE_DIR / ".env")                    # 指到文件
env = os.getenv("APP_ENV", "development")                # 给默认值
if env not in ["development", "testing", "production"]:  # 用约定的全称
```

## 三、最终代码

```python
import os
from pathlib import Path
import dotenv

BASE_DIR = Path(__file__).resolve().parent


def load_config() -> dict[str, str | bool]:
    dotenv.load_dotenv(BASE_DIR / ".env")

    env = os.getenv("APP_ENV", "development")

    if env not in ["development", "testing", "production"]:
        raise ValueError("不支持的运行环境")

    env_file_path = BASE_DIR / f".env.{env}"
    if not env_file_path.exists():
        raise FileNotFoundError(f"不存在的路径：{env_file_path}")

    dotenv.load_dotenv(env_file_path, override=True)

    debug = os.getenv("DEBUG", "false").lower() == "true"
    api_key = os.getenv("API_KEY")
    api_base_url = os.getenv("API_BASE_URL")

    if not api_key:
        raise ValueError("API_KEY未配置")
    if not api_base_url:
        raise ValueError("API_BASE_URL未配置")

    return {
        "app_env": env,
        "debug": debug,
        "api_key": api_key,
        "api_base_url": api_base_url,
    }
```

相比 Day18 的五处进步：

- **两段式加载**，`override=True` 让分层配置真正生效
- **白名单校验**环境名
- **存在性检查**，修正了 Day18 的静默失败
- **布尔转换**用字符串比较，没掉进 `bool("false")` 的坑
- **返回类型 `dict[str, str | bool]`**，用联合类型准确表达了值有两种类型

三个环境文件（值都是假的，可以安全提交）：

```text
.env.development    API_KEY=dev-123456    API_BASE_URL=https://dev.demo.com    DEBUG=True
.env.testing        API_KEY=test-123456   API_BASE_URL=https://test.demo.com   DEBUG=True
.env.production     API_KEY=prod-123456   API_BASE_URL=https://prod.demo.com   DEBUG=False
```

## 四、现在回头看

### 一、基础 `.env` 文件不存在

实测确认 `Day19/` 下**只有三个 `.env.*`，没有基础 `.env`**。所以第一行 `load_dotenv(BASE_DIR / ".env")` 静默失败（返回 `False`）。

程序照样能跑，因为 `APP_ENV` 有默认值 `development`。**这是优雅降级，但也掩盖了一个事实：那行加载语句实际上从来没起过作用。**

要么补一个 `.env` 写上 `APP_ENV=development`，要么去掉那行并在注释里说明 `APP_ENV` 只从系统环境变量读。保持现状的话，代码的意图和实际行为不一致。

### 二、`override=True` 会连系统环境变量一起覆盖

见知识讲解第 4 节的说明。当前写法下，如果部署平台注入了 `API_KEY`，第二段加载仍会用 `.env.production` 里的值覆盖它——这和 Day18 学的「让部署注入值优先」是相反的。

小项目无妨（生产环境通常不会同时存在 `.env.production` 文件和注入的变量），但要知道这个取舍。正规做法是用 `pydantic-settings`，它内置了「系统变量 > 环境文件 > 默认值」的优先级链。

> 仓库 `README.md` 的待办里提到「学 `pydantic-settings` 的 `extra` 行为」，起因就是不了解它导致主项目配置校验失败。这条和本节是同一个主题的延续。

### 三、`load_config()` 每次调用都重新加载

和 Day18 一样的问题，但这里影响更大：由于第二段是 `override=True`，**反复调用会反复覆盖**。实测里连续调用两次能正确切换环境，看起来是好事，但也意味着：如果程序某处意外调用了 `load_config()`，当前的环境变量会被改写——这是个隐藏的全局副作用。

更稳的做法是缓存结果：

```python
from functools import lru_cache

@lru_cache(maxsize=1)
def load_config() -> dict[str, str | bool]:
    ...
```

`lru_cache` 会记住第一次的返回值，后续调用直接返回缓存，不再执行加载逻辑。

### 四、`.env.development` 开头有两个空行

无害（dotenv 会忽略空行），但不整洁。

### 五、没有 `main.py`

题目要求的 `main.py` 没有落盘，所以没有调用示例，也没有 `logging` 配置。

## 五、复习自测

1. 为什么 `APP_ENV` 的默认值应该是 `development` 而不是 `production`？
2. 两段式加载的顺序能颠倒吗？为什么？
3. 第二段加载为什么必须用 `override=True`？用默认值会怎样？
4. `bool(os.getenv("DEBUG"))` 在 `DEBUG=false` 时得到什么？正确写法是什么？
5. 只有哪一种字符串在布尔上下文里是假值？
6. `APP_ENV=prodution`（拼错）如果不做白名单校验，会发生什么？
7. `env_file_path.exists()` 这个检查修正了 Day18 的什么问题？
8. 为什么生产环境必须明确设 `DEBUG=false`？
9. `dict[str, str | bool]` 这个类型标注表达了什么？

<details>
<summary>参考答案</summary>

1. 因为默认值要选「出错时损害最小」的那个。环境变量漏配时退化成开发环境，顶多功能不对；默认成生产环境则可能误用生产密钥、操作生产数据。
2. 不能。`APP_ENV` 本身可能写在基础 `.env` 里，必须先加载它才能读到，再根据它决定加载哪个环境文件。
3. 因为设计意图是「环境专属配置覆盖通用配置」。用默认的 `override=False` 时先加载的 `.env` 会保留，环境专属文件里的值无效，配置分层就失效了。实测中第二次切换环境之所以生效，就是靠 `override=True`。
4. 得到 `True`——非空字符串都是真值。正确写法是显式比较内容：`os.getenv("DEBUG", "false").lower() == "true"`。
5. 只有空字符串 `""`。`"false"`、`"0"`、`"no"` 在布尔上下文里全都是真值。
6. 程序会去找 `.env.prodution`，`load_dotenv()` 找不到就静默返回 `False`，最终报「缺少 API_KEY」——错误信息指向配置项缺失，而真因是环境名拼错了。
7. 修正了 `load_dotenv()` 找不到文件时静默返回 `False`、不报错的问题。提前检查并抛出带完整路径的 `FileNotFoundError`，让配置错误立刻且明确地暴露。
8. Debug 模式会输出内部路径、完整异常堆栈、配置项、SQL 等信息，这些会泄露部署结构和代码细节。
9. 返回的字典键是字符串，值可能是字符串**或**布尔值（`debug` 是 `bool`，其余三项是 `str`）。比裸 `dict` 精确。

</details>
