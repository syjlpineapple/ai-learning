---
kind: problem
outline: [2, 2]
time: 45 分钟
uses: [APP_ENV, 分层合并, dotenv_values, 系统环境变量优先]
record:
  - text: Day18 override=False
    link: https://github.com/syjlpineapple/ai-learning/blob/main/courseware/records/python/Day18.md
  - text: Day19 两段式加载
    link: https://github.com/syjlpineapple/ai-learning/blob/main/courseware/records/python/Day19.md
---

# 第 11 题 · 多环境配置

同一份代码要在三个地方跑：你的电脑（开发）、测试服务器、正式服务器（生产）。地址和密钥各不相同，靠一个 `APP_ENV` 决定用哪套。Day19 做过一遍，用的是 `load_dotenv` 两段式加载加 `override=True`，课件「回头看」里已经指出它会覆盖部署平台注入的变量。这一题换一种做法，把所有来源读成字典自己合并，不去改 `os.environ`。

## 题目

一个配置目录里可能有这些文件：

```text
.env                 所有环境共用，也可以在这里写 APP_ENV
.env.development     各环境自己的，至少要有当前环境这一个
.env.testing
.env.production
.env.local           只在你自己电脑上的真实密钥，不提交到 git（可选）
```

打开 [`code/m06_config/p11_layers_exercise.py`](../../code/m06_config/p11_layers_exercise.py)，实现两个函数：

| 函数 | 做什么 |
|---|---|
| `merge_layers(config_dir, environ)` | 合并所有来源，返回 `(环境名, 合并后的值, 每个值来自哪里)` |
| `load_for(config_dir, environ)` | 合并之后交给第 10 题的 `load_settings`，返回 `(环境名, Settings)` |

**要求**

1. **环境名**：系统环境变量里的 `APP_ENV` > `.env` 里的 `APP_ENV` > 默认 `development`。不分大小写、忽略首尾空格；不是三个环境之一就抛 `ConfigError`，消息写出原来的值
2. 当前环境的 `.env.{环境名}` 必须存在，否则抛 `ConfigError`，消息写出路径
3. **优先级**从低到高：`.env` < `.env.{环境名}` < `.env.local` < 系统环境变量。系统环境变量只合并文件里出现过的、以及 `KNOWN_KEYS` 里的那几个（`os.environ` 里还有 `PATH` 等几百个无关的）
4. **不修改 `os.environ`**；第三个返回值记录每个值来自哪里：文件名（比如 `".env.testing"`）或者 `"环境变量"`
5. `load_for`：生产环境开了 `DEBUG` 要抛 `ConfigError`，并写明 `DEBUG` 来自哪里

**验证**（在 `code/` 目录下）

```powershell
pytest tests/test_m06.py -k p11 -v
```

现在是 `21 passed, 18 skipped`，全部做完是 `39 passed`。

::: details 提示：要求 4，测试说 os.environ 被改了
`load_dotenv` 的工作就是把文件内容写进 `os.environ`。同一个库里还有一个函数，只读文件、返回字典，不碰 `os.environ`。
:::

::: details 提示：要求 3，怎么让后面的覆盖前面的
按优先级从低到高排好，一层一层地往同一个字典里写。后写的自然覆盖先写的，「来自哪里」也跟着一起更新。
:::

<Reveal>

## 讲评

### 参考答案

```python
def merge_layers(config_dir, environ):
    base = read_file(config_dir / ".env")              # read_file 用的是 dotenv_values

    raw_env = environ.get("APP_ENV") or base.get("APP_ENV") or "development"
    env = raw_env.strip().lower()
    if env not in ENVIRONMENTS:
        raise ConfigError(f"APP_ENV 只能是 {'、'.join(ENVIRONMENTS)}，实际是 {raw_env!r}")
    env_file = config_dir / f".env.{env}"
    if not env_file.is_file():
        raise ConfigError(f"找不到 {env} 环境的配置文件：{env_file}")

    layers = [(".env", base),
              (env_file.name, read_file(env_file)),
              (".env.local", read_file(config_dir / ".env.local"))]
    values, sources = {}, {}
    for name, layer in layers:                         # 从低到高，后写的覆盖先写的
        for key, value in layer.items():
            values[key] = value
            sources[key] = name
    for key in sorted(set(values) | set(KNOWN_KEYS)):  # 系统环境变量最后写，永远赢
        if key in environ:
            values[key] = environ[key]
            sources[key] = "环境变量"
    ...
```

完整代码见 [`p11_layers_solution.py`](../../code/m06_config/p11_layers_solution.py)。

### 坑 1：`load_dotenv` 改的是整个进程

Day19 的做法是 `load_dotenv(".env")`，再 `load_dotenv(f".env.{env}", override=True)`。`load_dotenv` 把文件内容写进 `os.environ`，写进去就一直在。

同一个进程里先读 development、再读 testing（不带 `override`）：

```text
load_dotenv(".env.development"); load_dotenv(".env.testing")
API_KEY   →  'dev-key'       testing 的值没生效，因为 API_KEY 已经存在了
DEV_ONLY  →  '1'             只在 development 里的变量，读 testing 时还在
```

典型初稿照着 Day19 的写法做了一份。跑测试时，**前一个测试写进进程的值，跑到了后一个测试里**：

```text
FAILED test_p11_app_env_from_base_file   assert 'production' == 'testing'
FAILED test_p11_load_for                 timeout 是 3.0，应该是 8.0
```

这两个测试本身没问题。`APP_ENV=production` 和 `TIMEOUT=3` 是之前一个测试读 `.env.production` 时写进 `os.environ` 的，一直留到了现在。实测用 `-k` 单独跑这两个测试，都能通过。**测试的结果取决于运行顺序**，这是最难查的一类问题。

参考答案用 `dotenv_values`：它只读文件，返回一个字典，`os.environ` 一点都不动。合并的规则在自己的代码里写清楚，测试之间也互不影响。

### 坑 2：`override=True` 会盖掉部署平台注入的值

```text
os.environ["API_KEY"] = "injected-by-platform"     （部署平台在启动程序时注入）
load_dotenv(".env.production", override=True)
API_KEY  →  'from-file'
```

Day18 的结论是「系统环境变量优先，让部署注入的密钥赢」，Day19 为了让环境文件覆盖基础文件改用了 `override=True`，结果把注入的值也覆盖了。两个结论放在 `load_dotenv` 上很难同时满足，因为它只有一个 `override` 开关，管不了「谁覆盖谁」这么细。自己合并字典就没有这个问题：系统环境变量放在最后一层写，永远赢。

`sources` 的用处也在这里：`.env` 改了却不生效时，看一眼 `sources["API_KEY"]` 是不是 `"环境变量"`，就知道是系统里有一个同名变量挡住了它。

### 坑 3：环境名的写法

```text
APP_ENV=Production       Day19 的写法报「不支持的运行环境」
APP_ENV= production      同上
APP_ENV=prodution        报错，但消息里没有写出这个拼错的值
```

部署平台的配置界面里，`Production` 这种首字母大写的写法很常见。参考答案先 `.strip().lower()` 再比较，报错时用 `!r` 写出原值，`'prodution'` 一眼就能看出少了个 `c`。

### 坑 4：`load_dotenv()` 不传路径时从哪找

Day18 讲义说「不传路径时从当前工作目录开始找」。实测 python-dotenv 1.2.4 的行为不是这样：

```text
proj/.env、other/.env、proj/src/main.py 里调 load_dotenv()
在 proj/ 下运行        →  读到 proj/.env
在 proj/src/ 下运行    →  读到 proj/.env
在 other/ 下运行       →  读到 proj/.env        不是 other/.env
python -c "..." 在 other/ 下  →  读到 other/.env
```

它从**调用 `load_dotenv` 的那个 `.py` 文件所在的目录**开始往上找，和你在哪里敲命令无关。只有在没有脚本文件的时候（`python -c`、交互模式），或者在调试器里运行时，才从当前目录开始。所以「换个目录启动就找不到 `.env`」这个说法不准确，但「显式写出路径」的建议仍然是对的：调试和正常运行时的查找起点不一样，这种差别很难排查。

### 坑 5：`load_dotenv` 返回 `False` 不等于「文件不存在」

```text
load_dotenv("不存在.env")   →  False
load_dotenv(目录)           →  False
load_dotenv(空文件)         →  False
```

Day18 讲义建议「返回 `False` 时记一条『未找到 .env 文件』」，空文件也会触发这条，措辞不准。要判断文件在不在，用 `Path.is_file()`，参考答案就是这样做的。

## 复盘

::: tip 这题用到的
- **优先级**：`.env` < `.env.{环境名}` < `.env.local` < 系统环境变量。按从低到高的顺序写进同一个字典，后写的覆盖先写的
- **`dotenv_values` 只读文件不改进程**；`load_dotenv` 写进 `os.environ`，一个进程里会残留，测试之间会互相污染
- **系统环境变量永远赢**：部署平台注入的密钥不能被仓库里的文件覆盖
- **记录每个值的来源**，配置不生效时一眼看出是谁覆盖了谁
- **环境名先归一化再比较**，报错写出原值；当前环境的文件必须存在
- **生产环境禁止 DEBUG**，在启动时就拦住
- **`.env.local` 放真实密钥**，不提交；仓库里只放假值或 `.env.example` 模板
:::

M6 到这里就结束了。下一个模块 M7 把配置、HTTP 请求、重试组合成一个 `APIClient` 类，对应学习记录 Day20。

## 自测

1. 同一个进程里先 `load_dotenv(".env.development")`，再 `load_dotenv(".env.testing")`，`API_KEY` 是哪个环境的？为什么？
2. 部署平台注入了 `API_KEY`，程序又执行了 `load_dotenv(".env.production", override=True)`，最后用的是哪个密钥？
3. 用 `load_dotenv` 的配置代码，测试为什么会「单独跑能过、一起跑就失败」？

<details>
<summary>参考答案</summary>

1. development 的。第一次加载已经把 `API_KEY` 写进了 `os.environ`，第二次默认 `override=False`，已存在的变量不会被覆盖。而且只在 development 里出现的变量也会一直留着。
2. 文件里的。`override=True` 会覆盖所有已存在的环境变量，包括部署平台注入的那个。
3. `load_dotenv` 把值写进了 `os.environ`，测试结束后不会恢复。前一个测试写进去的 `APP_ENV`、`TIMEOUT` 等，会被后一个测试读到，结果取决于测试的运行顺序。用 `dotenv_values` 读成字典、不改 `os.environ`，就没有这个问题。

</details>

</Reveal>
