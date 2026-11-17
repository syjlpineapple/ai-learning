# ai-learning

Python 工程化与 NLP/机器学习的学习记录。每天一节，代码即笔记。

从 `sell-gen` 仓库的 `backend/tests/` 下迁出（2026-11-17），**保留了 10/16 起的全部 23 条原始提交**，
因此 `git log` 可以直接当学习轨迹看。迁出的原因是学习代码和产品代码共用一套工程配置会互相干扰：
产品代码要 `mypy strict`，练习代码本来就该允许写得不漂亮，这两件事无法共存在同一份配置里。

## 目录

```
dailypractice/     A 线：Python 工程化（Day1 - Day22）
nlp/               B 线：NLP 与机器学习（Day3 - course33）
```

## 环境

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
```

`pip install -e .` 会把 `dailypractice` 和 `nlp` 注册成可导入的包，
所以 `from dailypractice.Day22.api_client import APIClient` 在任何目录下都能用。

运行：

```powershell
.\.venv\Scripts\python.exe -m pytest                        # 跑全部测试（当前 10 passed）
.\.venv\Scripts\python.exe -m nlp.course32.course_32        # 跑某节 NLP 课
.\.venv\Scripts\python.exe -m dailypractice.Day10.main      # 跑某个练习脚本
```

脚本要用 `python -m 包.路径` 的形式从仓库根目录运行，不要 `python dailypractice/Day10/main.py`——
后者的 `sys.path` 里没有仓库根，找不到 `dailypractice` 包。

Windows 控制台打印中文出现乱码时，设 `$env:PYTHONUTF8=1` 即可，不是代码问题。

## 学习路径

### A 线：Python 工程化（10/16 - 11/13）

载体是同一个「猜数字」项目，持续加码：

| 阶段 | 内容 | 关键跃迁 |
|---|---|---|
| Day1-6 | input/while、try-except、函数抽取、类型注解 | 从「能跑」到「有函数」 |
| Day7-10 | assert 断言、三文件拆分（logic / main / test） | 逻辑与 IO 分离 |
| Day11-14 | json 读写、`ensure_ascii`、tempfile 隔离、logging、分层校验 | 同一个 `history.py` 重写 4 遍 |
| Day15-17 | requests、timeout、`raise_for_status`、异常分类、docstring | 异常处理从 print 升级到 `logger.exception` + `raise` |
| Day18-20 | dotenv、多环境 `.env.{env}`、override 规则、`APIClient` 类 + Session 复用 | 散函数升级为类 |
| Day21-22 | MagicMock、`side_effect`、`assert_called_once_with`、`pytest.raises`、`@fixture` | 从 assert 到真正的单元测试 |

### B 线：NLP 与机器学习（10/20 - 11/16）

| 阶段 | 内容 |
|---|---|
| 数学地基 | numpy shape / `mean(axis)`、点积、`@` 矩阵乘法；**手推导数** `2x(wx-y)` 跑梯度下降 |
| 向量化原理 | 分词 → 词表 → one-hot 词袋 → 余弦相似度 → TF → IDF → TF-IDF，全部先手算再换 sklearn |
| 特征解读 | `argmax` 找最高权重词、`np.isclose` 处理浮点相等 |
| 完整流程 | jieba 接入 `TfidfVectorizer`、`train_test_split(stratify=)`、逻辑回归、`predict_proba` |
| 模型评估 | 手推 TP/FP/TN/FN 与 P/R/F1 公式再用代码验证；未登录词检查；阈值调整改变 P/R 平衡 |
| 过拟合与正则化 | 训练/测试准确率 gap、扫 C 值、`norm(model.coef_)` 观察权重大小 |

学得对的地方，值得继续保持：

- **先手算，再调库。** `day_7` 手算 TF-IDF，`day_8` 换 sklearn 发现数字对不上，自己查出原因是 L2 归一化。
- **同一主题反复重写，每遍都有改进。** `history.py` 四遍、`api_client` 两遍，不是复制粘贴。
- **疑问留痕并闭环。** `course_28` 注释里的三个问号，在 `course29/model_b.py` 里给出了答案。
- **自己发现了数据泄漏。** `course_27` 先 `fit_transform(全量)` 再划分，`course_28` 改成先划分再 fit。

## 待办

### 立刻（Day23 热身）

当前 `ruff check .` 有 14 个告警，全是无用 import 和 `except ... as e` 里没用到的 `e`
（`logger.exception` 自己会带 traceback，不需要 `as e`）。都不是 bug，故意留着没动：
自己跑一遍 `ruff check . --diff` 看它想改什么，再 `--fix`，比直接看结果学得多。

### A 线下一步：补上和真实项目的断层

按与实际开发的相关度排，不是按教材顺序：

1. **`async` / `await`** — 最大的断层。现在的 `APIClient` 是同步 `requests`，
   而真实的 FastAPI 项目全是异步的。建议把 `APIClient` 改成 `httpx.AsyncClient` + `pytest-asyncio`。
2. **Pydantic** — 用 Pydantic 模型重写 `Day14` 的 history 校验，顺便学 `pydantic-settings`
   的 `extra` 行为（这次迁移的起因之一就是不了解它导致主项目配置校验失败）。
3. **自定义异常类** — `Day14` 的测试里用 `assert str(e) == "类型错误"` 把测试和中文文案焊死了，
   改一个字测试就断。应该定义 `class HistoryFormatError(ValueError)` 按类型断言。
4. **`pytest.mark.parametrize`** — 能把 `Day14` 那一堆重复的 try/except 压缩成一张表。
5. 自己写上下文管理器（`__enter__` / `@contextmanager`）、`dataclass`、生成器、mypy。

另外两个一直在用 `type(x) != list` 的地方（Day12、Day14）该换成 `isinstance`，子类会判错。

### B 线下一步：先把结论变可信，再学新东西

**当前所有实验的数据量不足，结论不成立。** 24-32 条样本、测试集 6-8 条，
准确率的最小刻度是 1/6 ≈ 16.7%。`course32` 实测 C=100 时训练准确率 1.0、测试 0.167、gap 0.83，
这个 gap 里噪声远大于信号，换个 `random_state` 结论就翻。所以：

1. **`Pipeline` + `cross_val_score`** — Pipeline 把向量化和模型串起来，
   从源头消除 `course_27` 那类数据泄漏；交叉验证能部分缓解小样本。
   顺带 `GridSearchCV` 正是 `course31/32` 手工 for 循环扫 C 值要的东西。
2. **换真实数据集** — 几千条起（如 ChnSentiCorp）。然后把 course28-32 的实验**全部重跑一遍**，
   对照结论变了没有。这一步比学新知识点收获大。
3. **`ngram_range=(1,2)`** — 数据里有「不好」「不值得购买」「一点都不耐用」，
   单字词袋抓不住否定，bigram 才行。顺带 `min_df` / `max_df` / `stop_words`。
4. **基线模型对比** — `MultinomialNB`、`LinearSVC`。不比就不知道逻辑回归到底好不好。
5. `joblib` 持久化，之后才是 embedding → 预训练模型微调。

### 最该做的一件事：让学习成果真正落地

学了一个月 NLP，`sell-gen` 的 `backend/app/` 里**没有一行 jieba / sklearn / numpy**。
而那边有现成的落地点：

- `app/agents/ad_law_checker.py` — 纯正则匹配判断文案是否违规，**本质就是二分类任务**
- `app/agents/draft_scorer.py` — 纯词库 + 字符串匹配打分，「转化潜力」维度本质是回归/排序

建议做个闭环小项目：从 `generation_history` 表取真实记录加人工标注，
训练 TF-IDF + 逻辑回归分类器，和现有规则引擎做 A/B 对比。
这一件事同时用到 A 线（SQLAlchemy 取数、Pydantic、异步接口、pytest）
和 B 线（分词、向量化、训练、P/R/F1 评估），而且数据是真的、量够、产出能进产品代码。

## 记录习惯

每个阶段建议补一句「学了什么、踩了什么坑、还有什么没搞懂」。
`course_28` 里那三个问号是靠三天后 `course29` 的注释回答的——
这种闭环如果不记下来，三个月后会重新踩一遍。

## 注意

本仓库是公开仓库。`Day19` / `Day20` 下已入库的 `.env.development` 等文件里是
`dev-123456` 这类假值，仅用于演示多环境加载顺序。
以后练习要用真实的 API Key，一律写进 `.env.local`（已在 `.gitignore` 中），不要提交。

## 迁移时做过的改动

迁移只改「迁移导致失效的」和「本来就跑不通的」，不动风格问题：

| 文件 | 改动 | 原因 |
|---|---|---|
| Day12/13/14/20/21/22 | `tests.dailypractice.X` → `dailypractice.X` | 包路径变了 |
| Day10/main.py、Day10/test_game.py、Day11/test_history.py | 裸导入改为完整包路径 | 原来只在「cd 到该目录直接运行」时有效，pytest 下一直是 ImportError |
| Day20/main.py | 删掉 `import post` | `post` 是 `APIClient` 的方法，没有模块级 `post`，实测 ImportError |
| Day22/test_api_client.py | 删掉 `assert resp.status_code == 200` | `post()` 返回 `response.json()`（dict），dict 没有 `status_code`，实测 AttributeError |
| Day18/.env | 新建（假值） | 原来依赖 `backend/.env`，迁出后需要自带配置 |

`Day11/history.json` 是运行产物，原仓库里本来就没提交，已加入 `.gitignore`，
跑一次 `python -m dailypractice.Day11.history` 就会重新生成。
