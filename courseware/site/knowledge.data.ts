// 知识点索引的数据：构建时读每一课 frontmatter 里的 uses，按知识点归到一起。
// 新写一课只要在 uses 里列出知识点，索引会自动更新，不用手改。
import { createContentLoader } from 'vitepress'
import { findLesson } from '../.vitepress/lessons'

export interface Entry {
  url: string
  title: string
  where: string        // 「AI 应用开发 · 第 6 题」这样的位置
}

export interface Topic {
  name: string
  entries: Entry[]
}

declare const data: Topic[]
export { data }

export default createContentLoader(['ai/**/*.md', 'nlp/**/*.md', 'records/nlp/*.md'], {
  includeSrc: true,
  transform(pages): Topic[] {
    const topics = new Map<string, Entry[]>()
    for (const page of pages) {
      const uses = page.frontmatter.uses as string[] | undefined
      if (!uses?.length || page.url.includes('/code/')) continue
      const title = /^#\s+(.+)$/m.exec(page.src ?? '')?.[1]?.trim() ?? page.url
      const found = findLesson(page.url)
      const where = found ? found.course.title : ''
      for (const name of uses) {
        const list = topics.get(name) ?? []
        list.push({ url: page.url, title, where })
        topics.set(name, list)
      }
    }
    return [...topics.entries()]
      .map(([name, entries]) => ({ name, entries }))
      .sort((a, b) => a.name.localeCompare(b.name, 'zh-CN'))
  },
})
