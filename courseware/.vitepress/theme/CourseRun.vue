<script setup lang="ts">
// 首页的进度条：把整门课画成一次 pytest 运行。
// 做完的课是绿色的点，没做的是灰色的 s —— 和配套代码里「没做的练习显示 skip」是同一个约定。
import { computed, onMounted } from 'vue'
import { withBase } from 'vitepress'
import { groups } from '../lessons'
import { done, isDone, loadProgress } from './progress'

onMounted(loadProgress)

const rows = computed(() => {
  void done.value // 依赖进度，标记完成后重新计算
  return groups.map((g) => ({
    id: g.id,
    title: g.title,
    cells: g.lessons.map((l) => ({
      title: l.title,
      link: l.link ? withBase(l.link) : undefined,
      state: !l.link ? 'todo' : isDone(l.link) ? 'pass' : 'skip',
    })),
  }))
})

const total = computed(() => rows.value.reduce((n, r) => n + r.cells.length, 0))
const passed = computed(() =>
  rows.value.reduce((n, r) => n + r.cells.filter((c) => c.state === 'pass').length, 0),
)
const percent = (row: { cells: unknown[] }, i: number) => {
  const before = rows.value.slice(0, i + 1).reduce((n, r) => n + r.cells.length, 0)
  return Math.round((before / total.value) * 100)
}
</script>

<template>
  <figure class="run" aria-label="学习进度">
    <div class="cmd"><span class="prompt">$</span> pytest course/</div>
    <div class="dim">collected {{ total }} items</div>
    <ol class="rows">
      <li v-for="(row, i) in rows" :key="row.id" class="row">
        <span class="id">{{ row.id }}</span>
        <span class="cells">
          <template v-for="cell in row.cells" :key="cell.title">
            <a
              v-if="cell.link"
              :href="cell.link"
              :class="['cell', cell.state]"
              :title="cell.title + (cell.state === 'pass' ? '（已完成）' : '')"
            >{{ cell.state === 'pass' ? '•' : 's' }}</a>
            <span v-else class="cell todo" :title="cell.title + '（编写中）'">·</span>
          </template>
        </span>
        <span class="group">{{ row.title }}</span>
        <span class="pct">[{{ String(percent(row, i)).padStart(3, ' ') }}%]</span>
      </li>
    </ol>
    <div :class="['summary', passed === total ? 'all' : '']">
      <span class="ok">{{ passed }} passed</span>, {{ total - passed }} skipped
    </div>
    <figcaption>每个点是一课，点它直接打开。做完一课，在页面底部点「标记为已完成」，这里的 s 就会变成绿点。进度只存在这台电脑的浏览器里。</figcaption>
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
.cmd { color: var(--pe-term-fg); }
.prompt { color: var(--pe-term-dim); margin-right: 6px; }
.dim { color: var(--pe-term-dim); }
.rows { list-style: none; margin: 10px 0 8px; padding: 0; }
.row {
  display: grid;
  grid-template-columns: 2.6em max-content 1fr auto;
  align-items: baseline;
  column-gap: 14px;
  white-space: nowrap;
}
.id { color: var(--pe-term-dim); }
.cells { letter-spacing: 0.18em; }
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
.summary { border-top: 1px solid var(--pe-term-rule); padding-top: 8px; color: var(--pe-term-skip); }
.summary .ok { color: var(--pe-pass-bright); }
figcaption {
  margin-top: 14px;
  color: var(--pe-term-dim);
  font-family: var(--vp-font-family-base);
  font-size: 13px;
  line-height: 1.7;
  white-space: normal;
}
@media (max-width: 640px) {
  .run { padding: 16px; font-size: 13px; }
  .row { grid-template-columns: 2.4em max-content auto; }
  .group { display: none; }
}
</style>
