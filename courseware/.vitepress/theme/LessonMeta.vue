<script setup lang="ts">
// 题目页标题下面的一条信息：多长时间、用到哪些知识、对应哪几天的学习记录。
import { computed } from 'vue'
import { useData } from 'vitepress'

const { frontmatter } = useData()
const meta = computed(() => frontmatter.value as {
  kind?: string; time?: string; uses?: string[]; record?: { text: string; link: string }[]
})
</script>

<template>
  <dl v-if="meta.kind === 'problem'" class="meta">
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
