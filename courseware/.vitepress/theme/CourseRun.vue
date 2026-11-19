<script setup lang="ts">
// 课表页顶上的进度条：把一门课画成一次 pytest 运行。
// 做完的课是绿色的点，写好了还没做的是黄色的 s，还没写的是灰色的 · ——
// 和配套代码里「没做的练习显示 skip」是同一个约定。
import { computed, onMounted } from 'vue'
import { withBase } from 'vitepress'
import { courses, entryLink, numberLabel, pagesOf } from '../lessons'
import { done, isDone, loadProgress } from './progress'

const props = defineProps<{ course: string }>()
onMounted(loadProgress)

const course = computed(() => courses.find((c) => c.id === props.course)!)

const rows = computed(() => {
  void done.value // 依赖进度，标记完成后重新计算
  return course.value.stages.map((s) => ({
    id: s.id,
    title: s.title,
    cells: s.lessons.map((l) => {
      const link = entryLink(l)
      const pages = pagesOf(l)
      return {
        key: l.n,
        title: `${numberLabel(course.value, l.n)} ${l.title}`,
        link: link ? withBase(link) : undefined,
        // 一天的课文和加练都标了完成，这一天才算完成
        state: !link ? 'todo' : pages.every(isDone) ? 'pass' : 'skip',
      }
    }),
  }))
})

const count = (state: string) =>
  rows.value.reduce((n, r) => n + r.cells.filter((c) => c.state === state).length, 0)
const total = computed(() => rows.value.reduce((n, r) => n + r.cells.length, 0))
const percent = (i: number) => {
  const before = rows.value.slice(0, i + 1).reduce((n, r) => n + r.cells.length, 0)
  return Math.round((before / total.value) * 100)
}
</script>

<template>
  <figure class="run" aria-label="学习进度">
    <div class="cmd"><span class="prompt">$</span> pytest {{ course.id }}/</div>
    <div class="dim">collected {{ total }} items</div>
    <ol class="rows">
      <li v-for="(row, i) in rows" :key="row.id" class="row">
        <span class="id">{{ row.id }}</span>
        <span class="group">{{ row.title }}</span>
        <span class="cells">
          <template v-for="cell in row.cells" :key="cell.key">
            <a
              v-if="cell.link"
              :href="cell.link"
              :class="['cell', cell.state]"
              :title="cell.title + (cell.state === 'pass' ? '（已完成）' : '')"
            >{{ cell.state === 'pass' ? '•' : 's' }}</a>
            <span v-else class="cell todo" :title="cell.title + '（编写中）'">·</span>
          </template>
        </span>
        <span class="pct">[{{ String(percent(i)).padStart(3, ' ') }}%]</span>
      </li>
    </ol>
    <div class="summary">
      <span class="ok">{{ count('pass') }} passed</span>,
      <span class="sk">{{ count('skip') }} skipped</span>,
      <span class="td">{{ count('todo') }} 编写中</span>
    </div>
    <figcaption>
      每个符号是{{ course.id === 'ai' ? '一天' : '一课' }}，点它直接打开：<b class="k-pass">•</b> 做完了，<b class="k-skip">s</b> 写好了还没做，<b class="k-todo">·</b> 还没写。
      做完一课，在页面底部点「标记为已完成」。进度只存在这台电脑的浏览器里。
    </figcaption>
  </figure>
</template>

<style scoped>
.run {
  margin: 0;
  padding: 22px 26px 20px;
  border-radius: 10px;
  background: var(--pe-term-bg);
  color: var(--pe-term-fg);
  font-family: var(--vp-font-family-mono);
  font-size: 14px;
  line-height: 1.75;
  overflow-x: auto;
}
.prompt { color: var(--pe-term-dim); margin-right: 6px; }
.dim { color: var(--pe-term-dim); }
.rows { list-style: none; margin: 10px 0 8px; padding: 0; }
.row {
  display: grid;
  grid-template-columns: 1.4em 9.5em minmax(0, 1fr) auto;
  align-items: baseline;
  column-gap: 14px;
  white-space: nowrap;
}
.id { color: var(--pe-term-dim); }
.cells { letter-spacing: 0.14em; white-space: normal; word-break: break-all; }
.cell { text-decoration: none; font-weight: 700; }
.cell.pass { color: var(--pe-pass-bright); }
.cell.skip { color: var(--pe-term-skip); }
.cell.todo { color: var(--pe-term-dim); opacity: 0.55; font-weight: 400; }
a.cell:hover { color: var(--pe-term-fg); text-decoration: underline; }
a.cell:focus-visible { outline: 2px solid var(--pe-term-fg); outline-offset: 2px; border-radius: 2px; }
.group {
  color: var(--pe-term-dim);
  font-family: var(--vp-font-family-base);
  font-size: 13px;
  overflow: hidden;
  text-overflow: ellipsis;
}
.pct { color: var(--pe-term-dim); white-space: pre; }
.summary { border-top: 1px solid var(--pe-term-rule); padding-top: 8px; color: var(--pe-term-dim); }
.summary .ok { color: var(--pe-pass-bright); }
.summary .sk { color: var(--pe-term-skip); }
figcaption {
  margin-top: 14px;
  color: var(--pe-term-dim);
  font-family: var(--vp-font-family-base);
  font-size: 13px;
  line-height: 1.7;
  white-space: normal;
}
.k-pass { color: var(--pe-pass-bright); }
.k-skip { color: var(--pe-term-skip); }
.k-todo { color: var(--pe-term-fg); }
@media (max-width: 640px) {
  .run { padding: 16px; font-size: 13px; }
  .row { grid-template-columns: 1.4em minmax(0, 1fr) auto; }
  .cells { grid-column: 2; }
  .group { display: none; }
}
</style>
