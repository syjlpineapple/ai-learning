---
kind: lesson
outline: [2, 2]
time: 40 分钟
uses: [os.getenv, .env 与 load_dotenv, "Path(__file__).resolve()", override, .gitignore]
record:
  - text: 当时的代码 Day18/
    link: https://github.com/syjlpineapple/ai-learning/tree/main/dailypractice/Day18
---

# Day 18：环境变量与密钥

调大模型 API 要带一个密钥，长得像 `sk-xxxxxxxx`。最省事的写法是直接写进代码：

```python
API_KEY = "sk-123456789"      # 千万别这样
```

能跑，但代码一推到 GitHub，所有人都看得见。有程序专门扫公开仓库里的密钥，别人拿你的密钥调接口，账单算你的。而且 Git 会保留历史，事后删掉这一行，旧提交里还在。

所以密钥要放在代码**外面**，运行时再读进来。今天学怎么读。

> 如果密钥已经泄露了，正确做法是马上到服务商后台**撤销旧密钥、生成新的**。只删代码、或者把仓库改成私有，都不算数。

## 一、环境变量和 `os.getenv()`

环境变量是操作系统交给程序的一组「名字 = 值」。Python 用 `os.getenv()` 读：

```python
print(os.getenv("PE_NOT_SET"))
print(os.getenv("PE_NOT_SET", "fallback"))
try:
    os.environ["PE_NOT_SET"]
except KeyError as e:
    print("KeyError:", e)
```

```text
None
fallback
KeyError: 'PE_NOT_SET'
```

- 变量不存在时 `os.getenv()` 返回 `None`，**不报错**，所以要自己检查，缺了就 `raise ValueError(...)`
- 第二个参数是默认值，适合可选的配置
- `os.environ["名字"]` 缺了直接抛 `KeyError`

密钥读进来可以用，但**不要打印，也不要写进日志**。日志会被收集、转发、长期保存，密钥进了日志就等于扩散了。只打印「读取成功」。

## 二、`.env` 文件：`load_dotenv()` 搬进来，`os.getenv()` 取出来

每次手动设环境变量太麻烦，本地开发通常写一个 `.env` 文件（等号两边不加空格）：

```text
API_KEY=your_secret_key
API_BASE_URL=https://api.example.com
```

再装 `python-dotenv`（`pip install python-dotenv`），用 `load_dotenv()` 把文件里的内容加载进环境变量。

这一点你当天专门问过：**`os.getenv()` 不会自己去读 `.env`。** 实测，`.env` 里写了 `PE_API_KEY`，没调 `load_dotenv()` 就读：

```text
None
```

`load_dotenv()` 还有个返回值，找到文件返回 `True`，没找到返回 `False`，**不报错**：

```python
print(load_dotenv(Path(d) / "no_such.env"))
print(load_dotenv(env_file))
print(os.getenv("PE_API_KEY"))
```

```text
False
True
key-from-dotenv
```

路径写错了它也一声不吭，问题要等到后面 `os.getenv()` 拿到 `None` 才冒出来，报的还是「缺少 API_KEY」，很容易以为是 `.env` 里漏写了。

## 三、不传路径时，它去哪儿找 `.env`

> 注意：当天讲的是「从当前工作目录开始找」，实测（python-dotenv 1.2.4）不是这样。我在 `proj/` 和启动目录 `elsewhere/` 下各放了一个 `.env`，脚本 `proj/src/main.py` 里只写一句 `load_dotenv()`：

```text
从 elsewhere 启动 -> True proj 根目录的 .env
从 proj 启动 -> True proj 根目录的 .env
从 proj\src 启动 -> True proj 根目录的 .env
删掉 proj/.env，从 elsewhere 启动 -> False None
```

不管从哪里启动，读到的都是 `proj/.env`；把它删了，启动目录里那个 `.env` 也不会被读到。也就是说，它是从**调用 `load_dotenv()` 的那个 `.py` 文件所在的目录**开始，一层层往上找。

那为什么还要指定路径？因为「一层层往上找」本身就不可控：哪个文件调用它、上面几层碰巧有没有别的 `.env`，都会影响结果。明确写出来最稳：

```python
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")
```

`__file__` 是当前 `.py` 文件的路径，`.resolve()` 变成绝对路径，`.parent` 往上一层。层数要数准，用当天那道练习题验证：

```python
p = PurePosixPath("project/app/config/settings.py")
print(p.parent)
print(p.parent.parent)
print(p.parent.parent.parent)
print(p.parents[2])
```

```text
project/app/config
project/app
project
project
```

`parents[2]` 等于连着三次 `.parent`，层数多的时候用它更不容易数错。

## 四、`override=False`：系统里的值优先

如果操作系统里已经有这个变量，`.env` 里的同名值**默认不覆盖它**：

```python
os.environ["PE_BOTH"] = "value-from-os"       # 模拟部署平台已经注入
load_dotenv(env_file)                         # .env 里写的是 PE_BOTH=value-from-dotenv
print(os.getenv("PE_BOTH"))
load_dotenv(env_file, override=True)
print(os.getenv("PE_BOTH"))
```

```text
value-from-os
value-from-dotenv
```

这个默认值是故意的：上线时正式密钥由平台注入，万一服务器上残留了一份 `.env`，也不会把它覆盖掉。反过来，本地改了 `.env` 不生效时，先查查系统里是不是有个同名变量挡着。

## 五、`.gitignore`

把 `.env` 写进 `.gitignore`，Git 就不会提交它。但有个坑：**`.gitignore` 只对还没被 Git 跟踪的文件起作用。** 如果 `.env` 已经 `git add` 过，得 `git rm --cached .env` 才能停止跟踪，而且历史提交里那份密钥依然在。

常见做法是提交一份 `.env.example`，只写变量名和假值，告诉别人要配哪些东西。

## 六、今天的作业

写一个配置读取模块 `config.py`：

1. 用 `python-dotenv` 加载 `.env`，`.env` 里配 `API_KEY` 和 `API_BASE_URL`
2. `load_config()` 用 `os.getenv()` 读取
3. 缺少 `API_KEY` 时抛 `ValueError`
4. 正常时返回包含两项配置的字典
5. `main.py` 里调用，**只打印是否读取成功，不打印密钥**

## 七、小测

**1.** `os.getenv("API_KEY")` 在变量不存在时返回什么？

- A. 空字符串
- B. `None`
- C. 抛 `KeyError`

**2.** `.env` 里有 `API_KEY=abc123`，程序没调 `load_dotenv()`，系统里也没设，`os.getenv("API_KEY")` 是什么？

- A. `abc123`
- B. `None`
- C. 报错

**3.** `api_client.py` 需要 API Key，`config.py` 已经负责加载 `.env`，最推荐怎么拿？

- A. 每个模块都调一次 `load_dotenv()`
- B. 从 `config.py` 导入
- C. 每个模块自己读 `.env` 文件

<details>
<summary>答案</summary>

1. B。
2. B。`os.getenv()` 只读环境变量，不碰文件。
3. B。读取和校验只写一份，以后换配置来源也只改一个文件。

</details>

## 讲评（11-04）

路径题（`project/app/`）和配置管理题（B）你都答对了。答路径题时你没有被「两次 `.parent`」绕晕，一层一层数出来了。动手之前你还连着问了两个问题：「需要先 `load_dotenv()` 才能用 `os.getenv` 吗」「`load_dotenv()` 对哪里的 `.env` 生效」。第二个问题问得好，第三节就是它的实测答案。

代码第一版：

```python
def load_config():
    dotenv.load_dotenv()

    api_key = os.getenv("API_KEY_TEST")
    api_base_url = os.getenv("API_BASE_URL")
    if not api_key:
        raise ValueError("缺少API_KEY_TEST")
    if not api_base_url:
        raise ValueError("缺少API_BASE_URL")

    return { "api_key":api_key, "api_base_url":api_base_url }
```

两项配置都做了缺失检查，没有打印密钥，主线是对的。GPT 建议的两处改动你都收下了：用 `Path(__file__).resolve().parent` 指定 `.env` 的位置，返回类型标成 `dict[str, str]`。最终的 `day_18.py` 跑起来：

```text
读取成功 ['api_base_url', 'api_key']
```

回头看还有两处：

- 变量名用了 `API_KEY_TEST`。带 `_TEST` 后缀，等于把「这是测试用的」写死在了代码里，换到正式环境就得改代码。名字应该保持 `API_KEY` 不变，用不同的 `.env` 文件区分环境，这正是明天的内容。
- 没检查 `load_dotenv()` 的返回值。路径错了它返回 `False`，最后报的却是「缺少 API_KEY_TEST」。可以在报错里带上路径：`raise ValueError(f"缺少 API_KEY_TEST（已尝试加载 {ENV_PATH}）")`。

## 加练

[读配置](加练/day18_读配置.md)：把地址、密钥、超时、调试开关从环境变量读成一个类型正确、校验过的 `Settings` 对象，缺了的、格式不对的一次全报出来，打印对象时还不能露出密钥。
