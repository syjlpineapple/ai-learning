<script setup lang="ts">
// 每一课标题上面的一行位置（哪门课、哪个阶段、第几题），
// 题目页标题下面再加一条：多长时间、用到哪些知识、当时是哪几天学的。
import { computed } from 'vue'
import { useData, useRoute, withBase } from 'vitepress'
import { findLesson, numberLabel } from '../lessons'

const route = useRoute()
const { frontmatter } = useData()
const meta = computed(() => frontmatter.value as {
  kind?: string; time?: string; uses?: string[]; record?: { text: string; link: string }[]
})
const where = computed(() => findLesson(route.path))
// 这一页在课里的位置：「Day 15」「Day 15 · 加练」「讲义（旧版）」「第 34 课」
const number = computed(() => {
  const w = where.value
  if (!w) return ''
  if (w.parent) return `${numberLabel(w.course, w.parent.n)} · 加练`
  if (w.extra) return w.extra
  return numberLabel(w.course, w.lesson.n)
})
const showMeta = computed(() => meta.value.kind === 'problem' || meta.value.kind === 'lesson')
</script>

<template>
  <nav v-if="where" class="crumb" aria-label="位置">
    <a :href="withBase(where.course.home)">{{ where.course.title }}</a>
    <span class="sep">/</span>
    <a :href="withBase(where.course.home) + `#stage-${where.stage.id}`">阶段 {{ where.stage.id }} · {{ where.stage.title }}</a>
    <template v-if="number">
      <span class="sep">/</span>
      <span>{{ number }}</span>
    </template>
  </nav>
  <dl v-if="showMeta" class="meta">
    <div v-if="meta.time"><dt>用时</dt><dd>{{ meta.time }}</dd></div>
    <div v-if="meta.uses?.length">
      <dt>用到</dt>
      <dd><span v-for="u in meta.uses" :key="u" class="tag">{{ u }}</span></dd>
    </div>
    <div v-if="meta.record?.length">
      <dt>当时怎么学的</dt>
      <dd>
        <a v-for="r in meta.record" :key="r.link" :href="r.link" target="_blank" class="rec">{{ r.text }}</a>
      </dd>
    </div>
  </dl>
</template>

<style scoped>
.crumb {
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  gap: 4px 8px;
  margin: 0 0 10px;
  font-size: 13px;
  color: var(--vp-c-text-3);
}
.crumb a { color: var(--vp-c-text-2); text-decoration: none; }
.crumb a:hover { color: var(--vp-c-brand-1); }
.sep { color: var(--vp-c-divider); }
.meta {
  display: grid;
  gap: 6px;
  margin: 0 0 28px;
  padding: 0 0 18px;
  border-bottom: 1px solid var(--vp-c-divider);
  font-size: 14px;
}
.meta > div { display: flex; gap: 14px; align-items: baseline; }
dt { flex: 0 0 6em; color: var(--vp-c-text-3); }
dd { margin: 0; display: flex; flex-wrap: wrap; gap: 6px 8px; color: var(--vp-c-text-1); }
.tag {
  padding: 1px 9px;
  border-radius: 999px;
  background: var(--vp-c-brand-soft);
  color: var(--vp-c-brand-1);
  font-size: 13px;
}
.rec { color: var(--vp-c-brand-1); }
</style>
