---
kind: lesson
outline: [2, 2]
time: 45 分钟
uses: [APP_ENV, 两段式加载, override=True, 环境变量都是字符串, 白名单校验]
record:
  - text: 当时的代码 Day19/
    link: https://github.com/syjlpineapple/ai-learning/tree/main/dailypractice/Day19
---

# Day 19：多环境配置

昨天你用了 `API_KEY_TEST` 这个名字，回头看说过：「测试用」不该写进变量名，应该用不同的文件区分环境。今天就做这件事。

同一份代码要在三个地方跑：你的电脑（开发）、测试服务器、正式服务器（生产）。API 地址、密钥、要不要开调试，三处都不一样。目标是：**代码一个字不改，靠一个环境变量决定用哪套配置。**

## 一、`APP_ENV`：先决定是哪个环境

```python
env = os.getenv("APP_ENV", "development")
```

约定三个值：`development`、`testing`、`production`。用全称不用缩写，`dev`、`prod`、`test` 各项目写法不一，容易对不上。

默认值选 `development`，不选 `production`，是有意的：**万一漏配了，退回开发环境顶多功能不对，误用生产配置可能动到真实数据。** 默认值要选出错时损失最小的那个。

## 二、两段式加载

文件这样分：

```text
Day19/
├── .env                 所有环境都一样的配置，也可以写 APP_ENV
├── .env.development     API_KEY=dev-123456     DEBUG=True
├── .env.testing         API_KEY=test-123456    DEBUG=True
├── .env.production      API_KEY=prod-123456    DEBUG=False
└── config.py
```

加载分两步，顺序不能反：先读 `.env`（`APP_ENV` 可能就写在里面），再根据 `APP_ENV` 读对应的那个文件。

两个文件里都有同一个变量时，谁算数？由第二次加载的 `override` 决定。用临时文件实测：`.env` 里 `PE19_KEY=base-key`，`.env.testing` 里 `PE19_KEY=test-key`。

```python
load_dotenv(Path(d) / ".env")
env = os.getenv("APP_ENV", "development")
load_dotenv(Path(d) / f".env.{env}", override=override)
```

```text
override=False: env=testing, PE19_KEY=base-key
override=True: env=testing, PE19_KEY=test-key
```

不加 `override=True`，先读进来的 `base-key` 留着，测试环境的配置白写了。我们要的是「专属配置盖过通用配置」，所以**第二次加载要 `override=True`**。

这和昨天的结论不矛盾，是两个层面的事：

| 谁和谁比 | 用什么 | 为什么 |
|---|---|---|
| 系统环境变量 vs `.env` 文件 | `override=False`（默认） | 部署平台注入的值优先 |
| `.env.{env}` vs `.env` | `override=True` | 专属配置盖过通用配置 |

## 三、环境变量读出来都是字符串

`.env` 里写 `DEBUG=False`，读出来是字符串 `"False"`，不是布尔值。而 Python 里非空字符串都算「真」：

```text
bool('true') = True
bool('false') = True
bool('False') = True
bool('0') = True
bool('no') = True
bool('') = False
```

所以 `bool(os.getenv("DEBUG"))` 在 `DEBUG=false` 时也是 `True`。要比较内容：

```python
debug = os.getenv("DEBUG", "false").lower() == "true"
```

```text
'True' -> True
'TRUE' -> True
'false' -> False
None -> False
```

`.lower()` 让 `True`、`TRUE`、`true` 都能认；默认值 `"false"` 让没配的时候走关闭。生产环境一定要关调试：调试模式会把内部路径、完整报错、配置项打出来，这些都是给攻击者的线索。数字同理，`int(os.getenv("TIMEOUT", "10"))`，忘了转就是字符串 `"10"`。

## 四、两道防线：尽早、明确地失败

```python
if env not in ["development", "testing", "production"]:
    raise ValueError("不支持的运行环境")

env_file_path = BASE_DIR / f".env.{env}"
if not env_file_path.exists():
    raise FileNotFoundError(f"不存在的路径：{env_file_path}")
```

第一道挡拼写错误。`APP_ENV=prodution`（少个 c）如果不拦，程序会去找 `.env.prodution`，`load_dotenv()` 找不到也不报错（昨天实测过），最后报「缺少 API_KEY」，排查方向全错。

第二道补的正是昨天那个「找不到文件也不报错」，错误信息里直接带上完整路径，一眼就能看出问题。

配置有问题，就在启动时报出来。程序起不来，好过带着错误的密钥跑起来。

## 五、今天的作业

在昨天的基础上写多环境配置：

1. 用 `APP_ENV` 决定加载哪个 `.env.*`，默认 `development`
2. 只允许三种环境，否则抛 `ValueError`
3. 读 `API_KEY`、`API_BASE_URL`、`DEBUG`，前两个缺了抛 `ValueError`
4. `DEBUG` 转成真正的布尔值
5. 封装成 `load_config()`，返回四项配置的字典

## 六、小测

**1.** `os.getenv("DEBUG")` 返回什么类型？

- A. `bool`
- B. `int`
- C. `str` 或 `None`

**2.** 系统里设了 `API_KEY`，`.env.testing` 里也有 `API_KEY`，默认的 `load_dotenv()` 用哪个？

- A. `.env.testing` 里的
- B. 系统里的

**3.** `.env` 里 `APP_ENV=testing`、`API_KEY=base-key`，`.env.testing` 里 `API_KEY=test-key`，第二次加载写了 `override=True`，最后 `API_KEY` 是？

- A. `base-key`
- B. `test-key`
- C. `None`

<details>
<summary>答案</summary>

1. C。环境变量没有类型，全是字符串。
2. B。默认 `override=False`，不覆盖已经存在的值。
3. B。

</details>

## 讲评（11-04）

最后那道题你答的是「选 test-key，会被覆盖」，对。代码改了好几版，第一版的运行结果最值得看：

```text
D:\Lee\AICODE\sell-gen\backend\tests\dailypractice\Day19
None
Traceback (most recent call last):
  File "D:\Lee\AICODE\sell-gen\backend\tests\dailypractice\Day19\config.py", line 13, in <module>
    raise ValueError("不支持的运行环境")
ValueError: 不支持的运行环境
```

报错说「环境不支持」，可问题其实有三个，叠在一起：

1. `load_dotenv(BASE_DIR)` 传的是**目录**，不是文件。整理时实测，传目录返回 `False`，什么都没加载，也不报错
2. `os.getenv("APP_ENV")` 没给默认值，于是是 `None`
3. 白名单写的是 `["dev", "prod"]`，`None` 不在里面

报错指向的是第 3 个，根子却在第 1 个。好在你打印了 `env`，看到 `None` 就说明问题出在读取之前。这类「错误信息指向下游」的情况，办法还是 Day 11 那一套：一步一步看实际的值。

后面几版陆续改对：环境名用全称、给默认值、`DEBUG` 加了 `"false"` 默认值（之前 `os.getenv("DEBUG").lower()` 在没配 `DEBUG` 时会对 `None` 调 `.lower()` 报错）、去掉了 `print(API_KEY)`、封装进函数、第二次加载加上 `override=True`、返回类型改成 `dict[str, str | bool]`。最终的 `config.py` 实测：

```python
print(load_config())
os.environ["APP_ENV"] = "testing"
print(load_config())
os.environ["APP_ENV"] = "staging"
try:
    load_config()
except ValueError as e:
    print("ValueError:", e)
```

```text
{'app_env': 'development', 'debug': True, 'api_key': 'dev-123456', 'api_base_url': 'https://dev.demo.com'}
{'app_env': 'testing', 'debug': True, 'api_key': 'test-123456', 'api_base_url': 'https://test.demo.com'}
ValueError: 不支持的运行环境
```

（这些密钥都是演示用的假值，所以仓库里可以提交这几个文件。）

第二次能从 `dev-123456` 切到 `test-123456`，靠的就是 `override=True`：第一次调用留下的 `API_KEY=dev-123456` 已经在环境里了，默认不覆盖的话，你会拿着开发环境的密钥，以为自己在测试环境。

回头看还有两点：

- `Day19/` 下其实没有基础 `.env`，第一行 `load_dotenv(BASE_DIR / ".env")` 一直返回 `False`。程序能跑是因为 `APP_ENV` 有默认值，但那一行从来没起过作用。要么补上这个文件，要么删掉那行并写个注释。
- 第二段的 `override=True` 也会盖掉**系统**里的同名变量，和昨天「部署平台注入的值优先」正好相反。小项目问题不大，知道有这个取舍就行。

## 加练

[多环境配置](加练/day19_多环境配置.md)：换一种做法，把系统变量和几个 `.env` 文件都读成字典，自己按优先级合并，不去改 `os.environ`，从根上避开上面那个「`override=True` 盖掉系统变量」的问题。
