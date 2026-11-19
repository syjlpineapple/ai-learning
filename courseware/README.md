# courseware —— 两门每日一课

把跟 ChatGPT 学习的对话整理成两门课，接着往下学：

| 课程 | 原路线 | 编号 | 课表 |
|---|---|---|---|
| **AI 应用开发** | 90 天路线（11-17 调整版） | Day 1 - Day 90，和当时的「第 N 天」一致 | [`ai/README.md`](ai/README.md) |
| **NLP 算法工程师** | 48 周路线（含 RAG 专项） | 第 1 - 90 课，和当时的「第 N 课」一致 | [`nlp/README.md`](nlp/README.md) |

两门课并行，每天各 45 分钟。一天（一课）的顺序都一样：**讲概念 → 演示（代码和真实输出）→ 今天的作业 → 小测**。作业写完把输出发给我，讲评追加到那一天的文件末尾。课文里的结论都在本机跑过，报错是真实的报错。

## 文件结构

```
courseware/
├── README.md                       本文件：总介绍
├── ai/                             AI 应用开发
│   ├── README.md                   课表（自动生成）：每天一行，写好的可以点
│   ├── 1_Python基础/               阶段 1（Day 1-14）
│   │   ├── day01_输入与分支.md     ← 一天一个文件（Day 1-22 的课文还在整理，整理好就放在这一层）
│   │   ├── 加练/                   挂在某一天后面的选做题，文件名是 dayNN_标题.md，带测试
│   │   └── 讲义/                   早先按主题写的讲义（Day 1-10），之后并进每天的课文
│   ├── 2_网络请求与配置/           阶段 2（Day 15-22）
│   ├── 3_工程补充/                 阶段 3（Day 23-25），后面的阶段写到时再建文件夹
│   ├── …
│   └── code/                       加练题的骨架、参考答案和测试（pytest 项目）
├── nlp/                            NLP 算法工程师
│   ├── README.md                   课表（自动生成）
│   ├── 2_传统机器学习/             阶段文件夹，课文是 lessonNN_标题.md（写第 34 课时建）
│   └── …
├── records/                        当时的学习记录（底稿，不再更新）
│   ├── python/                     A 线 Day01-Day22，一天一篇
│   ├── nlp/                        B 线第 1-33 课，按主题合并成 9 篇
│   └── ai_旧版课程大纲.md          早先「33 章讲义」方案的大纲
├── site/                           只给网站用的页面：两门课的课表页、知识点索引、课文模板
├── .vitepress/                     网站配置；两门课的课表数据在 lessons.ts
├── tools/parse_export.py           解析 ChatGPT 导出数据的脚本
└── _raw/                           原始对话（不提交，见文末）
```

几条约定：

- **文件夹就是课表**。阶段文件夹前面带序号，课文文件名前面带补零的编号（`day07`、`lesson34`），在编辑器左侧按名字排序就是学习顺序。
- **作业不放在这里**：AI 应用开发写在仓库根目录的 `dailypractice/DayNN/`，NLP 写在仓库根目录的 `nlp/courseNN/`，和原来一样。
- **课表只在一处维护**：`.vitepress/lessons.ts`。`ai/README.md`、`nlp/README.md`、网站的侧边栏和课表页都由它生成。新写一课，在 lessons.ts 里给那一天加上 `file`，启动一次网站，README 就会更新。
- **新课按 `site/_lesson_template.md` 写**，只用编辑器也认的 Markdown（折叠用 `<details>`），保证不开网站也能看。

## 怎么学

**只看源文件**：在 Kiro 里打开 `ai/README.md` 或 `nlp/README.md`，点进当天的课文，按 `Ctrl+Shift+V` 看排版后的预览。标题、表格、公式、代码、折叠的小测答案都能正常显示，指向代码的链接点了直接在编辑器里打开那个文件。

**打开网站**：多了进度条、做完打勾、跨课搜索和知识点索引。

```powershell
cd courseware
npm install          # 第一次需要，装到 courseware/node_modules（已 gitignore）
npm run docs:dev     # 然后打开终端里显示的地址，默认 http://localhost:5173/
```

网站读的就是上面这些 `.md` 文件，没有另存一份。进度记录存在浏览器的 localStorage 里，只在本机这个浏览器有效。

## 加练的配套代码

`ai/code/` 是一个独立的 pytest 项目，每道加练有骨架（`_exercise.py`）、参考答案（`_solution.py`）和测试。在 `ai/code/` 下运行：

```powershell
python -m pytest     # 全绿（没做的练习显示 skip）
python -m ruff check .
python -m mypy .
```

当前实测结果：

| 检查 | 结果 |
|---|---|
| `pytest`（练习未做） | `722 passed, 316 skipped` |
| `pytest`（用参考答案填满练习） | `1038 passed`，0 skipped |
| `ruff check .` | `All checks passed!` |
| `mypy .` | `Success: no issues found in 76 source files` |

第二行的做法：把代码复制到临时目录，用 `_solution.py` 覆盖 `_exercise.py` 再跑一遍，证明每道题的测试都能被正确答案满足。没做 `pip install -e` 时要用 `python -m pytest`，直接敲 `pytest` 会导入失败。

## 素材从哪来

`records/` 和课文都来自 ChatGPT 的对话：14 个学习相关的会话、589 条消息、约 82 万字，存在 `_raw/conversations.json`，按会话提取的 Markdown 在 `_raw/markdown/`，按日期聚合的课时地图在 `_raw/OUTLINE.md`。账号里其他私人会话没有读取。

**`_raw/` 已写入根目录 `.gitignore`，不要改**：导出数据可能夹带私人内容、当时粘贴进去的 API Key 或内网地址，而本仓库是公开的。流程是「原始素材留在本地 → 整理成课件 → 人工过一遍 → 只提交课件」。

整理时每一节的代码和结论都在本地复跑过，查出了当时没发现的问题，比如 A 线 `Day15`、`Day16` 的 `except ValueError` 是死代码，B 线第 30-32 课那个 0.83 的差距不是过拟合。完整清单见 [`records/python/README.md`](records/python/README.md) 和 [`records/nlp/README.md`](records/nlp/README.md)。这些问题会在对应那一天的课文里用一句「注意」改正。

### 重新导出对话时

用官方导出包时，把 zip 放进 `_raw/`，先体检再提取：

```powershell
$env:PYTHONUTF8=1
# 1. 体检：列出全部会话的标题、时间、消息数、字数，不写任何文件
.\.venv\Scripts\python.exe courseware/tools/parse_export.py inspect courseware/_raw/你的导出包.zip
# 2. 提取：按标题关键字挑出学习相关的会话，转成 Markdown
.\.venv\Scripts\python.exe courseware/tools/parse_export.py extract courseware/_raw/你的导出包.zip `
    --out courseware/_raw/markdown --filter NLP --filter Python
```

体检会打印内容类型分布，出现脚本没见过的类型时，那部分内容会被计入「渲染为空的类型」，看到了要处理，否则会静默丢失。标题对不上关键字时用序号选：`--index 3 --index 7`。

导出文件里每个会话是一棵消息树（编辑提问、重新生成都会留下分支），脚本从 `current_node` 沿 parent 回溯，只还原你最后实际看到的那条对话。
