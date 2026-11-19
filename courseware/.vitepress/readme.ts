// 根据 lessons.ts 生成 ai/README.md 和 nlp/README.md：不打开网站，在编辑器或 GitHub 上看的课表。
// 每次启动网站（dev / build）都会重新生成；内容没变就不写文件。
import { existsSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs'
import { join } from 'node:path'
import { courses, numberLabel, type Course, type Lesson } from './lessons'

// 表格里的 | 要转义；__name__ 这类下划线不转义会被当成加粗
const cell = (s = '') => s.replace(/\|/g, '\\|').replace(/([_*])/g, '\\$1')

// 中文字符在等宽字体里占两格，画目录树时按显示宽度对齐
const width = (s: string) => [...s].reduce((n, ch) => n + (/[\u2e80-\uffff]/.test(ch) ? 2 : 1), 0)
const pad = (s: string, w: number) => s + ' '.repeat(Math.max(1, w - width(s)))

function rel(course: Course, file: string): string {
  return file.startsWith(course.dir + '/') ? file.slice(course.dir.length + 1) : '../' + file
}

function row(course: Course, l: Lesson): string {
  // 只转义显示的文字，链接地址原样保留（地址里的 _ 转义了就找不到文件）
  const title = l.file ? `[${cell(l.title)}](${rel(course, l.file)})` : cell(l.title)
  const subs = [
    ...(l.extras ?? []).filter((e) => e.file).map((e) => `[加练：${cell(e.title)}](${rel(course, e.file!)})`),
    ...(l.record ? [`[当时的记录](${rel(course, l.record)})`] : []),
  ]
  const project = l.project ? `（作品：${cell(l.project)}）` : ''
  const content = title + project + (subs.length ? '<br>' + subs.join('　') : '')
  const goal = cell(l.goal) + (l.note ? `<br>（${cell(l.note)}）` : '')
  const state = l.file ? '✅ 有课文' : l.extras?.some((e) => e.file) ? '📝 有加练' : '编写中'
  return `| ${numberLabel(course, l.n)} | ${content} | ${goal} | ${state} |`
}

function render(course: Course): string {
  const unit = course.id === 'ai' ? '天' : '课'
  const lines: string[] = [
    `# ${course.title}`,
    '',
    `> 本文件由 \`.vitepress/lessons.ts\` 自动生成，不要手改：改课表请改 lessons.ts，启动一次网站就会更新。`,
    '',
    `${course.desc}按当时定下的 ${course.route}走，每${unit}约 45 分钟。`,
    '',
    '## 怎么学',
    '',
    `- **一${unit}一个文件**，放在对应阶段的文件夹里，文件名前面是编号，按文件名排序就是学习顺序。`,
    '- **只看源文件也能学**：在 Kiro / VS Code 里打开一个 `.md`，按 `Ctrl+Shift+V` 看排版后的预览，公式、表格、折叠的小测答案都能正常显示，指向代码的链接点了直接打开文件。',
    `- **每${unit}的顺序**：讲概念 → 演示（代码和真实输出）→ 今天的作业 → 小测。`,
    `- **作业写在** ${course.homework}。写完把运行输出发给我（或者说一声「${course.id === 'ai' ? 'Day 23' : '第 34 课'} 做完了」），讲评会追加到那一${unit}的文件末尾。`,
    '- 想要进度条、打勾和全文搜索，就打开网站：在 `courseware/` 下运行 `npm run docs:dev`。',
    '',
    '## 文件夹',
    '',
    '```',
    `${course.dir}/`,
    `├── ${pad('README.md', 30)}这份课表`,
    ...course.stages.map((s, i) => {
      const last = i === course.stages.length - 1 && course.id !== 'ai'
      return `${last ? '└──' : '├──'} ${pad(s.folder + '/', 30)}阶段 ${s.id}（${s.range}）`
    }),
    ...(course.id === 'ai' ? [`└── ${pad('code/', 30)}配套代码和测试（加练题用）`] : []),
    '```',
    '',
    course.id === 'ai'
      ? '阶段文件夹里：`dayNN_标题.md` 是那一天的课文，`加练/` 是挂在某一天后面的选做题，`讲义/` 是早先按主题写的讲义（Day 1-14 每天一页写好后会并进去）。还没写到的阶段，文件夹会在写第一课时建出来。'
      : '阶段文件夹里：`lessonNN_标题.md` 是那一课的课文。第 1-33 课当时的学习记录在 `../records/nlp/`，一篇对应几课。还没写到的阶段，文件夹会在写第一课时建出来。',
    '',
    '## 课表',
  ]
  for (const s of course.stages) {
    lines.push('', `### 阶段 ${s.id} · ${s.title}（${s.range}）`, '', `文件夹：\`${course.dir}/${s.folder}/\``, '')
    if (s.note) lines.push(s.note, '')
    lines.push(`| ${unit} | 内容 | 学会什么 | 状态 |`, '|---|---|---|---|')
    for (const l of s.lessons) lines.push(row(course, l))
    if (s.extras) {
      lines.push('', `**${s.extras.title}**：${s.extras.note ?? ''}`, '')
      for (const e of s.extras.items) {
        if (e.file) lines.push(`- [${e.n} ${e.title}](${rel(course, e.file)})`)
      }
    }
  }
  lines.push('')
  return lines.join('\n')
}

export function writeReadmes(root: string): void {
  for (const course of courses) {
    mkdirSync(join(root, course.dir), { recursive: true })
    const path = join(root, course.dir, 'README.md')
    const text = render(course)
    if (existsSync(path) && readFileSync(path, 'utf-8') === text) continue
    writeFileSync(path, text, 'utf-8')
  }
}
