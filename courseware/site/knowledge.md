---
title: 知识点索引
aside: false
---

<script setup>
import { computed, ref } from 'vue'
import { withBase } from 'vitepress'
import { data } from './knowledge.data.ts'

const query = ref('')
const shown = computed(() => {
  const q = query.value.trim().toLowerCase()
  if (!q) return data
  return data.filter((t) =>
    t.name.toLowerCase().includes(q) || t.entries.some((e) => e.title.toLowerCase().includes(q)))
})
</script>

# 知识点索引

想查某个知识点在哪一课讲过，在这里找。每一课页面顶上「用到」那一栏列的知识点，都会自动收进来。

<input v-model="query" class="kn-search" type="search" placeholder="筛选，比如 timeout、pydantic、编码" aria-label="筛选知识点" />

<p class="kn-count">{{ shown.length }} 个知识点</p>

<dl class="kn-list">
  <template v-for="t in shown" :key="t.name">
    <dt>{{ t.name }}</dt>
    <dd>
      <a v-for="e in t.entries" :key="e.url" :href="withBase(e.url)">{{ e.title }}<small v-if="e.where">{{ e.where }}</small></a>
    </dd>
  </template>
</dl>

<style>
.kn-search {
  width: 100%;
  max-width: 28em;
  margin: 8px 0 4px;
  padding: 8px 12px;
  border: 1px solid var(--vp-c-divider);
  border-radius: 8px;
  background: var(--vp-c-bg);
  font-size: 15px;
}
.kn-search:focus { outline: none; border-color: var(--vp-c-brand-1); }
.kn-count { color: var(--vp-c-text-3); font-size: 13px; }
.kn-list { display: grid; grid-template-columns: minmax(10em, max-content) 1fr; gap: 8px 24px; margin-top: 16px; }
.kn-list dt { font-weight: 650; font-family: var(--vp-font-family-mono); font-size: 14px; }
.kn-list dd { margin: 0; display: flex; flex-wrap: wrap; gap: 4px 16px; font-size: 14px; }
.kn-list dd a { text-decoration: none; }
.kn-list dd small { margin-left: 6px; color: var(--vp-c-text-3); font-size: 12px; }
.kn-list dd a:hover { text-decoration: underline; }
@media (max-width: 640px) { .kn-list { grid-template-columns: 1fr; gap: 2px; } .kn-list dd { margin-bottom: 10px; } }
</style>
