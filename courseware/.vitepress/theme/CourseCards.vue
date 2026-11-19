<script setup lang="ts">
// 首页的两门课：各自的进度，和「接着学」哪一天。
import { computed, onMounted } from 'vue'
import { withBase } from 'vitepress'
import { courses, entryLink, numberLabel, pagesOf } from '../lessons'
import { done, isDone, loadProgress } from './progress'

onMounted(loadProgress)

const cards = computed(() => {
  void done.value
  return courses.map((c) => {
    const all = c.stages.flatMap((s) => s.lessons.map((l) => ({ l, stage: s })))
    const ready = all.filter(({ l }) => entryLink(l))
    const finished = ready.filter(({ l }) => pagesOf(l).every(isDone))
    const next = ready.find(({ l }) => !pagesOf(l).every(isDone))
    return {
      course: c,
      total: all.length,
      ready: ready.length,
      finished: finished.length,
      next: next ? { label: `${numberLabel(c, next.l.n)} ${next.l.title}`, link: entryLink(next.l)! } : undefined,
      stage: next?.stage ?? c.stages[c.stages.length - 1],
      unit: c.id === 'ai' ? '天' : '课',
    }
  })
})
</script>

<template>
  <div class="cards">
    <article v-for="card in cards" :key="card.course.id" class="card">
      <p class="route">{{ card.course.route }}</p>
      <h2>{{ card.course.title }}</h2>
      <p class="desc">{{ card.course.desc }}</p>

      <div class="bar" role="img" :aria-label="`共 ${card.total} ${card.unit}，有内容 ${card.ready} ${card.unit}，完成 ${card.finished} ${card.unit}`">
        <span class="fill ready" :style="{ width: (card.ready / card.total) * 100 + '%' }" />
        <span class="fill pass" :style="{ width: (card.finished / card.total) * 100 + '%' }" />
      </div>
      <p class="nums">
        <span class="n-pass">完成 {{ card.finished }}</span>
        <span class="n-ready">有内容 {{ card.ready }}</span>
        <span>共 {{ card.total }} {{ card.unit }}</span>
      </p>

      <p class="where">当前在 <b>阶段 {{ card.stage.id }} · {{ card.stage.title }}</b>（{{ card.stage.range }}）</p>

      <div class="card-actions">
        <a v-if="card.next" class="primary" :href="withBase(card.next.link)">接着学：{{ card.next.label }}</a>
        <a class="secondary" :href="withBase(card.course.home)">课表</a>
      </div>
    </article>
  </div>
</template>

<style scoped>
.cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(340px, 1fr));
  gap: 24px;
}
.card {
  display: flex;
  flex-direction: column;
  padding: 26px 28px 24px;
  border: 1px solid var(--vp-c-divider);
  border-radius: 12px;
  background: var(--vp-c-bg);
}
.route { margin: 0; font-size: 13px; color: var(--vp-c-text-3); }
h2 { margin: 4px 0 8px; font-size: 24px; font-weight: 800; color: var(--vp-c-text-1); }
.desc { margin: 0 0 22px; color: var(--vp-c-text-2); line-height: 1.7; font-size: 15px; flex: 1; }
.bar {
  position: relative;
  height: 8px;
  border-radius: 999px;
  background: var(--vp-c-bg-soft);
  overflow: hidden;
}
.fill { position: absolute; inset: 0 auto 0 0; border-radius: 999px; }
.fill.ready { background: color-mix(in srgb, var(--pe-term-skip) 45%, transparent); }
.fill.pass { background: var(--pe-pass); }
.nums { display: flex; gap: 16px; margin: 8px 0 0; font-size: 13px; color: var(--vp-c-text-3); }
.n-pass { color: var(--pe-pass); font-weight: 600; }
.n-ready { color: var(--pe-hint); }
.where { margin: 14px 0 18px; font-size: 14px; color: var(--vp-c-text-2); }
.where b { color: var(--vp-c-text-1); font-weight: 650; }
.card-actions { display: flex; flex-wrap: wrap; gap: 10px; }
.card-actions a { padding: 9px 18px; border-radius: 8px; font-weight: 600; font-size: 14px; text-decoration: none; }
.primary { background: var(--vp-c-brand-1); color: var(--vp-c-white); }
.primary:hover { background: var(--vp-c-brand-2); }
.secondary { border: 1px solid var(--vp-c-divider); color: var(--vp-c-text-1); }
.secondary:hover { border-color: var(--vp-c-brand-1); }
@media (max-width: 420px) {
  .cards { grid-template-columns: 1fr; }
}
</style>
