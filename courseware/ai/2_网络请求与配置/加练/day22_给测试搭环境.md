---
kind: problem
outline: [2, 2]
time: 45 分钟
uses: [yield fixture, scope, fixture 依赖 fixture, monkeypatch, conftest.py]
record:
  - text: Day22 Fixture
    link: https://github.com/syjlpineapple/ai-learning/blob/main/courseware/records/python/Day22.md
---

# 第 16 题 · 给测试搭环境

M5、M7 的测试里，每个测试都用 `with running_server()` 开一个新的排行榜服务。实测关一次服务要 0.5 秒左右：`serve_forever` 每 0.5 秒才检查一次「该停了吗」，`shutdown()` 要等它看到。每个测试都多等半秒，100 个测试就是 50 秒。

这一题把服务改成**整个测试运行共用一个**。这样做的代价是测试之间会互相影响，你得自己把它们隔开。顺便把环境变量和 `APIClient` 也做成 fixture，测试里不再重复写准备和清理的代码。

## 题目

在 [`code/m08_testing/p16_fixtures_exercise.py`](../../code/m08_testing/p16_fixtures_exercise.py) 里实现四个 fixture：

1. **`leaderboard`**：开一个排行榜服务（第 5 题的 `running_server()`）交给测试。**整个测试运行只开这一个**，所有测试跑完再关
2. **`server`**：每个测试开始前，把 `leaderboard` 的状态恢复成刚启动的样子（7 条种子成绩、没有失败计划、不要求密钥……），然后返回它
3. **`app_env`**：设置 `API_KEY=sk-p16-test`、`API_BASE_URL`（指向 `server`）、`TIMEOUT=2`、`RETRIES=0` 四个环境变量，服务端也设上同一个密钥（`state.api_key`）。测试结束后，环境变量恢复原样
4. **`client`**：用 `load_settings(os.environ)` 读配置，创建第 12 题的 `APIClient` 交给测试。测试结束后关掉它，**测试失败了也要关**

写好以后，测试可以这样用：

```python
def test_upload(server, client):
    assert client.upload("王五", 3)["id"] == 8
    server.state.fail_plan = [503] * 5      # 随便改，下一个测试拿到的还是干净的服务
```

**评测怎么做**：用你的 fixture 跑两个写好的测试文件 [`_p16_consumer_a.py`](../../code/m08_testing/_p16_consumer_a.py) 和 [`_p16_consumer_b.py`](../../code/m08_testing/_p16_consumer_b.py)。前面的测试故意把服务、环境变量弄脏，后面的测试检查脏东西有没有被清掉。不要改这两个文件。

**验证**（在 `code/` 目录下）

```powershell
pytest tests/test_m08.py -k p16 -v
```

现在是 `8 passed, 4 skipped`，全部做完是 `12 passed`。想直接看那两个文件里每个测试的结果：

```powershell
pytest m08_testing/_p16_consumer_a.py m08_testing/_p16_consumer_b.py -p m08_testing.p16_fixtures_exercise -v
```

> 真实项目里，这些 fixture 写在 `tests/conftest.py`，pytest 会自动加载，测试文件不用 import。这里用 `-p` 加载，是为了能在练习文件和参考答案之间切换。

::: details 提示：fixture 怎么用别的 fixture
和测试函数一样，写在参数里：`def server(leaderboard): ...`。pytest 自带的 `monkeypatch`、`tmp_path` 也是 fixture，同样写在参数里。作用域写在装饰器上：`@pytest.fixture(scope="session")`。
:::

::: details 提示：状态怎么恢复
`running_server()` 给你的是一个 `Running`，`running.state` 是服务的状态，`ServerState()` 就是刚启动时的样子。想一想：服务端处理请求时用的是哪个对象？你把 `running.state` 换掉，服务端会知道吗？
:::

::: details 提示：环境变量和关闭
`monkeypatch.setenv(name, value)` 设的环境变量，测试结束后自动恢复。关闭用 `yield`：`yield` 前面是准备，后面是清理。`APIClient` 支持 `with`。
:::

<Reveal>

## 讲评

### 参考答案

```python
@pytest.fixture(scope="session")
def leaderboard():
    with running_server() as srv:
        yield srv


@pytest.fixture
def server(leaderboard):
    vars(leaderboard.state).update(vars(ServerState()))   # 在原来的对象上改
    return leaderboard


@pytest.fixture
def app_env(server, monkeypatch):
    values = {"API_KEY": API_KEY, "API_BASE_URL": server.base_url,
              "TIMEOUT": "2", "RETRIES": "0"}
    for name, value in values.items():
        monkeypatch.setenv(name, value)
    server.state.api_key = API_KEY
    return values


@pytest.fixture
def client(app_env):
    with APIClient(load_settings(os.environ)) as api:
        yield api
```

带类型标注的版本见 [`p16_fixtures_solution.py`](../../code/m08_testing/p16_fixtures_solution.py)。四个 fixture 连成一条链：`client` → `app_env` → `server` → `leaderboard`。测试只写了 `client`，pytest 就顺着参数把整条链准备好；结束时倒过来清理：先关 client，再恢复环境变量，`leaderboard` 等所有测试都跑完才关。

一个典型的初稿照搬 M5 测试里的写法：`leaderboard` 不写 scope、`server` 里写 `leaderboard.state = ServerState()`、`app_env` 用 `os.environ.update(...)`、`client` 用 `return`。评测 4 项里它挂了 3 项，**偏偏「状态恢复」那一项通过了**。原因见坑 2。

### 坑 1：scope 不写，就是每个测试一个

```text
3 个测试一共开了 3 个服务        scope 不写（function）     评测文件跑了 2.11 秒
3 个测试一共开了 2 个服务        scope="module"            1.10 秒
3 个测试一共开了 1 个服务        scope="session"           0.58 秒
```

| scope | 多久建一次 |
|---|---|
| `function`（默认） | 每个测试一次 |
| `module` | 每个测试文件一次 |
| `session` | 整个测试运行一次 |

评测的两个测试文件都用 `server`，所以 `module` 会开 2 个。只有 3 个测试，差距就有 1.5 秒；测试越多差得越多。

还有一个容易犯的错：`with running_server() as srv: return srv`。`return` 一执行，`with` 块就结束了，服务在测试开始之前就关掉了。测试里的请求连不上，Windows 上 `TIMEOUT=2` 时报的是 `requests.exceptions.ConnectTimeout`（第 7 题讲过为什么是超时而不是连接被拒绝）。要用 `yield`，让 fixture 停在 `with` 块里面，等测试跑完再回来。

### 坑 2：共用一个服务，前一个测试的状态会留给后一个

改成 `session` 以后，上一个测试设的失败计划、密钥、上传的成绩都还在服务里，下一个测试一请求就是 503 或 401。所以要在每个测试开始前恢复。初稿的恢复是这样写的：

```python
leaderboard.state = ServerState()
```

它不起作用。`Running.state` 和服务端（`httpd.state`）原本指向同一个 `ServerState` 对象；这一行只是让 `Running.state` 指向了一个新对象，服务端手里拿的还是旧的：

```text
srv.state.fail_plan = [503]
srv.state = ServerState()
GET /scores    →  503            服务端还在用旧的状态
```

更糟的是，换掉以后测试里所有 `server.state.xxx = ...` 都改到了那个新对象上，服务端根本看不到。测试以为自己设了失败计划，其实什么都没设。评测里：

```text
要求 2：成绩应该是最初的 7 条，实际是 8 条（上一个测试上传过一条）
```

那初稿为什么能通过这一项？因为它的 `leaderboard` 没写 scope，每个测试都是一个新服务，状态本来就是干净的，`server` 里那行恢复有没有用都一样。**两个错误互相掩盖了**（第 12 题也遇到过）：把 scope 改对，这个错误才暴露出来。

正确的做法是在原来的对象上改：`vars(leaderboard.state).update(vars(ServerState()))`，把新对象的每个属性抄到旧对象上。

恢复成绩列表时还有一个陷阱：

```python
leaderboard.state.scores = SEED_SCORES      # 没有复制
```

```text
上传一条成绩以后   SEED_SCORES 的长度：7 → 8
```

两个名字指向同一个列表，服务往 `state.scores` 里加一条，模块里的常量 `SEED_SCORES` 也多了一条，以后每次「恢复」都是 8 条。`ServerState` 里写的是 `default_factory=lambda: list(SEED_SCORES)`，每次复制一份，就是为了这个。

### 坑 3：直接改 `os.environ`，下一个测试还看得见

```python
os.environ.update(values)
```

```text
要求 3：前面的测试设的环境变量 ['API_KEY', 'API_BASE_URL', 'TIMEOUT', 'RETRIES'] 还在
```

`os.environ` 是整个进程共用的，测试结束不会自动还原。这和第 11 题 `load_dotenv` 留下的污染是同一个问题：测试结果开始取决于测试的执行顺序。

`monkeypatch.setenv` 会先记下这个变量原来的样子，测试结束后改回去：原来有值的恢复原值，原来没有的删掉。`monkeypatch.delenv`（删掉一个变量）、`monkeypatch.setattr`（替换一个属性，第 15 题讲评里替换 `time.sleep` 用的就是它）也一样，测试结束自动还原。

### 坑 4：session 的 fixture 不能用 `monkeypatch`

想把 `app_env` 也改成 `session`，省得每个测试设一次？

```text
ScopeMismatch: You tried to access the function scoped fixture monkeypatch with a session scoped request object.
```

`monkeypatch` 的作用域是 `function`：它在每个测试结束时还原。活得长的 fixture 不能依赖活得短的，否则测试结束时 `monkeypatch` 已经还原了，`session` 的 fixture 却还要接着用。`tmp_path` 也一样（同样的报错），`session` 级的临时目录要用 `tmp_path_factory`。

所以参考答案里是一长三短：`leaderboard` 是 `session`，`server`、`app_env`、`client` 都是默认的 `function`。贵的东西共用，便宜的状态每次重建。

### 坑 5：`return` 交出去的资源没人关

```python
@pytest.fixture
def client(app_env):
    return APIClient(load_settings(os.environ))
```

```text
要求 4：有 2 个 client 测试结束后没有关
```

`return` 以后 fixture 就结束了，没有地方写清理代码。改成 `yield`，后面的代码在测试结束后执行，**测试失败了也执行**：评测里那个故意失败的测试，它的 client 照样被关掉了。

但有一种情况 `yield` 后面不会执行：**`yield` 之前就出错了**。实测 fixture 在 `yield` 前抛异常，测试报 ERROR，`yield` 后面的清理代码一行都没跑。所以参考答案把 `yield` 放在 `with` 里面：准备到一半出错，`with` 也会把已经打开的东西关掉。

## 复盘

::: tip 这题用到的
- **fixture 用 fixture**：写在参数里；pytest 按依赖顺序准备，倒过来清理
- **`yield` 分两段**：前面准备，后面清理；测试失败也会清理，`yield` 之前出错就不会。`yield` 放在 `with` 里最稳
- **scope**：`function`（默认）、`module`、`session`；贵的资源（服务、数据库连接）用大的 scope
- **共用就要重置**：大 scope 的资源，配一个 `function` 级的 fixture 在每个测试前恢复状态
- **恢复状态要在原对象上改**：给 `running.state` 重新赋值，服务端手里的那个对象不会变；种子数据要复制一份
- **`monkeypatch`**：`setenv`、`delenv`、`setattr`，测试结束自动还原；不要直接改 `os.environ`
- **活得长的不能依赖活得短的**：`session` 的 fixture 用 `monkeypatch`、`tmp_path` 会报 `ScopeMismatch`
- **`conftest.py`**：共用的 fixture 放这里，pytest 自动加载，不用 import
:::

## 自测

1. `leaderboard` 改成 `scope="session"` 以后，为什么还需要 `server` 这个 fixture？
2. `running.state = ServerState()` 为什么恢复不了服务的状态？应该怎么写？
3. 想让 `app_env` 也只设置一次，改成 `scope="session"` 会怎样？
4. fixture 里 `yield` 后面的代码，什么情况下会执行，什么情况下不会？

<details>
<summary>参考答案</summary>

1. 服务是所有测试共用的，前一个测试设的失败计划、密钥、上传的成绩都会留到后一个测试。`server` 是 `function` 级的，在每个测试开始前把状态恢复成刚启动的样子。
2. 服务端处理请求时用的是它自己手里的那个 `ServerState` 对象。给 `running.state` 赋一个新对象，只是让 `running.state` 这个名字指向别处，服务端那个对象没变。要在原对象上改：`vars(running.state).update(vars(ServerState()))`。
3. 报 `ScopeMismatch`：`app_env` 用了 `monkeypatch`，而 `monkeypatch` 是 `function` 级的，`session` 级的 fixture 不能依赖它。
4. 测试通过或失败，`yield` 后面都会执行。`yield` 之前就抛了异常（准备到一半出错），后面就不会执行。

</details>

</Reveal>
