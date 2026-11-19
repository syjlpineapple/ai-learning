# Day 13 · 日志与返回值的语义

> **学习日** 2026-10-26（15:46 - 15:59，4 轮对话）
> **对应代码** [`dailypractice/Day13/`](../../../dailypractice/Day13/)（`history.py` / `test_history.py`）
> **原始对话** `courseware/_raw/markdown/03_Python每日练习出题.md`（对话里称「Day 13」）

> `history.py` 第三遍。Day11 读写与校验 → Day12 测试覆盖 → **Day13 日志** → Day14 分层校验与错误语义。

## 本节掌握

- `logging` 为什么比 `print` 好
- 五个日志级别，以及该用哪个
- `logging.getLogger(__name__)` 里 `__name__` 的意义
- **模块负责记录日志，应用入口负责配置日志**
- `basicConfig()` 放在哪会导致测试里看不到日志（本节的核心发现）
- 没配置日志时，WARNING 和 INFO 的行为**不一样**
- 日志不改变返回值——**返回值的语义歧义问题**
- 错误处理的三种设计方案及其取舍

这一节有两个问题是自己发现的，不是被告知的，含金量最高。

---

# 第一部分 · 知识讲解

## 1. 为什么用 logging 而不是 print

前面十二天排查问题全靠 `print`。它的毛病在真实项目里会放大：

| 需求 | `print` | `logging` |
|---|---|---|
| 区分「调试信息」和「严重错误」 | 做不到，全是一样的 | 五个级别 |
| 上线后关掉调试输出 | 得逐行删掉或注释 | 改一个级别配置 |
| 知道这条消息来自哪个模块 | 得自己在文字里写 | 自动带模块名 |
| 记录时间 | 自己拼字符串 | 格式里配一次 |
| 输出到文件、同时上报监控 | 做不到 | 换 handler |

核心区别：**`print` 是硬编码的输出，`logging` 是可配置的记录。** 写代码时只管「记一条什么级别的消息」，去哪、要不要显示，交给配置决定。

## 2. 五个级别

| 级别 | 数值 | 什么时候用 |
|---|---|---|
| `DEBUG` | 10 | 详细的排查信息，只在开发时看 |
| `INFO` | 20 | 正常流程的关键节点（「开始读取历史记录」） |
| `WARNING` | 30 | 不正常但程序能继续（「历史文件不存在，用空记录」） |
| `ERROR` | 40 | 某个操作失败了 |
| `CRITICAL` | 50 | 严重到程序没法继续 |

**级别是过滤阈值**：配置为 INFO 时，INFO 及以上（INFO/WARNING/ERROR/CRITICAL）都输出，DEBUG 被丢掉。

本节的用法是：正常节点记 `INFO`，各种校验失败记 `WARNING`——因为数据不合法时程序并没有挂，只是用空列表继续，属于「不正常但能继续」。

## 3. `logging.getLogger(__name__)`

```python
logger = logging.getLogger(__name__)
```

这是模块级 logger 的标准写法，固定放在 import 之后。

`__name__` 就是 Day10 学的那个变量——被导入时它是模块的完整路径，比如 `dailypractice.Day13.history`。所以日志会自动带上来源：

```text
INFO:dailypractice.Day13.history:开始读取历史记录
```

好处是**日志能按模块分别控制**。logger 的名字是带层级的，用点分隔：

```python
logging.getLogger("dailypractice").setLevel(logging.WARNING)   # 整个包只看警告
logging.getLogger("dailypractice.Day13.history").setLevel(logging.DEBUG)  # 这个模块看全部
```

如果写死成 `getLogger("history")`，就失去了这种层级控制能力。

## 4. 核心原则：模块记录，入口配置

```python
# 业务模块（history.py）：只获取 logger、只记录
logger = logging.getLogger(__name__)
logger.warning("历史记录文件不存在")

# 应用入口（main.py）：统一配置级别、格式、输出目标
logging.basicConfig(level=logging.INFO)
```

为什么要这么分：

一个项目有多个模块（`history.py`、`api_client.py`……），如果每个模块都自己 `basicConfig()`，级别和格式就会互相打架——而且 `basicConfig()` **只有第一次调用生效**，后面的静默失效，于是最终行为取决于「哪个模块先被导入」，非常难排查。

**配置是部署时的决定**（开发环境看 DEBUG、生产环境只记 WARNING 并写进文件），不该由业务模块决定。模块只管「这件事值得记一条 WARNING」。

## 5. 核心发现：`basicConfig()` 的位置

当时把 `basicConfig()` 从模块顶层挪进了入口保护：

```python
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print(load_history("history.json"))
```

然后发现：**「你这样调整位置后，执行测试就不生效了」**。

原因就是 Day10 的知识：测试文件是 `import` 这个模块，`__name__` 不等于 `"__main__"`，所以 `basicConfig()` 这一行**根本不会执行**。

### 实测：没配置时到底会怎样

这里有个比「看不到日志」更精确的结论。实测（Python 3.13.2）：

```text
=== 没有调用 basicConfig ===
root logger 级别: WARNING
root logger 的 handler: []
lastResort handler 级别: WARNING
→ 读取不存在的文件：WARNING「历史记录文件不存在」仍然输出到了 stderr

=== 调用 basicConfig(level=logging.INFO) 之后 ===
root logger 级别: INFO
→ INFO:dailypractice.Day13.history:开始读取历史记录   ← INFO 这才出现
```

所以准确的说法是：

| 日志级别 | 没有 `basicConfig` | 有 `basicConfig(level=INFO)` |
|---|---|---|
| `WARNING` 及以上 | **仍会输出**，但格式简陋（只有消息本身） | 输出，带 `级别:模块名:消息` 格式 |
| `INFO` / `DEBUG` | **不输出** | 输出 |

WARNING 还能出来，靠的是 `logging.lastResort`——Python 3.2 起加的兜底 handler。当 root logger 没有任何 handler 时，它接管 WARNING 及以上的记录，直接丢到 stderr。这是为了避免「程序出了警告却一声不响」。

而 INFO 被拦住有两个原因叠加：root logger 默认级别是 WARNING，`lastResort` 的级别也是 WARNING。

> 实用结论：**不要用「日志有没有打出来」判断代码走到没走到。** WARNING 能出来、INFO 不能，很容易误判成「代码没执行到那一行」。要确认就先配好 `basicConfig(level=logging.DEBUG)`。

### 解决办法

对学习项目，在测试文件顶部配一次即可：

```python
import logging
logging.basicConfig(level=logging.INFO)
```

工程项目里通常由测试框架配置（pytest 有 `log_cli` 和 `log_level` 选项，不必手写）。

## 6. 日志不改变返回值

容易混的一点：**记日志只是留痕给开发者排查，它不影响函数的返回值，调用方也看不到它。**

```python
except FileNotFoundError:
    logger.warning("历史记录文件不存在")    # 开发者在日志里能看到
    return []                              # 调用方只拿到一个空列表
```

调用方**拿不到**「文件不存在」这个信息，它只看见 `[]`。

这就引出本节最重要的设计问题。

## 7. 返回值的语义歧义

当时的进阶问题：拿到 `[]` 的调用方，能区分「用户还没有历史记录」和「文件里有非法数据」吗？

答案是**不能**——这是自己识别出来的。六种完全不同的情况返回了同一个值：

| 实际情况 | 返回值 | 该怎么处理 |
|---|---|---|
| 文件不存在 | `[]` | 正常，首次运行 |
| JSON 语法损坏 | `[]` | 数据坏了，可能要备份、告警 |
| 顶层不是列表 | `[]` | 数据格式不对 |
| 元素不是整数 | `[]` | 数据内容不对 |
| 数字越界 | `[]` | 违反业务规则 |
| 文件内容真的是 `[]` | `[]` | 正常，用户清空过记录 |

于是调用方只能这样写：

```python
history = load_history("history.json")
if history == []:
    print("没有历史记录")      # 可能在撒谎：文件也许存在但已损坏
```

**用同一个返回值表示多种语义，调用方就失去了做正确决策的能力。** 日志能帮开发者事后排查，但帮不了运行中的程序。

## 8. 三种错误处理设计

没有普适的最优解，取决于业务需要。

### 方案 A：返回空值 + 记日志（Day13 的做法）

```python
except FileNotFoundError:
    logger.warning("...")
    return []
```

- **优点**：调用方代码简单，不会因为读取失败而中断
- **缺点**：语义歧义，调用方无法区分原因
- **适合**：读取失败无关紧要的场景（可选的缓存、非关键的统计数据）

### 方案 B：抛异常

```python
except FileNotFoundError:
    return []                    # 首次运行是正常的
# JSON 损坏则让异常往上抛，或主动抛 ValueError
```

- **优点**：不同错误可以分别处理，调用方必须正面应对
- **缺点**：调用方必须写 `try/except`，否则程序崩
- **适合**：错误必须被处理的场景（配置文件、关键数据）

### 方案 C：同时返回结果和错误

```python
history, error = load_history("history.json")
```

- **优点**：语义明确，又不用异常控制流程
- **缺点**：每次调用都要解包、判断，代码啰嗦
- **适合**：错误是常规分支而非异常情况（Go 语言的主流风格）

### 当时的选择

> **文件不存在：返回 `[]`；JSON 格式错误：抛出异常。**

这个判断是对的，理由在于**两种情况的业务含义根本不同**：

- 文件不存在 = 用户还没玩过，这是**正常状态**，用空记录继续完全合理
- JSON 损坏 = 本该有数据却读不出来，这是**异常状态**，不该伪装成「没有记录」

同样的思路搬到 AI 应用上：配置文件不存在可以用默认值兜住；配置文件存在但格式损坏，就必须报错——否则程序会带着一套不是你想要的默认配置悄悄跑起来。

> 这个设计的实现是 Day 14 的内容。Day13 的代码仍然是方案 A。

---

# 第二部分 · 当天的练习

## 一、题目

在 `history.py` 里引入 `logging`，让「文件不存在」和「JSON 格式错误」分别产生 WARNING 日志。思考日志该放在什么位置。

## 二、代码改进

这一版同时修掉了 Day12 的几处退步：

| 改动 | Day12 | Day13 |
|---|---|---|
| 读取编码 | `open(filename)` | `open(filename, "r", encoding="utf-8")` ✅ |
| 类型注解 | `data: list`、`-> list` | `data: list[int]`、`-> list[int]` ✅ |
| 类型比较 | `type(ls) != list` | `type(ls) is not list` ✅ |
| 异常类名 | `json.decoder.JSONDecodeError` | `json.JSONDecodeError` ✅ |
| 校验位置 | 嵌在 JSON 解析的 `try` 里 | 移到 `try` 外面 ✅ |

**`json.JSONDecodeError` 和 `json.decoder.JSONDecodeError` 是同一个类**，前者是 `json` 包对外暴露的名字，后者是它的实际定义位置。用前者——实现位置是内部细节，可能变。

**校验移出 `try` 的意义**：那个 `try` 现在只包住 `json.load()` 一行，职责单一（只处理 JSON 语法错误）。而且校验是在 `with` 块**外面**做的，也就是文件已经关闭之后——文件该用完就关，没必要在持有文件句柄的时候做业务校验。

## 三、日志位置

```python
with open(filename, "r", encoding="utf-8") as f:
    logger.info("开始读取历史记录")
    ...
```

这条 INFO 在 `open()` **之后**，所以文件不存在时它不会被记录——直接跳到 `except FileNotFoundError` 记 WARNING。

这不是 bug，但要清楚它的含义：现在这条日志表示「文件已打开，开始解析」。如果想表示「开始尝试读取」，就该挪到 `try` 之前。**日志的文字描述要和它的实际位置对得上**，否则看日志的人会误判程序走到了哪一步。

## 四、最终代码

```python
import json
import logging

logger = logging.getLogger(__name__)


def save_history(filename: str, data: list[int]) -> None:
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_history(filename: str) -> list[int]:
    try:
        with open(filename, "r", encoding="utf-8") as f:
            logger.info("开始读取历史记录")
            try:
                ls = json.load(f)
            except json.JSONDecodeError:
                logger.warning("JSON 格式错误")
                return []

        if type(ls) is not list:
            logger.warning("历史记录的数据结构错误")
            return []

        for i in ls:
            if type(i) is not int:
                logger.warning("历史记录包含非整数")
                return []

            if not 1 <= i <= 100:
                logger.warning("历史记录数字超出范围")
                return []

        return ls

    except FileNotFoundError:
        logger.warning("历史记录文件不存在")
        return []


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print(load_history("history.json"))
```

五个失败分支各有一条专属的 WARNING，排查时能直接定位是哪一类问题。这是日志相比 `print` 的直接收益——以前只能看到「返回了 `[]`」，现在能看到「为什么是 `[]`」。

## 五、现在回头看

### 一、测试文件没配置日志

`Day13/test_history.py` 顶部没有 `logging.basicConfig()`，所以跑测试时 INFO 看不到（WARNING 能看到，但没有格式前缀）。当时讨论出的解决办法没落进代码。

### 二、测试仍在模块顶层调用

最后一行还是裸的 `test_history()`，没有 `if __name__ == "__main__":` 保护。这个问题 Day12 被指出过，Day13 仍然在。后果是 pytest 下测试跑两遍（导入时一次、收集后一次）。

### 三、`save_history` 的参数顺序和 Day11 不一致

Day11 是 `save_history(history, filename)`，Day12 起改成 `save_history(filename, data)`。改动本身合理，但属于破坏性变更。

### 四、日志消息里没带上下文

```python
logger.warning("历史记录文件不存在")
```

没有说是**哪个**文件。真实项目里同一个函数会被不同路径调用，日志不带参数就没法定位：

```python
logger.warning("历史记录文件不存在: %s", filename)
```

注意用 `%s` 占位符传参，**不要用 f-string**。原因是 logging 只在这条日志真的要输出时才做字符串格式化；用 f-string 的话，哪怕这条日志因为级别被过滤掉，字符串拼接也已经执行了。日志量大时这是实际的性能损失。

## 六、复习自测

1. `logging` 比 `print` 好在哪几点？
2. 五个日志级别从低到高是什么？级别配成 INFO 时，DEBUG 会输出吗？
3. `logging.getLogger(__name__)` 里 `__name__` 起什么作用？写死成字符串有什么损失？
4. 为什么业务模块不该自己调 `basicConfig()`？
5. `basicConfig()` 放在 `if __name__ == "__main__":` 里，用测试导入这个模块时会怎样？
6. 没有调用 `basicConfig()` 时，`logger.warning()` 和 `logger.info()` 的表现一样吗？
7. 记了日志之后，调用方能知道失败原因吗？
8. 为什么说「文件不存在返回 `[]`、JSON 损坏抛异常」是合理的设计？
9. 日志消息为什么推荐 `logger.warning("失败: %s", name)` 而不是 f-string？

<details>
<summary>参考答案</summary>

1. 有级别可以分类过滤、能通过配置一键调整而不用改代码、自动带模块名和时间、能切换输出目标（控制台／文件／监控系统）。
2. DEBUG < INFO < WARNING < ERROR < CRITICAL。级别配成 INFO 时 DEBUG 不输出——级别是阈值，只有等于或高于它的才会被记录。
3. `__name__` 是模块的完整路径，让日志自动带上来源，并且支持按模块层级分别设置级别。写死字符串就失去了这种层级控制能力。
4. 因为 `basicConfig()` 只有第一次调用生效，多个模块各自配置会互相覆盖，最终行为取决于导入顺序，难以排查。而且配置是部署时的决定，不该由业务模块决定。
5. 那一行不会执行——测试是 `import` 该模块，`__name__` 是模块路径而非 `"__main__"`。
6. **不一样。** WARNING 及以上仍会通过 `logging.lastResort` 输出到 stderr（格式简陋，只有消息本身）；INFO 和 DEBUG 完全不输出，因为 root logger 默认级别是 WARNING。所以不能用「日志没打出来」判断代码没执行到。
7. 不能。日志是给开发者事后排查的，调用方只能拿到返回值。要让调用方知道原因，必须通过返回值或异常传达。
8. 因为两者业务含义不同：文件不存在是正常状态（首次运行），用空记录继续合理；JSON 损坏是异常状态（本该有数据却读不出来），伪装成「没有记录」会掩盖真问题。
9. 因为 logging 只在日志真的要输出时才格式化字符串。用 f-string 的话，即使这条日志被级别过滤掉，拼接也已经执行了，日志量大时是实际的性能开销。

</details>
