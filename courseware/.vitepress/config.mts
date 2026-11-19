import { fileURLToPath } from 'node:url'
import { defineConfig } from 'vitepress'
import { courses, REPO, sidebar } from './lessons'
import { writeReadmes } from './readme'

const CODE_ROOT = 'courseware/ai/code/'

// 启动网站时顺便更新 ai/README.md、nlp/README.md 两份课表（不开网站时在编辑器里看的就是它们）
writeReadmes(fileURLToPath(new URL('..', import.meta.url)))

// 一个链接指向的东西不是网站页面时（源码、学习记录、原始素材、README），改成 GitHub 地址。
// repoPath 是相对仓库根目录的路径，比如 nlp/day_5.py、courseware/records/python/Day11.md
function notAPage(repoPath: string): boolean {
  if (!repoPath.startsWith('courseware/')) return true                  // 课件目录以外：练习代码
  if (repoPath.startsWith(CODE_ROOT)) return true                       // 配套代码仓
  if (/^courseware\/(_raw|tools|records\/python)\//.test(repoPath)) return true  // 素材、脚本、A 线学习记录
  if (/^courseware\/records\/[^/]+\.md$/.test(repoPath)) return true   // records/ 下的零散文件（旧大纲）
  if (/(^|\/)README\.md$/.test(repoPath)) return true
  const ext = /\.([a-z0-9]+)$/i.exec(repoPath)?.[1]?.toLowerCase()
  return ext !== undefined && ext !== 'md' && ext !== 'html'
}

export default defineConfig({
  lang: 'zh-CN',
  title: '每日一课',
  description: 'AI 应用开发与 NLP 两门课，每天各 45 分钟，先动手再讲评。',
  cleanUrls: true,
  lastUpdated: true,

  // 只发布课文。原始素材、代码仓、A 线学习记录、README 不进网站。
  // records/nlp/ 下的 9 篇是 NLP 第 1-33 课的学习记录，暂时作为那门课的附加材料发布
  srcExclude: [
    '_raw/**', 'tools/**', 'records/python/**', 'records/*.md', '**/README.md', '**/code/**',
    'node_modules/**',
    '**/_*.md',             // 下划线开头的是模板之类的内部文件
  ],

  // 只给网站用的页面（课表页、知识点索引）放在 site/，不和课文混在一起
  rewrites: {
    'site/ai.md': 'ai/index.md',
    'site/nlp.md': 'nlp/index.md',
    'site/knowledge.md': 'knowledge.md',
  },

  // 指向代码文件和学习记录的链接改成 GitHub 地址（下面的 markdown 配置里处理），
  // 剩下的死链要让构建失败，这样不会悄悄发布一个点了 404 的页面
  ignoreDeadLinks: false,

  markdown: {
    lineNumbers: false,
    math: true,               // NLP 课里的公式（$...$、$$...$$），用 markdown-it-mathjax3 渲染
    languageAlias: { gitignore: 'ini' },
    container: {
      tipLabel: '复盘',
      warningLabel: '提示',
      dangerLabel: '踩坑',
      infoLabel: '说明',
      detailsLabel: '展开',
    },
    config(md) {
      // 行内代码加 v-pre：讲义里有 `{{` `}}` 这类 f-string 写法，
      // 不加的话 Vue 会把它当成模板插值，整页编译失败。（代码块默认就是 v-pre）
      const inlineCode = md.renderer.rules.code_inline!
      md.renderer.rules.code_inline = (tokens, idx, options, env, self) =>
        inlineCode(tokens, idx, options, env, self).replace(/^<code/, '<code v-pre')

      const defaultRender = md.renderer.rules.link_open
        ?? ((tokens, idx, options, _env, self) => self.renderToken(tokens, idx, options))
      md.renderer.rules.link_open = (tokens, idx, options, env, self) => {
        const href = tokens[idx].attrGet('href') ?? ''
        const page: string = env.relativePath ?? ''
        if (href && !/^(https?:|#|mailto:)/.test(href)) {
          // 网站根目录是仓库里的 courseware/，从这里算出链接在仓库里的真实位置
          const url = new URL(href, 'file:///courseware/' + page)
          const encoded = url.pathname.slice(1)
          if (notAPage(decodeURIComponent(encoded))) {
            const isDir = encoded.endsWith('/')
            tokens[idx].attrSet('href', `${REPO}/${isDir ? 'tree' : 'blob'}/main/${encoded}${url.hash}`)
            tokens[idx].attrSet('target', '_blank')
          }
        }
        return defaultRender(tokens, idx, options, env, self)
      }
    },
  },

  themeConfig: {
    nav: [
      ...courses.map((c) => ({
        text: c.title,
        link: c.home,
        activeMatch: c.prefixes.map((p) => '^' + p).join('|'),
      })),
      { text: '知识点索引', link: '/knowledge' },
      { text: '代码仓', link: `${REPO}/tree/main/${CODE_ROOT}` },
    ],
    sidebar: sidebar(),
    outline: { level: [2, 3], label: '本页' },
    docFooter: { prev: '上一课', next: '下一课' },
    lastUpdated: { text: '最后更新' },
    returnToTopLabel: '回到顶部',
    sidebarMenuLabel: '目录',
    darkModeSwitchLabel: '深色模式',
    search: {
      provider: 'local',
      options: {
        translations: {
          button: { buttonText: '搜索', buttonAriaLabel: '搜索' },
          modal: {
            noResultsText: '没有找到',
            resetButtonTitle: '清空',
            footer: { selectText: '打开', navigateText: '切换', closeText: '关闭' },
          },
        },
      },
    },
    socialLinks: [{ icon: 'github', link: REPO }],
  },
})
