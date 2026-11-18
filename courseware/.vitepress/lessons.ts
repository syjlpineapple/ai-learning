// 课程目录的唯一来源：侧边栏、上一课/下一课、首页进度条都从这里生成。
// link 为空表示还没写，只在首页进度条里占一个位置。

export interface Lesson {
  title: string
  link?: string
}

export interface Group {
  id: string        // 进度条每一行左边的短名
  title: string     // 侧边栏分组名
  kind: 'problem' | 'lecture'
  lessons: Lesson[]
}

const L = '/course/python-engineering/'
const P = L + 'practice/'

export const groups: Group[] = [
  {
    id: 'M4',
    title: '每日一题 · 数据持久化',
    kind: 'problem',
    lessons: [
      { title: '第 1 题 · 排行榜存盘', link: P + 'p01_排行榜存盘' },
      { title: '第 2 题 · JSON 存档' },
      { title: '第 3 题 · 不信任读进来的数据' },
      { title: '第 4 题 · 用日志代替 print' },
      { title: '第 5 题 · 该返回空值还是抛异常' },
    ],
  },
  {
    id: 'M0',
    title: '讲义 · 开始之前',
    kind: 'lecture',
    lessons: [
      { title: '0.1 这门课怎么学', link: L + '00_01_怎么学' },
      { title: '0.2 环境准备', link: L + '00_02_环境准备' },
    ],
  },
  {
    id: 'M1',
    title: '讲义 · 语言基础',
    kind: 'lecture',
    lessons: [
      { title: '1.1 程序的三种结构', link: L + '01_01_程序的三种结构' },
      { title: '1.2 条件分支与真值测试', link: L + '01_02_条件分支与真值测试' },
      { title: '1.3 循环与四个结束', link: L + '01_03_循环与四个结束' },
      { title: '1.4 模块与字符串格式化', link: L + '01_04_模块与字符串格式化' },
      { title: '1.5 异常处理入门', link: L + '01_05_异常处理入门' },
      { title: '1.6 函数', link: L + '01_06_函数' },
      { title: '1.7 列表', link: L + '01_07_列表' },
      { title: '1.8 字典、元组、集合', link: L + '01_08_字典元组集合' },
      { title: '1.9 内置函数与边界条件', link: L + '01_09_内置函数与边界条件' },
    ],
  },
  {
    id: 'M2',
    title: '讲义 · 测试入门',
    kind: 'lecture',
    lessons: [
      { title: '2.1 assert 与自动化测试', link: L + '02_01_assert与自动化测试' },
      { title: '2.2 异常体系与 raise', link: L + '02_02_异常体系与raise' },
      { title: '2.3 从 assert 到 pytest', link: L + '02_03_从assert到pytest' },
    ],
  },
  {
    id: 'M3',
    title: '讲义 · 工程结构',
    kind: 'lecture',
    lessons: [
      { title: '3.1 模块、包与 import 机制', link: L + '03_01_模块包与import机制' },
      { title: '3.2 类与面向对象', link: L + '03_02_类与面向对象' },
      { title: '3.3 项目分层与职责划分', link: L + '03_03_项目分层与职责划分' },
    ],
  },
]

function items(kind: Group['kind']) {
  return groups
    .filter((g) => g.kind === kind)
    .map((g) => ({
      text: g.title,
      collapsed: kind === 'lecture' ? false : undefined,
      items: g.lessons.map((l) =>
        l.link ? { text: l.title, link: l.link } : { text: `${l.title}（编写中）` },
      ),
    }))
}

// 两套侧边栏：题目页只在题目之间翻页，讲义页只在讲义之间翻页。
// 「上一课 / 下一课」按侧边栏顺序生成，放在一起的话，最后一道题的下一课会跳进讲义。
export function sidebar() {
  return {
    [P]: items('problem'),
    [L]: items('lecture'),
  }
}
