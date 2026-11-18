import { defineConfig } from 'vitepress'
import { sidebar } from './lessons'

const REPO = 'https://github.com/syjlpineapple/ai-learning'
const CODE_ROOT = 'course/python-engineering/code/'

export default defineConfig({
  lang: 'zh-CN',
  title: 'Python 工程化 · 每日一题',
  description: '从一个猜数字程序开始，一题一题改成能交付的代码。',
  cleanUrls: true,
  lastUpdated: true,

  // 只发布整理好的成品。原始素材、代码仓、学习记录（暂未迁移）不进网站
  srcExclude: [
    '_raw/**', 'tools/**', 'python/**', 'nlp/**', 'README.md',
    '**/code/**', 'course/python-engineering/README.md',
  ],

  // 指向代码文件和学习记录的链接改成 GitHub 地址（下面的 markdown 配置里处理），
  // 剩下的死链要让构建失败，这样不会悄悄发布一个点了 404 的页面
  ignoreDeadLinks: false,

  markdown: {
    lineNumbers: false,
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

      // 课件里大量链接指向 code/ 下的源码目录和 python/ 下的学习记录。
      // 它们不是网站页面，统一改写成 GitHub 上的地址。
      const defaultRender = md.renderer.rules.link_open
        ?? ((tokens, idx, options, _env, self) => self.renderToken(tokens, idx, options))
      md.renderer.rules.link_open = (tokens, idx, options, env, self) => {
        const href = tokens[idx].attrGet('href') ?? ''
        const page: string = env.relativePath ?? ''
        if (href && !/^(https?:|#|mailto:)/.test(href)) {
          const target = new URL(href, 'file:///' + page).pathname.slice(1)
          const decoded = decodeURIComponent(target)
          if (decoded.includes(CODE_ROOT) || /^(python|nlp)\//.test(decoded)) {
            const isFile = /\.[a-z]+$/i.test(decoded) && !decoded.endsWith('/')
            tokens[idx].attrSet('href', `${REPO}/${isFile ? 'blob' : 'tree'}/main/courseware/${target}`)
            tokens[idx].attrSet('target', '_blank')
          }
        }
        return defaultRender(tokens, idx, options, env, self)
      }
    },
  },

  themeConfig: {
    nav: [
      { text: '每日一题', link: '/course/python-engineering/practice/p01_排行榜存盘' },
      { text: '讲义', link: '/course/python-engineering/00_01_怎么学' },
      { text: '代码仓', link: `${REPO}/tree/main/courseware/${CODE_ROOT}` },
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
