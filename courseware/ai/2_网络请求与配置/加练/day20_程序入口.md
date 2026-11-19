---
kind: problem
outline: [2, 2]
time: 40 分钟
uses: [三层结构, 退出码, 最外层的 except Exception, 标准输出和标准错误]
record:
  - text: Day20 三层架构与 finally
    link: https://github.com/syjlpineapple/ai-learning/blob/main/courseware/records/python/Day20.md
---

# 第 13 题 · 程序入口

到这里，各个部件都有了：第 11 题读配置，第 12 题的 `APIClient` 发请求、重试，第 7 题给失败分类。还差最上面一层：从命令行接收命令，把部件组装起来，处理它们抛出来的各种异常，最后告诉操作系统程序成功了没有。

```text
p13_main      命令行、组装、决定出错了怎么办、退出码
   ↓
p12_client    发请求、重试、解析回应
   ↓
p11 / p10     读配置、校验
```

## 题目

打开 [`code/m07_client/p13_main_exercise.py`](../../code/m07_client/p13_main_exercise.py)，实现 `main(argv, environ, config_dir, client_factory)`，返回退出码：

```powershell
python -m m07_client.p13_main_exercise scores           # 打印排行榜
python -m m07_client.p13_main_exercise scores 张三
python -m m07_client.p13_main_exercise upload 张三 3     # 上传一条成绩
```

| 退出码 | 什么时候 |
|---|---|
| `0` | 成功 |
| `2` | 命令行不对，或者配置不对 |
| `3` | 网络请求失败（重试过了还不行） |
| `1` | 其他所有情况：程序自己的 bug |

配置目录是 `m07_client/config/`，里面的值都是假的。`client_factory` 平时就是 `APIClient` 这个类，测试会换成一个能检查「客户端有没有被关掉」的版本。

**要求**

1. 命令行不对时，在**标准错误**里打印 `USAGE`，返回 2，**不建客户端**
2. 配置不对（`load_for` 抛 `ConfigError`）时，记一条 `ERROR` 写明原因，**不带 traceback**，返回 2，不建客户端
3. 用 `with` 管理客户端，结果打印到**标准输出**。排行榜是空的时打印 `（还没有成绩）`
4. 网络请求失败（`RequestException`）时，记一条 `ERROR`，写明 `classify(e)` 的类别，返回 3
5. 其他任何异常，用 `logger.exception` 记下完整的 traceback，返回 1。第 3 到 5 条里，客户端都必须被关掉

**验证**（在 `code/` 目录下）

```powershell
pytest tests/test_m07.py -k p13 -v
```

现在是 `16 passed, 14 skipped`，全部做完是 `30 passed`。

::: details 提示：要求 2，配置错误的 ERROR 带了 traceback
`logger.exception` 等于 `logger.error` 加上 traceback。配置写错了是预料之中的情况，要的是一句话说清楚哪里不对，不是一大段调用栈。
:::

::: details 提示：要求 4、5，怎么区分网络问题和 bug
两个 `except`：先接 `requests.exceptions.RequestException`，再接 `Exception`。顺序反过来会怎样？
:::

<Reveal>

## 讲评

### 参考答案

```python
def main(argv, environ=os.environ, config_dir=CONFIG_DIR, client_factory=APIClient):
    command = parse_args(argv)
    if command is None:
        print(USAGE, file=sys.stderr)
        return BAD_INPUT
    try:
        env, settings = load_for(config_dir, environ)
    except ConfigError as e:
        logger.error("配置有问题：%s", e)
        return BAD_INPUT
    logger.info("环境 %s，服务 %s", env, settings.base_url)

    name, args = command
    try:
        with client_factory(settings) as client:
            if name == "scores":
                rows = client.get_scores(*args)
                for line in format_scores(rows) or ["（还没有成绩）"]:
                    print(line)
            else:
                row = client.upload(*args)
                print(f"已上传：第 {row['id']} 条")
    except requests.exceptions.RequestException as e:
        logger.error("请求失败（%s）：%s", classify(e), e)
        return NETWORK
    except Exception:
        logger.exception("程序出错了")
        return BUG
    return OK
```

`parse_args` 把命令行变成 `("scores", [...])` 或 `("upload", [玩家, 次数])`，不合法返回 `None`，完整代码见 [`p13_main_solution.py`](../../code/m07_client/p13_main_solution.py)。

整个 `main` 的顺序是：**先做不需要网络就能发现的检查**（命令行、配置），再建客户端、发请求。前面的问题都在启动的一瞬间暴露，不会等到连上服务器、重试了好几次之后才发现配置里少了一项。

### 坑 1：先建客户端，再进 `try`

典型初稿照着 Day20 的 `main.py` 写：

```python
env, settings = load_for(config_dir, environ)     # 在 try 外面：配置错了直接崩
client = client_factory(settings)
try:
    ...
except Exception as e:
    print("出错了：", e)
    return 1
finally:
    client.close()
```

配置不对时，`load_for` 在 `try` 外面抛出 `ConfigError`，程序带着一大段 traceback 崩掉，测试里的三种配置错误都是这样失败的。

有人会把 `load_for` 也挪进 `try`，再在前面写一句 `client = None`。这时如果配置出错，`finally` 里的 `client.close()` 会再出一个错：

```text
ValueError: 配置不对

During handling of the above exception, another exception occurred:

AttributeError: 'NoneType' object has no attribute 'close'
```

报错的最后一行是 `AttributeError`，真正的原因 `ValueError` 被挤到了上面。参考答案用 `with`：客户端建成功了才会进入 `with` 块，退出时一定会 `close`；没建成功，根本不会去关它。第 1.5 章讲过 `finally`，`with` 就是把「建好了才清理」这件事交给了语法。

### 坑 2：最外层的 `except Exception` 只 `print`

Day20 讲义说，`except Exception` 只在程序最外层用，而且**必须记下完整的异常**。初稿只 `print("出错了：", e)`：

- 网络问题、程序 bug、配置错误，返回的都是 1，调用方分不清
- `KeyError('程序自己的 bug')` 只剩一句 `出错了： '程序自己的 bug'`，不知道是哪一行出的错
- 错误信息打在了标准输出里，和排行榜混在一起

参考答案分成两层：预料之中的 `RequestException` 单独接，用一句话说清楚类别；剩下的才归 `except Exception`，用 `logger.exception` 留下完整的 traceback。**预料之中的错误不需要 traceback，预料之外的才需要。**

### 坑 3：退出码

程序的退出码是给别的程序看的：PowerShell 里是 `$LASTEXITCODE`，CI 和部署脚本靠它判断这一步成功了没有。初稿在命令行不对时返回 2，其他所有失败都返回 1，`scores` 命令写错了参数（`scores a b`）还会被当成正常的查询发出去。

`main` 返回整数、由 `sys.exit(main(sys.argv[1:]))` 交给操作系统，这样测试可以直接调用 `main` 检查返回值，不用开子进程。第 1.3 章讲过 `sys.exit()` 的退出码。

### 坑 4：结果走标准输出，其他的走标准错误

```text
$ python -m m07_client.p13_main_solution scores 李四
 1. 李四  3 次                                         ← 标准输出
INFO __main__: 环境 development，服务 http://...        ← 标准错误
```

别人可能会用 `> scores.txt` 把结果存下来，或者用管道交给下一个程序。日志、用法说明、错误信息都放标准错误，标准输出里只有结果，这些用法才不会被干扰。`logging` 默认就输出到标准错误；`print(USAGE, file=sys.stderr)` 是手动指定。

注意日志里的 logger 名字是 `__main__`，不是 `m07_client.p13_main_solution`。用 `-m` 运行时，入口模块的 `__name__` 就是 `"__main__"`（第 3.1 章），`getLogger(__name__)` 跟着变。测试最开始按模块名写断言，在这里失败了一次。

### 坑 5：日志配置写在哪

```python
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    sys.exit(main(sys.argv[1:]))
```

`basicConfig` 写在 `if __name__ == "__main__":` 里，不写在 `main` 里。测试会直接调用 `main`，在测试里配置日志会拆掉 pytest 自己的 handler（第 4 题坑 1），`caplog` 就收不到日志了。

### 典型初稿会被哪些测试抓住

```text
FAILED test_p13_no_scores                空排行榜什么都没打印
FAILED test_p13_bad_arguments            （5 条）返回 1 或者 IndexError；用法打在了标准输出
FAILED test_p13_config_error             （3 条）ConfigError 在 try 外面，直接崩了
FAILED test_p13_network_error            返回 1，应该是 3
FAILED test_p13_wrong_key                返回 1，应该是 3
FAILED test_p13_bug                      只 print 了一句，没有 traceback；输出混进了标准输出
12 failed, 2 passed
```

## 复盘

::: tip 这题用到的
- **入口负责组装和决定对策**：读配置、建客户端、接异常、返回退出码。下面的模块只管做事和抛异常
- **先检查不需要网络的东西**：命令行、配置，在发请求之前就失败
- **`with` 管理资源**：建成功了才清理；不要在 `finally` 里关一个可能是 `None` 的对象
- **异常分两层**：预料之中的（`ConfigError`、`RequestException`）一句话说清楚；预料之外的在最外层 `except Exception`，用 `logger.exception` 留下 traceback。这是全课唯一该接 `Exception` 的地方
- **退出码区分失败的种类**；`main` 返回整数，`sys.exit(main(...))`
- **结果走标准输出，日志和错误走标准错误**
:::

M7 到这里结束。程序现在能跑起来了，但测试它的时候一直开着一个本机服务，还要专门让服务「故意出错」。下一个模块 M8 不再依赖真的服务：用 Mock 冒充网络，讲清楚一直在用的 `@pytest.fixture` 这类装饰器到底是什么，最后用 fixture 给测试搭一个共用的环境。

## 自测

1. 为什么参考答案要在建客户端之前检查命令行和配置？
2. `client = None` 然后 `try: ... finally: client.close()`，配置出错时报错的最后一行是什么？真正的原因在哪？
3. 为什么配置错误用 `logger.error`，程序 bug 用 `logger.exception`？

<details>
<summary>参考答案</summary>

1. 这些问题不需要网络就能发现。先检查，程序在启动的一瞬间就能失败并说清原因；先建客户端、发请求的话，可能要等连接超时、重试几次之后，才发现是配置里少了一项。
2. 最后一行是 `AttributeError: 'NoneType' object has no attribute 'close'`。真正的原因（比如 `ConfigError`）在上面那段 traceback 里，被 `During handling of the above exception, another exception occurred` 隔开了，很容易看漏。
3. 配置错误是预料之中的，一句话说清楚哪一项、什么值就够了，traceback 只会把这句话淹没。程序 bug 是预料之外的，不知道在哪一行、怎么走到那里的，需要完整的 traceback 才能定位。

</details>

</Reveal>
