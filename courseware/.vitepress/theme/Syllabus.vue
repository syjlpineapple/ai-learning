<script setup lang="ts">
// 课表页的完整课表：每个阶段一张表，一行是一天（一课）。
// 写好的课文可以点，加练和当时的学习记录跟在后面；还没写的灰着。
// 「接着学」指向第一个有内容、还没全部标记完成的一天。
import { computed, onMounted } from 'vue'
import { withBase } from 'vitepress'
import {
  courses, entryLink, linkOf, numberLabel, pagesOf, stagePages, urlOf, type Lesson, type Stage,
} from '../lessons'
import { done, isDone, loadProgress, markAll } from './progress'

const props = defineProps<{ course: string }>()
onMounted(loadProgress)

const course = computed(() => courses.find((c) => c.id === props.course)!)

const url = (file: string) => {
  const u = urlOf(file)
  return u.startsWith('http') ? u : withBase(u)
}

function state(l: Lesson): 'pass' | 'open' | 'todo' {
  void done.value
  if (!entryLink(l)) return 'todo'
  return pagesOf(l).every(isDone) ? 'pass' : 'open'
}

const next = computed<Lesson | undefined>(() =>
  course.value.stages.flatMap((s) => s.lessons).find((l) => state(l) === 'open'))

function stageDone(s: Stage): boolean {
  void done.value
  const pages = stagePages(s)
  return pages.length > 0 && pages.every(isDone)
}
</script>

<template>
  <div class="syllabus">
    <section v-for="s in course.stages" :key="s.id" class="stage">
      <h2 :id="`stage-${s.id}`">
        阶段 {{ s.id }} · {{ s.title }}
        <span class="range">{{ s.range }}</span>
      </h2>
      <p class="folder">文件夹 <code>{{ course.dir }}/{{ s.folder }}/</code></p>
      <p v-if="s.note" class="note">{{ s.note }}</p>
      <button
        v-if="stagePages(s).length"
        type="button"
        class="mark"
        @click="markAll(stagePages(s), !stageDone(s))"
      >{{ stageDone(s) ? '撤销本阶段的完成标记' : '这一阶段有内容的我都学过了' }}</button>
      <table>
        <thead>
          <tr>
            <th class="c-n">{{ course.id === 'ai' ? '天' : '课' }}</th>
            <th class="c-title">内容</th>
            <th class="c-goal">学会什么</th>
            <th class="c-state">状态</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="l in s.lessons" :key="l.n" :class="state(l)">
            <td class="c-n">{{ numberLabel(course, l.n) }}</td>
            <td class="c-title">
              <a v-if="l.file" :href="withBase(linkOf(l.file))">{{ l.title }}</a>
              <span v-else>{{ l.title }}</span>
              <span v-if="l.project" class="project">作品 · {{ l.project }}</span>
              <span v-if="l.extras?.length || l.record" class="subs">
                <a v-for="e in l.extras" :key="e.file" :href="withBase(linkOf(e.file!))">加练：{{ e.title }}</a>
                <a v-if="l.record" :href="url(l.record)" target="_blank" class="rec">当时的记录</a>
              </span>
            </td>
            <td class="c-goal">
              {{ l.goal }}
              <span v-if="l.note" class="lnote">{{ l.note }}</span>
            </td>
            <td class="c-state">
              <span v-if="state(l) === 'pass'" class="st pass">✓ 已完成</span>
              <span v-else-if="next === l" class="st next">接着学</span>
              <span v-else-if="state(l) === 'open'" class="st open">{{ l.file ? '可以学' : '有加练' }}</span>
              <span v-else class="st todo">编写中</span>
            </td>
          </tr>
        </tbody>
      </table>
      <details v-if="s.extras" class="extras">
        <summary>{{ s.extras.title }}（{{ s.extras.items.length }} 篇）</summary>
        <p v-if="s.extras.note" class="note">{{ s.extras.note }}</p>
        <ul>
          <li v-for="e in s.extras.items" :key="e.file">
            <a :href="url(e.file!)">{{ e.n }} {{ e.title }}</a>
          </li>
        </ul>
      </details>
    </section>
  </div>
</template>

<style scoped>
.stage h2 {
  display: flex;
  align-items: baseline;
  gap: 12px;
  margin: 48px 0 4px;
  padding-top: 0;
  border-top: 0;
  font-size: 20px;
}
.range { font-size: 14px; font-weight: 500; color: var(--vp-c-text-3); }
.folder { margin: 0; font-size: 13px; color: var(--vp-c-text-3); }
.note { margin: 4px 0 8px; color: var(--vp-c-text-2); font-size: 14px; }
.mark {
  margin: 6px 0 4px;
  padding: 3px 12px;
  border: 1px solid var(--vp-c-divider);
  border-radius: 6px;
  color: var(--vp-c-text-2);
  font-size: 13px;
}
.mark:hover { border-color: var(--pe-pass); color: var(--pe-pass); }
/* 固定列宽：每个阶段一张表，列宽一致，上下对得齐 */
table { display: table; width: 100%; table-layout: fixed; margin: 10px 0 0; font-size: 14px; }
th { white-space: nowrap; }
td, th { padding: 7px 12px; vertical-align: top; }
.c-n { width: 5.5em; font-family: var(--vp-font-family-mono); color: var(--vp-c-text-2); white-space: nowrap; }
.c-title { width: 36%; }
.c-goal { color: var(--vp-c-text-2); }
.c-state { width: 6em; white-space: nowrap; }
.c-title > a { font-weight: 600; text-decoration: none; }
.c-title a:hover { text-decoration: underline; }
tr.todo .c-title { color: var(--vp-c-text-2); }
.subs { display: flex; flex-wrap: wrap; gap: 2px 12px; margin-top: 2px; font-size: 13px; }
.subs a { text-decoration: none; }
.subs .rec { color: var(--vp-c-text-3); }
.project {
  display: inline-block;
  margin-left: 8px;
  padding: 0 8px;
  border-radius: 999px;
  background: var(--vp-c-brand-soft);
  color: var(--vp-c-brand-1);
  font-size: 12px;
  white-space: nowrap;
}
.lnote { display: block; color: var(--pe-hint); font-size: 13px; }
.st { font-size: 13px; }
.st.pass { color: var(--pe-pass); font-weight: 600; }
.st.next {
  padding: 2px 9px;
  border-radius: 6px;
  background: var(--vp-c-brand-1);
  color: var(--vp-c-white);
  font-weight: 600;
}
.st.open { color: var(--vp-c-brand-1); }
.st.todo { color: var(--vp-c-text-3); }
.extras { margin-top: 12px; font-size: 14px; }
.extras ul { margin: 6px 0 0; padding-left: 1.2em; columns: 2; }
.extras li { margin: 2px 0; }
@media (max-width: 760px) {
  .c-goal { display: none; }
  .c-title { width: auto; }
  .extras ul { columns: 1; }
}
</style>
