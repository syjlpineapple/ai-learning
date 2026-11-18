# courseware —— 把 ChatGPT 学习对话整理成课件

目标：代码只能说明「最后写成了什么」，说不清「为什么这么写、当时错在哪、背后的理论是什么」。
这部分全在 ChatGPT 的对话里。把它们提取出来做成课件，用于日后复习，也可以给别人学。

## 目录约定

```
courseware/
  tools/parse_export.py   解析 ChatGPT 官方导出的脚本
  _raw/                   原始导出包与提取出的 Markdown（不入库，见下）
  python/                 A 线学习记录，22 节，按学习日编号
  nlp/                    B 线学习记录，9 节，按阶段合并
  course/                 系统化课程（在建），可对外、带配套代码
    python-engineering/   《Python 工程化实战》33 章
```

**三者的关系**：`_raw/` 是原始素材，`python/` 和 `nlp/` 是按学习轨迹整理的**学习记录**，`course/` 是在学习记录基础上重组、补齐、配上可运行代码的**课程**。前两者已完成，`course/` 正在建设。

`_raw/` 已写入根目录 `.gitignore`。**原因是安全的，不要改**：
ChatGPT 的数据导出是账号下**全量**对话，不只是学习相关的那几个会话，
里面可能有私人内容、你当时粘贴进去的 API Key 或内网地址。本仓库是公开仓库。
流程是「原始素材留在本地 → 整理成课件 → 人工过一遍 → 只提交课件」。

## 拿到导出包后怎么做

OpenAI 的邮件说可能要几天，实际通常几分钟到一小时就会收到第二封带下载链接的邮件，
链接一般 24 小时内有效，收到后尽快下载。把 zip 放进 `courseware/_raw/`，然后：

```powershell
$env:PYTHONUTF8=1

# 1. 体检：列出全部会话的标题、时间、消息数、字数，不写任何文件
.\.venv\Scripts\python.exe courseware/tools/parse_export.py inspect courseware/_raw/你的导出包.zip

# 2. 提取：按标题关键字挑出学习相关的会话，转成 Markdown
.\.venv\Scripts\python.exe courseware/tools/parse_export.py extract courseware/_raw/你的导出包.zip `
    --out courseware/_raw/markdown --filter NLP --filter Python
```

先 `inspect` 再 `extract`，不要跳过第一步：导出格式 OpenAI 改过几次，
体检会打印内容类型分布，如果出现脚本没见过的新类型，那一行会被统计进
「渲染为空的类型」，看到了就说一声，否则那部分内容会静默丢失。

标题对不上关键字时，用体检给出的序号直接选：`--index 3 --index 7`。

## 脚本为什么不是简单的 JSON 转 Markdown

导出文件里每个会话不是消息列表，而是一棵消息树（`mapping` 字段，节点用 parent/children 相连）。
每次编辑提问或点「重新生成」，旧那条回答会作为另一条分支留在树里。
`current_node` 指向你最后实际看到的叶子节点。

所以脚本从 `current_node` 沿 parent 回溯来还原对话。
直接遍历 `mapping` 的所有节点，会把你当初抛弃的回答一起塞进课件。
体检输出里的「弃支」一列就是被丢掉的节点数。

## 素材现状

对话已经通过浏览器调试接口取回，没有用 OpenAI 的邮件导出（那边排队太久）。
取回的数据结构和官方 `conversations.json` 完全一致，所以上面的脚本通用。

- **14 个会话、589 条消息、约 82 万字**，存于 `_raw/conversations.json`
- 只取学习相关的会话：Python 线 5 个、NLP 线 6 个、配套单点提问 3 个。
  账号里另外 107 个私人会话（薪资、体检、理财之类）一律没有读取
- 按会话提取的 Markdown 在 `_raw/markdown/`，按日期聚合的课时地图在 `_raw/OUTLINE.md`

比官方导出包更干净：不夹带私人对话，且页面组件标签已清理。

## 课件切分

按**课时**切分，和代码一一对应，不按原会话切——两个最大的会话各有 19 万字、横跨十几天，
直接当课件没法用。

```
courseware/python/Day01.md ...     A 线，一课一文件（22 个），对齐 dailypractice/DayN.py
courseware/nlp/01_xxx.md    ...     B 线，按阶段合并（9 个），每节标注覆盖的课时
```

A 线的编号对齐规则见 [`python/README.md`](python/README.md)（和对话里的「Day N」差一位）。

B 线没有按「一课一文件」切。前 17 课是一条连续的数学链条（向量 → 点积 → 损失 → 导数 → 梯度 →
梯度下降），每课只有一个概念加一道选择题，拆成 17 个文件会把推导割断。
分节依据和课时↔代码映射见 [`nlp/README.md`](nlp/README.md)。

## 完成状态

**两条线全部整理完毕，共 31 节、约 60 万字。**

| 线 | 节数 | 覆盖 | 索引 |
|---|---:|---|---|
| **A 线** Python 工程化 | **22** | Day01 - Day22，对齐 `dailypractice/DayN.py` | [`python/README.md`](python/README.md) |
| **B 线** NLP 与机器学习 | **9** | 第 1-33 课，从向量到交叉验证 | [`nlp/README.md`](nlp/README.md) |

每节都是两部分：

**第一部分 · 知识讲解** —— 当成教材读，不依赖原始对话也能看懂。概念、公式推导、为什么这样做。
**第二部分 · 当时的练习** —— 代码演进、踩的坑、小测题目与答案、复习自测（带折叠答案）。

## 整理时顺手做的事：全部实测复跑

课件不是对话的转录。每一节的代码和结论我都在本地跑过，**查出若干当时没发现、或者当时结论不对的地方**。

A 线 5 个真问题（详见 [`python/README.md`](python/README.md)）：

| | 问题 |
|---|---|
| `Day7.py` | 没调用 `test_check_num()`，测试根本没执行 |
| `Day10/test_game.py` | `pytest` → `collected 0 items`（断言写在 `if __name__ == "__main__"` 里） |
| `Day12/history.py` | 缺 `encoding="utf-8"` → `UnicodeDecodeError: 'gbk' codec`（`PYTHONUTF8=1` 会掩盖） |
| `Day15`、`Day16` | `except ValueError` 是死代码（`JSONDecodeError` 同时继承 `RequestException` 和 `ValueError`） |

B 线 5 个发现（详见 [`nlp/README.md`](nlp/README.md)）：

| | 发现 |
|---|---|
| 05 | 手算和 sklearn 的差异**有两处**，L2 归一化掩盖了 TF 定义的那一处 |
| 06 | 数据泄漏的实际后果：规范写法下测试集出现**全零向量**，100% 准确率靠截距猜的 |
| 07 | `max_iter=10` **不是**根因（`n_iter_=[5]` 就收敛）；真根因是情感词全部未登录；还查到一条**标注错误** |
| 08 | 那个 0.83 的 gap **不是过拟合**（预测取反能拿 0.83）；L1 在 `C=1` 时把 37 个权重全压成 0 |
| 09 | 交叉验证自己也不稳（换种子平均分在 0.15~0.38 漂）；用 CV 选 `C` 选出来的是噪声 |

**反复出现的一个教训：结果对了不代表过程对了。** 05、07、09 三节各撞了一次。

## 怎么用这份课件

- **复习**：直接读第一部分，每节末尾的「复习自测」用来检验（答案在折叠块里）
- **重学**：按 README 的索引顺序走，A 线和 B 线互不依赖，可以并行
- **查某个坑**：两条线的 README 里都有问题清单，按现象搜

---

## 系统化课程（`course/`，在建）

学习记录按「当时怎么学的」组织，有个人痕迹、有缺口、代码带已知 bug。要给别人学，需要重组一遍。

`course/python-engineering/` 是这件事的产物：**《Python 工程化实战》，33 章 + 3 篇附录 + 配套代码仓**。

| | 学习记录 `python/` | 课程 `course/python-engineering/` |
|---|---|---|
| 编号 | 按学习日（Day01-Day22） | 按知识模块（M0-M8） |
| 顺序 | 当时怎么学的 | 怎么教更顺 |
| 内容 | 含个人练习、小测、提问 | 只留可复用的知识与练习 |
| 完整性 | 缺字典、类、装饰器、虚拟环境 | **补 6 章新内容** |
| 练习 | 回忆型自测 | **分级动手题 + 参考答案 + 自动验证** |
| 代码 | 练习状态，含 5 个已知 bug | 修正版，`pytest` / `ruff` / `mypy` 全过 |

### 当前进度：17 / 33 章（3.3 起为精简版）

- [x] 课程总览与 33 章大纲 —— [`course/python-engineering/README.md`](course/python-engineering/README.md)
- [x] **M0 开始之前**（2 章）：[0.1 这门课怎么学](course/python-engineering/00_01_怎么学.md)、[0.2 环境准备](course/python-engineering/00_02_环境准备.md)
- [x] **M1 语言基础 1.1 - 1.5**：[三种结构与输入输出](course/python-engineering/01_01_程序的三种结构.md)、[条件分支与真值测试](course/python-engineering/01_02_条件分支与真值测试.md)、[循环与四个结束](course/python-engineering/01_03_循环与四个结束.md)、[模块与字符串格式化](course/python-engineering/01_04_模块与字符串格式化.md)、[异常处理入门](course/python-engineering/01_05_异常处理入门.md)、[函数](course/python-engineering/01_06_函数.md)、[列表](course/python-engineering/01_07_列表.md)、[字典元组集合](course/python-engineering/01_08_字典元组集合.md)、[内置函数与边界条件](course/python-engineering/01_09_内置函数与边界条件.md) —— **M1 完成**
- [x] **M2 测试入门**：[2.1 assert 与自动化测试](course/python-engineering/02_01_assert与自动化测试.md)、[2.2 异常体系与 raise](course/python-engineering/02_02_异常体系与raise.md)、[2.3 从 assert 到 pytest](course/python-engineering/02_03_从assert到pytest.md) —— **M2 完成**
- [x] **M3 工程结构**：[3.1 模块、包与 import 机制](course/python-engineering/03_01_模块包与import机制.md)、[3.2 类与面向对象](course/python-engineering/03_02_类与面向对象.md)、[3.3 项目分层与职责划分](course/python-engineering/03_03_项目分层与职责划分.md) ⚡ —— **M3 完成**
- [x] 配套代码仓（`pyproject.toml` + M0-M3 模块 + 547 条测试 + 环境自检脚本）
- [ ] M4 - M8（16 章，精简版）← 下一步：M4 数据持久化
- [ ] 附录 A 常见错误手册
- [ ] 第二门课：机器学习数学地基（取 B 线 01-04 节）

**按课程顺序推进**，所以任何时候前 N 章都是完整可学的。

### 配套代码的质量标准

每一章的代码都要满足：

```powershell
pytest          # 全绿（未做的练习显示 skip）
ruff check .    # 零告警
mypy .          # 零错误
```

当前实测结果：

| 检查 | 结果 |
|---|---|
| `pytest`（练习未做） | `439 passed, 108 skipped` |
| `pytest`（**用参考答案填满练习**） | `547 passed`，**0 skipped** |
| `ruff check .` | `All checks passed!` |
| `mypy .` | `Success: no issues found in 43 source files` |

> 这里的 `pytest` 指在 `code/` 下运行 `python -m pytest`。没做 `pip install -e` 的环境里直接敲 `pytest` 会导入失败，原因见第 3.1 章第 9 节。

108 个 skipped 是故意的——那是留给学习者的练习，没做完就显示 skip。

第二行是一条额外的验证：把代码复制到临时目录、用每章的 `_solution.py` 覆盖 `_exercise.py` 再跑一遍。它证明了**每一道练习的测试都是可以被正确答案满足的**，不存在「怎么写都过不了」的测试。每次新增章节都要重跑这一步。

### 为什么 B 线只取前 4 节

B 线数学地基那 4 节（向量 → 损失 → 梯度 → 梯度下降）质量过硬，可以独立成课。

但建模那 4 节（第 24-33 课）的实验结论**全部不成立**：24~32 条手造数据、测试集 6 条。实测证据是换一个随机种子，交叉验证的平均准确率就在 0.15~0.38 之间漂，而调超参数的影响比改种子还小。拿这个教人会传递错误的经验。

**那部分要重做，必须先换成真实数据集**（ChnSentiCorp、waimai_10k 之类，几千到上万条），把第 27-33 课的实验重跑一遍。
