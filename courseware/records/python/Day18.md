# Day 18 · 环境变量、.env 与密钥安全

> **学习日** 2026-11-04（10:51 - 11:44，5 轮对话）
> **对应代码** [`dailypractice/Day18/day_18.py`](../../../dailypractice/Day18/day_18.py) 与 `Day18/.env`
> **原始对话** `courseware/_raw/markdown/03_Python每日练习出题.md`（对话里称「第 18 天」）

> A 线从这里进入配置管理。Day18 单环境 → Day19 多环境 → Day20 `APIClient` 类。

## 本节掌握

- 为什么 API Key 绝不能写进代码
- `os.getenv()` 的行为，包括第二个参数（默认值）
- `load_dotenv()` 和 `os.getenv()` 的分工——**后者不会主动读 `.env`**
- `.env` 的查找规则：当前工作目录和脚本目录不是一回事
- `Path(__file__).resolve().parent` 逐层拆解
- **`override=False` 默认规则**：系统环境变量优先于 `.env`
- **`load_dotenv()` 找不到文件时不报错**，只返回 `False`
- `.gitignore`，以及「已被跟踪的文件加 gitignore 没用」这个坑
- 配置集中管理：`load_dotenv()` 该放在哪

---

# 第一部分 · 知识讲解

## 1. 为什么密钥不能写进代码

```python
API_KEY = "sk-123456789"        # 绝对不要这样
```

三个风险：

1. **泄露**：代码推到 GitHub 后，任何人都能看到。自动爬虫专门扫描公开仓库里的密钥，通常几分钟内就会被发现。
2. **费用**：别人用你的密钥调用 API，账单是你的。
3. **难以收回**：Git 会保留历史。即使后来删掉那一行，密钥仍在历史提交里——**改代码不等于撤销密钥**。

所以密钥要放在代码之外，通过环境变量读入。

> 如果密钥已经泄露，正确做法是**立刻到服务商后台撤销旧密钥、生成新的**。只删代码、或者把仓库改成私有，都无效——密钥可能已经被抓取。

## 2. 环境变量与 `os.getenv()`

环境变量是操作系统提供给进程的配置信息。

```python
import os

api_key = os.getenv("API_KEY")
```

两个要点：

**一、不存在时返回 `None`，不抛异常。** 所以必须自己检查：

```python
if not api_key:
    raise ValueError("缺少 API_KEY 环境变量")
```

**二、第二个参数是默认值：**

```python
os.getenv("NOT_SET")              # None
os.getenv("NOT_SET", "fallback")  # 'fallback'
```

这对可选配置很方便，比如 `os.getenv("APP_ENV", "development")`——没设就用开发环境。

> `os.environ["API_KEY"]` 是另一种写法，但它在变量不存在时抛 `KeyError`。想要「缺了就立刻报错」用它，想要「缺了给默认值」用 `os.getenv()`。

**不要打印密钥。** 读取和使用都可以，但不要输出到终端或日志——日志经常被收集、转发、长期存储，密钥一旦进了日志系统就等于扩散了。只打印「是否读取成功」。

## 3. `.env` 文件与 python-dotenv

每次手动设置环境变量太麻烦，所以本地开发常用 `.env` 文件：

```bash
pip install python-dotenv
```

`.env` 的内容：

```text
API_KEY=your_secret_key
API_BASE_URL=https://api.example.com
```

格式要点：**等号两边不加空格**，一行一个，不用引号（除非值里有空格）。

### `load_dotenv()` 和 `os.getenv()` 的分工

这是当时的第一个追问，很关键：

| 函数 | 做什么 |
|---|---|
| `load_dotenv()` | 读 `.env` 文件，把里面的内容**加载进当前进程的环境变量** |
| `os.getenv()` | 从**当前进程的环境变量**里读 |

**`os.getenv()` 不会主动去读 `.env` 文件。** 所以：

- 如果环境变量已经由操作系统设置（`export API_KEY=xxx`），直接 `os.getenv()` 就行，不需要 `load_dotenv()`
- 如果配置只写在 `.env` 里，必须先 `load_dotenv()`，否则 `os.getenv()` 返回 `None`

记法：**`load_dotenv()` 负责「搬进来」，`os.getenv()` 负责「取出来」。**

## 4. `.env` 在哪里被找到

这是当时的第二个追问，也是最容易出错的地方。

```python
load_dotenv()        # 不传路径
```

> **更正（2026-11-19）**：下面这句是当时的讲法，实测不对。python-dotenv 1.2.4 下，`load_dotenv()` 不传路径时，是从**调用它的那个 `.py` 文件所在的目录**开始往上找，和你从哪个目录启动无关（在 `python -c` 或交互式环境里调用时才用当前工作目录）。实测过程见课文 [Day 18](../../ai/2_网络请求与配置/day18_环境变量与密钥.md) 第三节。复习自测第 5 题的答案同样按此更正。

不传路径时，它从**当前工作目录**开始找，并可能向上层目录查找。这里有两个容易混的概念：

| 概念 | 含义 |
|---|---|
| **当前工作目录（CWD）** | 你**敲命令时所在的目录** |
| **脚本所在目录** | `.py` 文件实际存放的目录 |

**这两个目录经常不一样。** 比如项目结构是：

```text
my_project/
├── .env
└── src/
    └── main.py
```

在 `my_project/` 下执行 `python src/main.py`，CWD 是 `my_project/`，能找到 `.env`；
但如果 `cd src` 之后执行 `python main.py`，CWD 变成了 `my_project/src/`，`.env` 就可能找不到。

**同一份代码，换个目录启动，行为就不同**——这类问题极难排查，因为代码没变。

### 解法：显式指定绝对路径

```python
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")
```

逐层拆解：

| 代码 | 得到什么 |
|---|---|
| `__file__` | 当前这个 `.py` 文件的路径 |
| `Path(__file__)` | 转成 `Path` 对象 |
| `.resolve()` | 转成规范化的**绝对路径**（展开符号链接和 `..`） |
| `.parent` | 它所在的目录 |
| `.parent.parent` | 再上一层 |
| `/ ".env"` | 拼接出 `.env` 的完整路径 |

**关键在于 `__file__` 是相对于文件自身的，和你从哪里启动程序无关。** 所以这种写法稳定。

层数要数准。当时的练习题：

```text
project/
├── .env
└── app/
    └── config/
        └── settings.py
```

在 `settings.py` 里 `Path(__file__).resolve().parent.parent` 指向哪？

答案是 `project/app/`：`.resolve()` 得到文件路径 → 第一个 `.parent` 得到 `config/` → 第二个 `.parent` 得到 `app/`。要定位到 `project/`（`.env` 所在处）得再上一层，也就是三次 `.parent`。

等价的简写是：

```python
BASE_DIR = Path(__file__).resolve().parents[2]      # 等于三次 .parent
```

`parents` 是个序列，`parents[0]` 就是 `.parent`，`parents[1]` 是 `.parent.parent`，以此类推。层数多的时候这个写法更清楚，也不容易数错。

## 5. `override=False`：系统环境变量优先

`load_dotenv()` 的默认参数是 `override=False`。含义是：**如果某个变量在操作系统里已经存在，`.env` 里的同名值不会覆盖它。**

实测验证：

```python
os.environ["BOTH_PLACES"] = "value-from-os"        # 模拟系统已设置
# .env 里写着 BOTH_PLACES=value-from-dotenv

load_dotenv(env_file)                      # 默认 override=False
os.getenv("BOTH_PLACES")                   # 'value-from-os'      ← 系统的赢了
os.getenv("FROM_ENV_FILE")                 # 'dotenv-value'       ← 只有 .env 有，所以生效

load_dotenv(env_file, override=True)       # 显式覆盖
os.getenv("BOTH_PLACES")                   # 'value-from-dotenv'  ← .env 赢了
```

**这个默认值是故意设计的，而且很有用：** 部署到服务器时，正式密钥通过系统环境变量或密钥管理服务注入；万一仓库里不小心留了一份 `.env`，它也不会覆盖掉生产配置。

反过来也要注意：本地调试时改了 `.env` 却不生效，有可能是系统里有同名变量把它挡住了。排查时先 `echo $env:API_KEY`（PowerShell）看一眼。

## 6. 找不到 `.env` 时不会报错

这是个容易踩的静默失败。实测：

```python
load_dotenv(tmp / "no_such.env")      # 返回 False，不抛异常
```

**路径写错了、文件名拼错了、层数数错了，`load_dotenv()` 都不会报错**，只是安静地什么都不做。问题要到后面 `os.getenv()` 返回 `None` 时才间接暴露，而那时的报错信息是「缺少 API_KEY」——很容易误以为是 `.env` 内容写错了，而真正的原因是文件根本没被读到。

防御方法是检查返回值：

```python
if not load_dotenv(BASE_DIR / ".env"):
    logger.warning("未找到 .env 文件: %s", BASE_DIR / ".env")
```

或者在配置校验的报错信息里带上路径：

```python
raise ValueError(f"缺少 API_KEY，已尝试加载 {ENV_PATH}")
```

## 7. `.gitignore` 与一个常见误解

```text
.env
__pycache__/
*.pyc
.venv/
```

**关键的坑：`.gitignore` 只对「还没被 Git 跟踪」的文件生效。**

如果 `.env` 已经 `git add` 过，后来再写进 `.gitignore`，Git 仍然会继续跟踪它的改动。要取消跟踪得显式操作：

```bash
git rm --cached .env
```

而且这只是停止跟踪——**之前的提交历史里仍然有那份密钥**。真正泄露过的密钥必须去服务商后台撤销。

> 这个仓库的实践可以对照看：`Day19`/`Day20` 下的 `.env.development` 等文件**是故意提交的**，因为里面是 `dev-123456` 这类假值，仅用于演示多环境加载顺序。而真实密钥一律写进 `.env.local`，它在根目录 `.gitignore` 里。
>
> 这是个值得学的模式：**提交「结构示例」，忽略「真实值」**。很多项目会提交一份 `.env.example` 作为模板，让新人知道需要配哪些变量。

## 8. `load_dotenv()` 放在哪里

三种方式，适用场景不同：

### 方式 1：放在 `main.py`

```python
load_dotenv()
api_key = os.getenv("API_KEY")
```

简单直观，适合小脚本。**风险**是：如果其他模块在 `load_dotenv()` 执行之前就读了环境变量（比如模块顶层代码），会拿到 `None`。

### 方式 2：放在 `config.py`（模块级）

```python
# config.py
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

API_KEY = os.getenv("API_KEY")
if not API_KEY:
    raise ValueError("缺少 API_KEY 配置")
```

```python
# 其他模块
from config import API_KEY
```

配置集中在一处，其他模块只管导入。注意 `from config import API_KEY` 会触发 `config.py` 的顶层代码执行（Day10 的知识），所以加载时机取决于导入时机。

### 方式 3：封装成函数（Day18 作业采用的方式）

```python
def load_config() -> dict[str, str]:
    load_dotenv(ENV_PATH)
    ...
    return {"api_key": api_key, "api_base_url": api_base_url}
```

加载时机明确（调用才加载），而且**便于测试**——可以传不同的路径、可以多次调用验证不同配置。模块级变量的方式做不到这一点，因为导入只会执行一次。

### 一条原则

**配置加载集中管理，不要让每个业务模块各自调 `load_dotenv()`。**

当时的理解题问：`api_client.py` 需要 API_KEY 时该怎么拿？答案是**从 `config.py` 导入**，而不是自己再读一遍 `.env`。理由是：读取逻辑只有一份、校验只做一次、换配置源（比如改成从密钥服务读）时只改一个文件。

## 9. 不同环境的密钥管理

| 环境 | 常见做法 |
|---|---|
| 个人开发 | `.env` 文件 |
| 团队开发 | 环境变量 + 受控的配置分发 |
| 生产部署 | 云平台的 Secret Manager / 密钥管理服务 |

`.env` 适合本地，不适合生产——生产环境通常不把密钥以明文文件形式放在服务器上，而是由平台在进程启动时注入环境变量。

这也解释了为什么 `override=False` 是对的默认值：**让部署环境的注入值始终优先。**

---

# 第二部分 · 当天的练习

## 一、题目

写一个安全的配置读取模块：用 `python-dotenv` 读 `.env`，实现 `load_config()`，用 `os.getenv()` 读取，缺少 `API_KEY` 时抛 `ValueError`，正常时返回包含两项配置的字典。**不允许打印真实 API Key**，只打印是否读取成功。

四道理解题的回答全部正确：

| 题目 | 答案 |
|---|---|
| `os.getenv('API_KEY')` 在变量不存在时返回什么 | `None` |
| `.env` 应该提交到 GitHub 吗 | 不应该 |
| `load_dotenv()` 的作用 | 读取 `.env` 并加载环境变量 |
| API Key 泄露后的正确做法 | 立即撤销旧密钥并生成新密钥 |

## 二、代码

```python
import os
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / ".env"


def load_config() -> dict[str, str]:
    load_dotenv(ENV_PATH)

    api_key = os.getenv("API_KEY_TEST")
    api_base_url = os.getenv("API_BASE_URL")

    if not api_key:
        raise ValueError("缺少 API_KEY_TEST")

    if not api_base_url:
        raise ValueError("缺少 API_BASE_URL")

    return {
        "api_key": api_key,
        "api_base_url": api_base_url,
    }
```

做对的四点：

- **显式指定 `.env` 路径**，用 `Path(__file__).resolve().parent` 定位，不依赖启动目录
- **`BASE_DIR` 和 `ENV_PATH` 提到模块级**，意图清楚，也便于别处复用
- **两个配置都做了缺失校验**，而不是只查 API_KEY
- **返回类型标注 `dict[str, str]`**，比裸 `dict` 精确（Day06 的教训）

配套的 `.env`：

```text
API_KEY_TEST=demo-key-not-a-real-secret
API_BASE_URL=https://httpbin.org
```

> 这份 `.env` 里是假值，所以可以安全地提交。仓库根目录的 `README.md` 对此有明确说明。

## 三、现在回头看

### 一、变量名和题目不一致

题目要求的是 `API_KEY`，代码用的是 `API_KEY_TEST`。两边自洽（`.env` 里也是 `API_KEY_TEST`），不影响运行。

**但带 `_TEST` 后缀这个习惯本身有个隐患**：如果将来真实环境用 `API_KEY`、测试用 `API_KEY_TEST`，那么代码就被钉死在测试配置上，切换环境得改代码。更好的做法是变量名保持一致（`API_KEY`），用**不同的 `.env` 文件**区分环境——这正是 Day19 的内容。

### 二、没有检查 `load_dotenv()` 的返回值

路径如果写错了，`load_dotenv()` 静默返回 `False`，程序继续跑到 `os.getenv()` 返回 `None`，最后报「缺少 API_KEY_TEST」。报错信息指向了「配置项缺失」，但真正的原因可能是「`.env` 文件没找到」——两件事的排查方向完全不同。

建议在报错里带上路径：

```python
raise ValueError(f"缺少 API_KEY_TEST（已尝试加载 {ENV_PATH}）")
```

### 三、每次调用都会重新 `load_dotenv()`

`load_config()` 每次被调用都执行一遍 `load_dotenv()`。功能上没问题（重复加载是幂等的），但有两点值得注意：

- 每次都读一遍文件，有微小的 IO 开销
- 由于 `override=False`，第一次加载后变量已进入环境，后续加载实际上不会改变任何值——**所以如果你在运行时改了 `.env`，重新调用 `load_config()` 也不会生效**。这个行为容易让人困惑。

### 四、没有 `main.py`

题目要求在 `main.py` 里调用并打印是否成功，这部分没有落盘。`day_18.py` 只有 `load_config()` 一个函数，没有入口代码——它是个纯模块。

## 四、复习自测

1. API Key 写进代码后又删掉，密钥就安全了吗？
2. `os.getenv("X")` 和 `os.environ["X"]` 在变量不存在时的行为有什么不同？
3. `os.getenv("APP_ENV", "development")` 的第二个参数是什么意思？
4. 只写 `os.getenv("API_KEY")`、不调用 `load_dotenv()`，而配置只在 `.env` 里，会得到什么？
5. 「当前工作目录」和「脚本所在目录」有什么区别？为什么这会影响 `load_dotenv()`？
6. `Path(__file__).resolve().parent.parent` 和 `parents[1]` 等价吗？
7. 系统环境变量和 `.env` 里有同名变量时，默认哪个生效？为什么这样设计是合理的？
8. `load_dotenv("路径写错了.env")` 会发生什么？
9. `.env` 已经被 `git add` 过，现在加进 `.gitignore` 还有用吗？
10. 为什么业务模块不该各自调用 `load_dotenv()`？

<details>
<summary>参考答案</summary>

1. 不安全。Git 保留完整历史，旧提交里仍然有那个密钥。必须到服务商后台撤销旧密钥并生成新的。
2. `os.getenv()` 返回 `None`；`os.environ["X"]` 抛 `KeyError`。想「缺了就立刻报错」用后者，想「缺了给默认值」用前者。
3. 默认值。`APP_ENV` 不存在时返回 `"development"`。
4. 得到 `None`。`os.getenv()` 只读当前进程的环境变量，不会主动去读 `.env` 文件。
5. 当前工作目录是**敲命令时所在的目录**，脚本所在目录是 `.py` 文件实际存放的位置，两者经常不同。`load_dotenv()` 不传路径时从当前工作目录开始找，所以换个目录启动，同一份代码的行为就可能不同。
6. 等价。`parents[0]` 相当于一次 `.parent`，`parents[1]` 相当于两次。层数多时用 `parents[n]` 更不容易数错。
7. 默认系统环境变量生效（`override=False`）。这样设计是为了让部署环境注入的配置始终优先，避免仓库里残留的 `.env` 覆盖生产配置。
8. 什么都不会发生——返回 `False`，不抛异常。问题要到后面 `os.getenv()` 返回 `None` 时才间接暴露，而报错信息会指向「配置项缺失」而非「文件没找到」。
9. 没用。`.gitignore` 只对尚未被跟踪的文件生效。要停止跟踪得执行 `git rm --cached .env`，而且历史提交里的密钥依然存在。
10. 因为读取逻辑会散落多处、校验重复、换配置源时要改很多文件。应该集中在一个配置模块，其他模块从它导入。

</details>
