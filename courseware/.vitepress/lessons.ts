// 两门课的课表：网站的侧边栏、上一课/下一课、课表页、进度条、左边目录的打勾，
// 还有 ai/README.md、nlp/README.md 两份课表（由 readme.ts 生成），都从这里来。
//
// 一个 Lesson 就是一天（AI 应用开发）或一课（NLP），编号和当时跟 ChatGPT 学的一致。
// file 是课文在 courseware/ 下的路径；没有 file 表示还没写，只出现在课表里。
// extras 是挂在这一天下面的附加材料（加练题）；Stage.extras 是整个阶段共用的（旧讲义、学习记录）。

export interface Lesson {
  n: string           // 编号：'23'（Day 23 / 第 23 课）、'预备1'、'0.1'（讲义章号）
  title: string
  file?: string
  goal?: string       // 课表里的「学会什么」
  project?: string    // 这一天交付哪个作品项目
  note?: string       // 课表里的补充说明
  record?: string     // 当时的学习记录，courseware/ 下的路径
  extras?: Lesson[]
}

export interface Stage {
  id: string
  title: string
  range: string       // 「Day 1-14」「第 24-40 课」
  folder: string      // 这一阶段的课文放在哪个文件夹
  note?: string
  lessons: Lesson[]
  extras?: { title: string; note?: string; items: Lesson[] }
}

export interface Course {
  id: 'ai' | 'nlp'
  title: string
  route: string       // 原路线
  desc: string
  dir: string         // 课程文件夹：ai、nlp
  home: string        // 网站上的课表页
  prefixes: string[]  // 哪些路径下的页面属于这门课
  homework: string    // 作业写在哪
  stages: Stage[]
}

export const REPO = 'https://github.com/syjlpineapple/ai-learning'

export function linkOf(file: string): string {
  return '/' + file.replace(/\.md$/, '')
}

/** 不发布到网站的文件（A 线学习记录）指向 GitHub，其余是站内地址 */
export function urlOf(file: string): string {
  return file.startsWith('records/python/') ? `${REPO}/blob/main/courseware/${file}` : linkOf(file)
}

// ---------------------------------------------------------------------------
// AI 应用开发（原 90 天路线，2026-11-17 调整版）
// ---------------------------------------------------------------------------

const S1 = 'ai/1_Python基础/'
const S2 = 'ai/2_网络请求与配置/'
const REC = 'records/python/'

const lecture = (n: string, title: string, name: string): Lesson =>
  ({ n, title, file: `${S1}讲义/${name}.md` })
const drill = (stage: string, day: number, title: string, name = title): Lesson =>
  ({ n: '练', title, file: `${stage}加练/day${String(day).padStart(2, '0')}_${name}.md` })

const ai: Course = {
  id: 'ai',
  title: 'AI 应用开发',
  route: '90 天路线（11-17 调整版）',
  desc: '从一个猜数字程序开始，一路做到带 RAG、Agent、数据库和部署的 AI 应用。',
  dir: 'ai',
  home: '/ai/',
  prefixes: ['/ai/'],
  homework: '仓库根目录的 `dailypractice/DayNN/`（和原来一样）',
  stages: [
    {
      id: '1',
      title: 'Python 基础',
      range: 'Day 1-14',
      folder: '1_Python基础',
      lessons: [
        { n: '1', title: '输入与分支', goal: 'input()、类型转换、if / elif / else', record: REC + 'Day01.md' },
        { n: '2', title: 'while 循环', goal: '循环、break、continue', record: REC + 'Day01.md' },
        { n: '3', title: '随机数与模块导入', goal: 'import、random、f-string', record: REC + 'Day02.md' },
        { n: '4', title: '计数器与异常处理', goal: '计数、try / except、校验输入', record: REC + 'Day03.md' },
        { n: '5', title: '函数与职责分离', goal: 'def、返回值、类型注解', record: REC + 'Day04.md' },
        { n: '6', title: '列表与数据记录', goal: '列表、切片、可变与引用', record: REC + 'Day05.md' },
        { n: '7', title: '统计函数与边界条件', goal: 'len / max / min / sum、空列表、守卫语句', record: REC + 'Day06.md' },
        { n: '8', title: 'assert 与自动化测试', goal: '不启动游戏也能验证函数', record: REC + 'Day07.md' },
        { n: '9', title: '异常分类与异常链', goal: 'raise、异常层次、from None、测异常', record: REC + 'Day09.md' },
        { n: '10', title: '模块拆分与程序入口', goal: '拆成三个文件、if __name__、python -m', record: REC + 'Day10.md' },
        { n: '11', title: '文件读写与 JSON', goal: 'with open、encoding、JSON 读写与校验', record: REC + 'Day11.md',
          extras: [drill(S1, 11, '排行榜存盘'), drill(S1, 11, 'JSON 存档', 'JSON存档')] },
        { n: '12', title: '测试覆盖与异常粒度', goal: '六种场景都测到、临时目录隔离', record: REC + 'Day12.md',
          extras: [drill(S1, 12, '不信任读进来的数据')] },
        { n: '13', title: '日志与返回值的语义', goal: 'logging、都返回 [] 的歧义', record: REC + 'Day13.md',
          extras: [drill(S1, 13, '用日志代替 print', '用日志代替print')] },
        { n: '14', title: '错误语义与异常继承', goal: '返回空值还是抛异常、自定义异常', record: REC + 'Day14.md',
          extras: [drill(S1, 14, '该返回空值还是抛异常', '返回空值还是抛异常')] },
      ],
      extras: {
        title: '讲义（旧版）',
        note: '早先按主题写的讲义，覆盖 Day 1-10。Day 1-14 每天一页写好以后，这里的内容会并进去。',
        items: [
          lecture('0.1', '这门课怎么学', '00_01_怎么学'),
          lecture('0.2', '环境准备', '00_02_环境准备'),
          lecture('1.1', '程序的三种结构', '01_01_程序的三种结构'),
          lecture('1.2', '条件分支与真值测试', '01_02_条件分支与真值测试'),
          lecture('1.3', '循环与四个结束', '01_03_循环与四个结束'),
          lecture('1.4', '模块与字符串格式化', '01_04_模块与字符串格式化'),
          lecture('1.5', '异常处理入门', '01_05_异常处理入门'),
          lecture('1.6', '函数', '01_06_函数'),
          lecture('1.7', '列表', '01_07_列表'),
          lecture('1.8', '字典、元组、集合', '01_08_字典元组集合'),
          lecture('1.9', '内置函数与边界条件', '01_09_内置函数与边界条件'),
          lecture('2.1', 'assert 与自动化测试', '02_01_assert与自动化测试'),
          lecture('2.2', '异常体系与 raise', '02_02_异常体系与raise'),
          lecture('2.3', '从 assert 到 pytest', '02_03_从assert到pytest'),
          lecture('3.1', '模块、包与 import 机制', '03_01_模块包与import机制'),
          lecture('3.2', '类与面向对象', '03_02_类与面向对象'),
          lecture('3.3', '项目分层与职责划分', '03_03_项目分层与职责划分'),
        ],
      },
    },
    {
      id: '2',
      title: '网络请求与配置',
      range: 'Day 15-22',
      folder: '2_网络请求与配置',
      lessons: [
        { n: '15', title: 'HTTP 请求与 requests 异常', goal: 'requests.get、timeout、异常树', record: REC + 'Day15.md',
          extras: [drill(S2, 15, '查询排行榜'), drill(S2, 15, '失败分类')] },
        { n: '16', title: '请求参数与异常分层', goal: 'params、except 的顺序', record: REC + 'Day16.md',
          extras: [drill(S2, 16, '失败了就重试')] },
        { n: '17', title: 'POST 请求', goal: 'json= 与 data=、logger.exception + raise', record: REC + 'Day17.md',
          extras: [drill(S2, 17, '上传成绩')] },
        { n: '18', title: '环境变量与密钥', goal: '.env、load_dotenv、密钥不进代码', record: REC + 'Day18.md',
          extras: [drill(S2, 18, '读配置')] },
        { n: '19', title: '多环境配置', goal: 'APP_ENV、两段式加载、override', record: REC + 'Day19.md',
          extras: [drill(S2, 19, '多环境配置')] },
        { n: '20', title: 'APIClient 与分层', goal: 'Session、配置 / 请求 / 入口三层、finally', record: REC + 'Day20.md',
          extras: [drill(S2, 20, 'APIClient'), drill(S2, 20, '程序入口')] },
        { n: '21', title: '单元测试与 Mock', goal: 'MagicMock、side_effect、检查调用', record: REC + 'Day21.md',
          extras: [drill(S2, 21, '用 Mock 测 APIClient', '用Mock测APIClient')] },
        { n: '22', title: 'Fixture 与测试资源', goal: 'yield、作用域、pytest.raises', record: REC + 'Day22.md',
          extras: [drill(S2, 22, '装饰器'), drill(S2, 22, '给测试搭环境')] },
      ],
    },
    {
      id: '3',
      title: '工程补充',
      range: 'Day 23-25',
      folder: '3_工程补充',
      lessons: [
        { n: '23', title: '参数化测试与 pydantic 入门', goal: '一组数据跑同一个测试；用模型声明数据的样子',
          file: 'ai/3_工程补充/day23_参数化测试与pydantic.md' },
        { n: '24', title: 'pydantic 进阶', goal: '嵌套模型、直接从 JSON 校验、自定义规则；重写 Day 14 的读历史记录',
          file: 'ai/3_工程补充/day24_pydantic进阶.md' },
        { n: '25', title: '给 AI 应用搭项目骨架', goal: 'pyproject、依赖分组、锁版本，后面 65 天都在这个骨架上加东西' },
      ],
    },
    {
      id: '4',
      title: '大模型 API',
      range: 'Day 26-45',
      folder: '4_大模型API',
      lessons: [
        { n: '26', title: '第一次调用大模型', goal: 'OpenAI 兼容接口、密钥放 .env、messages 的结构', note: '从这一天起需要 API 密钥' },
        { n: '27', title: '请求参数改变了什么', goal: 'temperature、max_tokens、top_p，同一个问题问十遍看差别' },
        { n: '28', title: '提示词设计（一）', goal: '角色、任务、格式、示例四件事' },
        { n: '29', title: '提示词设计（二）', goal: '少样本、分步骤、让模型说「不知道」' },
        { n: '30', title: '多轮对话', goal: '消息历史怎么存、怎么传，模型自己不记得上一句' },
        { n: '31', title: '上下文长度与 token', goal: '数 token、历史太长时截断还是总结' },
        { n: '32', title: '成本', goal: '按 token 计费，估算一次对话多少钱，怎么省' },
        { n: '33', title: '流式输出（一）', goal: 'SSE，一段一段地收、一段一段地显示' },
        { n: '34', title: '流式输出（二）', goal: '中途断开、超时、拼出完整结果' },
        { n: '35', title: '结构化输出（一）', goal: '让模型返回 JSON，用 pydantic 校验' },
        { n: '36', title: '结构化输出（二）', goal: '校验失败时带着错误信息让模型重来' },
        { n: '37', title: '大模型的错误处理', goal: '限流、超时、服务端错误，接上 Day 15-16' },
        { n: '38', title: '给大模型客户端分层', goal: '配置、客户端、业务三层，接上 Day 20' },
        { n: '39', title: '模型说的不一定对', goal: '哪些输出要程序再检查一遍' },
        { n: '40', title: '提示词注入', goal: '亲手注入一次，再挡住它' },
        { n: '41', title: '敏感信息', goal: '什么不能进提示词，日志里不留密钥和隐私' },
        { n: '42', title: '换一家模型', goal: '同一套代码切换不同厂商：适配层' },
        { n: '43', title: '用测试守住提示词', goal: '固定样例 + 检查输出格式，改提示词不怕改坏' },
        { n: '44', title: '阶段项目：AI 助手（一）', goal: '多轮对话、按指定格式输出', project: 'AI 助手' },
        { n: '45', title: '阶段项目：AI 助手（二）', goal: '收尾、README、演示', project: 'AI 助手' },
      ],
    },
    {
      id: '5',
      title: 'RAG 知识库',
      range: 'Day 46-65',
      folder: '5_RAG知识库',
      lessons: [
        { n: '46', title: 'RAG 是什么', goal: '模型为什么需要外部资料，整体流程' },
        { n: '47', title: '读文档', goal: 'TXT、Markdown、PDF' },
        { n: '48', title: '文本清洗', goal: '页眉页脚、空行、乱码' },
        { n: '49', title: '切块（一）', goal: '按长度切，chunk size 和 overlap' },
        { n: '50', title: '切块（二）', goal: '按段落和标题切，保留来源信息' },
        { n: '51', title: '调用 embedding', goal: '把文本变成向量（原理在 NLP 第 48 课）' },
        { n: '52', title: '相似度检索', goal: '余弦、Top-K，先用 numpy 手写一遍' },
        { n: '53', title: '向量数据库', goal: 'Chroma 存、查、删' },
        { n: '54', title: '元数据过滤', goal: '按文档、日期筛选' },
        { n: '55', title: '把资料交给模型', goal: '检索结果怎么拼进提示词' },
        { n: '56', title: '引用来源', goal: '回答里标出出自哪一段' },
        { n: '57', title: '资料里没有怎么办', goal: '相似度阈值，让它说「资料里没有」' },
        { n: '58', title: '检索评估', goal: '命中率、召回率，接上 NLP 的 P/R' },
        { n: '59', title: '答案评估', goal: '建测试集，人工评分和自动评分' },
        { n: '60', title: '混合检索', goal: '关键词 + 向量' },
        { n: '61', title: '重排序', goal: '先多找，再挑最相关的' },
        { n: '62', title: '增量更新', goal: '文档改了，索引怎么跟着改' },
        { n: '63', title: '权限与隐私', goal: '每个人只能查到自己能看的文档' },
        { n: '64', title: '阶段项目：知识库助手（一）', goal: '根据你的文档回答问题', project: '知识库助手' },
        { n: '65', title: '阶段项目：知识库助手（二）', goal: '评估报告与改进', project: '知识库助手' },
      ],
    },
    {
      id: '6',
      title: 'Agent 与工具调用',
      range: 'Day 66-78',
      folder: '6_Agent与工具调用',
      lessons: [
        { n: '66', title: '工具调用', goal: '让模型决定调哪个函数' },
        { n: '67', title: '描述工具', goal: '用 pydantic 写工具的参数说明，并校验模型给的参数' },
        { n: '68', title: '完整的一个回合', goal: '执行工具，把结果还给模型' },
        { n: '69', title: '多步骤任务', goal: '循环到模型说完成为止' },
        { n: '70', title: '防止失控', goal: '最多几步、超时、出错怎么停' },
        { n: '71', title: '工具权限', goal: '哪些操作要人确认' },
        { n: '72', title: '知识库变成工具', goal: '把 RAG 交给 Agent 用' },
        { n: '73', title: 'LangGraph 入门', goal: '把流程画成图' },
        { n: '74', title: 'LangGraph：状态与分支', goal: '根据中间结果走不同的路' },
        { n: '75', title: 'LangGraph：中断与人工确认', goal: '执行到一半停下，等人确认再继续' },
        { n: '76', title: '记录与回放', goal: '每一步做了什么、花了多少' },
        { n: '77', title: '评估 Agent', goal: '任务完成率、步数、成本' },
        { n: '78', title: '阶段项目：多步骤助手', goal: '能查资料、能计算、关键操作要确认', project: '多步骤助手' },
      ],
    },
    {
      id: '7',
      title: '完整 AI 应用',
      range: 'Day 79-90',
      folder: '7_完整AI应用',
      lessons: [
        { n: '79', title: 'FastAPI 入门', goal: '第一个接口' },
        { n: '80', title: '请求与响应模型', goal: 'pydantic + FastAPI' },
        { n: '81', title: '流式接口', goal: '把大模型的流式输出转给前端' },
        { n: '82', title: '数据库', goal: 'SQLite 存对话记录' },
        { n: '83', title: '会话管理', goal: '会话 ID、读取历史' },
        { n: '84', title: '认证', goal: 'API Key 与简单登录' },
        { n: '85', title: '接口测试', goal: 'TestClient，测试放进功能里一起写' },
        { n: '86', title: '界面', goal: 'Streamlit 做一个能用的页面' },
        { n: '87', title: '日志、监控与成本统计', goal: '每次调用记下耗时、token 和费用' },
        { n: '88', title: '部署', goal: 'Docker 打包运行' },
        { n: '89', title: '毕业项目（一）', goal: '选一个真实需求，整合前面的能力', project: '毕业项目' },
        { n: '90', title: '毕业项目（二）', goal: '可运行、可演示、有文档', project: '毕业项目' },
      ],
    },
  ],
}

// ---------------------------------------------------------------------------
// NLP 算法工程师（原 48 周路线，含 11-13 加入的 RAG 专项）
// ---------------------------------------------------------------------------

const NREC = 'records/nlp/'
const record = (title: string, name: string): Lesson => ({ n: '记录', title, file: `${NREC}${name}.md` })

const nlp: Course = {
  id: 'nlp',
  title: 'NLP 算法工程师',
  route: '48 周路线（含 RAG 专项）',
  desc: '从向量和梯度讲起，经过传统机器学习、词向量、PyTorch，到 Transformer 微调和 RAG。',
  dir: 'nlp',
  home: '/nlp/',
  prefixes: ['/nlp/', '/records/nlp/'],
  homework: '仓库根目录的 `nlp/courseNN/`（和原来一样）',
  stages: [
    {
      id: '1',
      title: '数学与文本向量化',
      range: '第 1-23 课',
      folder: '1_数学与文本向量化',
      lessons: [
        { n: '预备1', title: 'NumPy 数组', goal: 'shape、axis、mean' },
        { n: '预备2', title: '矩阵乘法', goal: 'X @ w 与形状' },
        { n: '1', title: '数学公式在描述什么', goal: '公式就是把一件事写成符号' },
        { n: '2', title: '变量', goal: '变量和权重的区别' },
        { n: '3', title: '函数', goal: '模型就是一个把输入变成输出的函数' },
        { n: '4', title: '参数', goal: '模型要学的就是参数' },
        { n: '5', title: '损失', goal: '模型怎么知道自己预测得好不好' },
        { n: '6', title: '模型怎样改进预测', goal: '根据损失调参数' },
        { n: '7', title: '梯度', goal: '告诉模型往哪个方向调' },
        { n: '8', title: '梯度下降完整走一遍', goal: '更新参数、重新算损失' },
        { n: '9', title: '学习率', goal: '步子太大为什么反而变差' },
        { n: '10', title: '导数是什么', goal: '变化的快慢' },
        { n: '11', title: '两个求导规则', goal: '常数、x 的 n 次方' },
        { n: '12', title: '平方函数求导', goal: '为什么 x² 的导数是 2x' },
        { n: '13', title: '链式法则', goal: '变化一层层传递' },
        { n: '14', title: '用 Python 训练一个模型', goal: '手写一次参数更新' },
        { n: '15', title: '连续训练 10 次', goal: '训练循环' },
        { n: '16', title: 'Token 与词 ID', goal: '计算机怎么理解文字' },
        { n: '17', title: '词向量', goal: '用一串数字表示一个词' },
        { n: '18', title: '两个词的相似度', goal: '余弦相似度' },
        { n: '19', title: '文本向量表示', goal: '词袋：一句话变成一个向量' },
        { n: '20', title: 'TF-IDF 入门', goal: '常见词不重要，少见词重要' },
        { n: '21', title: '用 Python 计算 TF-IDF', goal: '手算一遍' },
        { n: '22', title: 'TF-IDF 综合练习', goal: '从看懂代码到自己写出来' },
        { n: '23', title: '用 scikit-learn 生成 TF-IDF', goal: 'TfidfVectorizer，和手算的差别' },
      ],
      extras: {
        title: '学习记录',
        note: '当时的学习记录整理，按主题合并，一篇对应几课。第 1-33 课一课一页写好以后，这里只作底稿。',
        items: [
          record('第 1-2 天练习 · NumPy 与向量基础', '01_numpy与向量基础'),
          record('第 1-6 课 · 从公式到损失', '02_从公式到损失'),
          record('第 7 课 · 导数与梯度', '03_导数与梯度'),
          record('第 8-15 课 · 梯度下降', '04_梯度下降'),
          record('第 16-23 课 · 文本向量化', '05_文本向量化'),
        ],
      },
    },
    {
      id: '2',
      title: '传统机器学习与文本分类',
      range: '第 24-40 课',
      folder: '2_传统机器学习',
      lessons: [
        { n: '24', title: 'TF-IDF 关键词提取实战', goal: '读懂一段完整代码' },
        { n: '25', title: '用 TF-IDF 提取关键词', goal: '逐篇找出最重要的词' },
        { n: '26', title: '机器学习是什么', goal: '监督学习与无监督学习' },
        { n: '27', title: '监督学习与文本分类', goal: '特征与标签、训练测试划分' },
        { n: '28', title: '第一个文本分类模型', goal: '分词 → TF-IDF → 逻辑回归 → 准确率' },
        { n: '29', title: '不要只看准确率', goal: '混淆矩阵、P / R / F1、阈值' },
        { n: '30', title: '模型优化与过拟合', goal: '训练和测试的差距' },
        { n: '31', title: '正则化', goal: 'L1、L2、C' },
        { n: '32', title: '模型复杂度', goal: '过拟合、欠拟合、偏差与方差' },
        { n: '33', title: '交叉验证', goal: 'K 折、Pipeline、标准差' },
        { n: '34', title: '换成真实数据集', goal: '11987 条外卖评论：类别比例、基线、抽查标签',
          file: 'nlp/2_传统机器学习/lesson34_换成真实数据集.md' },
        { n: '35', title: '朴素贝叶斯', goal: '贝叶斯定理、先验与后验、平滑、MultinomialNB',
          file: 'nlp/2_传统机器学习/lesson35_朴素贝叶斯.md' },
        { n: '36', title: '逻辑回归与朴素贝叶斯对比', goal: '重复交叉验证：差多少才算真的更好' },
        { n: '37', title: '网格搜索', goal: 'GridSearchCV + Pipeline，调参不泄漏' },
        { n: '38', title: '类别不平衡', goal: 'class_weight，看 F1 而不只看准确率' },
        { n: '39', title: '错误分析', goal: '模型错在哪类评论上，标签错还是模型错' },
        { n: '40', title: '项目一：中文文本分类器', goal: '可运行、有评估报告', project: '中文文本分类器' },
      ],
      extras: {
        title: '学习记录',
        note: '第 24-33 课当时的学习记录整理。',
        items: [
          record('第 24-27 课 · 机器学习流程', '06_机器学习流程'),
          record('第 28-29 课 · 模型评估', '07_模型评估'),
          record('第 30-32 课 · 过拟合与正则化', '08_过拟合与正则化'),
          record('第 33 课 · 交叉验证', '09_交叉验证'),
        ],
      },
    },
    {
      id: '3',
      title: '语义表示与搜索',
      range: '第 41-53 课',
      folder: '3_语义表示与搜索',
      lessons: [
        { n: '41', title: '词袋的局限', goal: '为什么「好」和「棒」在 TF-IDF 里毫无关系' },
        { n: '42', title: '分布式假设', goal: '看一个词的邻居，就知道它的意思' },
        { n: '43', title: 'Word2Vec 的直觉', goal: '用「预测邻居」来学向量' },
        { n: '44', title: 'CBOW 与 Skip-gram', goal: '两种预测方向' },
        { n: '45', title: '训练自己的词向量', goal: '在评论数据上训练，看近义词' },
        { n: '46', title: '词向量能做什么', goal: '近义词、类比，以及做不到的事' },
        { n: '47', title: '从词向量到句向量', goal: '平均与加权平均' },
        { n: '48', title: '预训练 embedding 模型', goal: '一句话一个向量（AI 应用开发 Day 51 会用到）' },
        { n: '49', title: '余弦相似度深入', goal: '归一化、点积与距离的关系' },
        { n: '50', title: '语义搜索', goal: '输入一句话，找到意思最像的评论' },
        { n: '51', title: '检索评估', goal: 'Recall@K、MRR' },
        { n: '52', title: '用 embedding 做分类', goal: '和 TF-IDF 方案正面比一次' },
        { n: '53', title: '项目二：中文语义搜索', goal: '可运行、可评估', project: '中文语义搜索' },
      ],
    },
    {
      id: '4',
      title: '深度学习与 PyTorch',
      range: '第 54-66 课',
      folder: '4_深度学习与PyTorch',
      lessons: [
        { n: '54', title: '用到的概率', goal: '条件概率、期望，只讲后面要用的' },
        { n: '55', title: 'PyTorch 张量', goal: '和 NumPy 一一对应' },
        { n: '56', title: '自动求导', goal: '第 8-15 课手推的梯度，交给框架算' },
        { n: '57', title: '用 PyTorch 重写梯度下降', goal: '第 15 课的训练循环，换成框架的写法' },
        { n: '58', title: '神经元与激活函数', goal: '加权求和再过一个函数，和逻辑回归是什么关系' },
        { n: '59', title: '多层网络与反向传播', goal: '链式法则在网络里怎么走' },
        { n: '60', title: '交叉熵', goal: '为什么分类用它而不用平方误差' },
        { n: '61', title: '训练循环', goal: 'batch、epoch、优化器' },
        { n: '62', title: 'Embedding 层', goal: '把词 id 变成可以训练的向量' },
        { n: '63', title: '用神经网络做文本分类', goal: '和项目一的模型比' },
        { n: '64', title: 'RNN', goal: '按顺序读一句话' },
        { n: '65', title: 'CNN 用于文本', goal: '了解即可' },
        { n: '66', title: '防止过拟合的新办法', goal: 'dropout、早停' },
      ],
    },
    {
      id: '5',
      title: 'Transformer 与预训练模型',
      range: '第 67-78 课',
      folder: '5_Transformer与预训练模型',
      lessons: [
        { n: '67', title: '注意力的直觉', goal: '读一句话时，每个词该看哪里' },
        { n: '68', title: 'Self-Attention', goal: 'Q、K、V 拆开讲，用小数字手算一次' },
        { n: '69', title: '多头注意力与位置编码', goal: '同时从几个角度看；词的顺序怎么告诉模型' },
        { n: '70', title: 'Transformer 架构', goal: 'Encoder 与 Decoder' },
        { n: '71', title: 'Tokenizer', goal: '子词切分，中文怎么切' },
        { n: '72', title: 'BERT', goal: '预训练在学什么' },
        { n: '73', title: 'GPT 系列', goal: '和 BERT 的区别，接上 AI 应用开发' },
        { n: '74', title: 'Hugging Face 入门', goal: '加载模型和分词器' },
        { n: '75', title: '微调（一）', goal: '准备数据集' },
        { n: '76', title: '微调（二）', goal: '训练与评估', note: '这台电脑没有 NVIDIA 显卡：用小模型在 CPU 上跑，或借云端 GPU，到时实测' },
        { n: '77', title: '微调（三）', goal: '和 TF-IDF、embedding 两种方案对比' },
        { n: '78', title: '项目三：Transformer 文本分类', goal: '实验报告与部署', project: 'Transformer 文本分类' },
      ],
    },
    {
      id: '6',
      title: 'RAG 专项与求职',
      range: '第 79-90 课',
      folder: '6_RAG专项与求职',
      lessons: [
        { n: '79', title: 'RAG 回顾', goal: '在 AI 应用开发搭好的系统上继续，不从零再搭', note: 'AI 应用开发 Day 46-65' },
        { n: '80', title: '混合检索实验', goal: '关键词和向量各占多少' },
        { n: '81', title: '重排序模型', goal: 'cross-encoder 为什么更准、更慢' },
        { n: '82', title: '切块与 Top-K 实验', goal: '每个参数对检索指标的影响' },
        { n: '83', title: '幻觉分析', goal: '答案和资料对不上，错在检索还是生成' },
        { n: '84', title: '项目四：企业知识库 RAG', goal: '评估与优化报告', project: '企业知识库 RAG' },
        { n: '85', title: '消融实验', goal: '每个改动各贡献多少' },
        { n: '86', title: '推理效率', goal: '模型变小、批量推理' },
        { n: '87', title: '用 FastAPI 部署模型', goal: '把训练好的模型做成接口' },
        { n: '88', title: '整理作品', goal: 'README、实验记录、GitHub 主页' },
        { n: '89', title: '面试准备（一）', goal: '机器学习基础题' },
        { n: '90', title: '面试准备（二）', goal: 'NLP 原理与讲项目' },
      ],
    },
  ],
}

export const courses: Course[] = [ai, nlp]

// ---------------------------------------------------------------------------
// 查询
// ---------------------------------------------------------------------------

/** 「Day 23」「第 34 课」；讲义章号、预备课、「练」「记录」这类原样返回 */
export function numberLabel(course: Course, n: string): string {
  if (!/^\d+$/.test(n)) return n
  return course.id === 'ai' ? `Day ${n}` : `第 ${n} 课`
}

export function normalizePath(path: string): string {
  return decodeURI(path).replace(/\.html$/, '').replace(/\/index$/, '/')
}

export function courseOf(path: string): Course | undefined {
  const p = normalizePath(path)
  return courses.find((c) => c.prefixes.some((pre) => p.startsWith(pre)))
}

export interface Found {
  course: Course
  stage: Stage
  lesson: Lesson
  parent?: Lesson      // 加练：挂在哪一天下面
  extra?: string       // 阶段附加材料的名字：「讲义（旧版）」「学习记录」
}

export function findLesson(path: string): Found | undefined {
  const p = normalizePath(path)
  const hit = (l: Lesson) => !!l.file && linkOf(l.file) === p
  for (const course of courses) {
    for (const stage of course.stages) {
      for (const lesson of stage.lessons) {
        if (hit(lesson)) return { course, stage, lesson }
        const ex = lesson.extras?.find(hit)
        if (ex) return { course, stage, lesson: ex, parent: lesson }
      }
      const se = stage.extras?.items.find(hit)
      if (se) return { course, stage, lesson: se, extra: stage.extras!.title }
    }
  }
  return undefined
}

/** 一天能不能学：有课文，或者有加练 */
export function entryLink(l: Lesson): string | undefined {
  if (l.file) return linkOf(l.file)
  const first = l.extras?.find((e) => e.file)
  return first ? linkOf(first.file!) : undefined
}

/** 这一天要标记完成的所有页面（课文 + 加练） */
export function pagesOf(l: Lesson): string[] {
  return [l.file, ...(l.extras ?? []).map((e) => e.file)]
    .filter((f): f is string => !!f).map(linkOf)
}

export function stagePages(s: Stage): string[] {
  return [...s.lessons.flatMap(pagesOf), ...(s.extras?.items ?? []).flatMap(pagesOf)]
}

// ---------------------------------------------------------------------------
// 侧边栏：每门课一套。只列已经有内容的天；还没写的在课表里看
// ---------------------------------------------------------------------------

function label(n: string, title: string): string {
  return `<span class="pe-n">${n}</span><span class="pe-t">${title}</span>`
}

interface Item { text: string; link?: string; collapsed?: boolean; items?: Item[] }

function courseSidebar(course: Course): Item[] {
  const stages: Item[] = []
  for (const s of course.stages) {
    const items: Item[] = []
    for (const l of s.lessons) {
      const extras = (l.extras ?? []).filter((e) => e.file)
      if (!l.file && !extras.length) continue
      items.push({
        text: label(l.n, l.file ? l.title : `${l.title}<span class="pe-wip">待写</span>`),
        link: l.file ? linkOf(l.file) : undefined,
        items: extras.length
          ? extras.map((e) => ({ text: label('练', e.title), link: linkOf(e.file!) }))
          : undefined,
      })
    }
    if (s.extras) {
      items.push({
        text: s.extras.title,
        collapsed: true,
        items: s.extras.items.filter((e) => e.file)
          .map((e) => ({ text: label(e.n, e.title), link: linkOf(e.file!) })),
      })
    }
    if (!items.length) continue
    stages.push({
      text: `阶段 ${s.id} · ${s.title}<span class="pe-range">${s.range}</span>`,
      collapsed: true,          // 只展开当前这一页所在的阶段（VitePress 会自动展开）
      items,
    })
  }
  return [{ text: '课表与进度', link: course.home }, ...stages]
}

export function sidebar(): Record<string, Item[]> {
  const result: Record<string, Item[]> = {}
  for (const course of courses) {
    for (const prefix of course.prefixes) result[prefix] = courseSidebar(course)
  }
  return result
}
