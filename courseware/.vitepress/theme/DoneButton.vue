<script setup lang="ts">
// 每一课正文末尾的「标记为已完成」。课表、进度条、左边目录的打勾读的都是这里存的状态。
import { computed, onMounted } from 'vue'
import { useData, useRoute } from 'vitepress'
import { findLesson } from '../lessons'
import { done, isDone, loadProgress, toggleDone } from './progress'

const route = useRoute()
const { frontmatter } = useData()
onMounted(loadProgress)

// 只在课程里的某一课显示，课表页、知识点索引不显示
const visible = computed(() => frontmatter.value.layout !== 'home' && !!findLesson(route.path))
const finished = computed(() => {
  void done.value
  return isDone(route.path)
})
</script>

<template>
  <div v-if="visible" class="done">
    <button
      type="button"
      :class="['done-btn', finished ? 'is-done' : '']"
      :aria-pressed="finished"
      @click="toggleDone(route.path)"
    >
      {{ finished ? '已完成' : '标记为已完成' }}
    </button>
    <span class="done-note">{{ finished ? '再点一次可以撤销' : '左边目录会给这一课打勾，课表里也会更新' }}</span>
  </div>
</template>

<style scoped>
.done {
  display: flex;
  align-items: center;
  gap: 14px;
  margin: 48px 0 28px;
}
.done-btn {
  padding: 7px 16px;
  border: 1px solid var(--pe-pass);
  border-radius: 8px;
  color: var(--pe-pass);
  font-weight: 600;
  font-size: 14px;
  transition: background-color 0.2s, color 0.2s;
}
.done-btn:hover { background: var(--pe-pass-soft); }
.done-btn.is-done { background: var(--pe-pass); color: #fff; }
.done-btn:focus-visible { outline: 2px solid var(--pe-pass); outline-offset: 3px; }
.done-note { color: var(--vp-c-text-3); font-size: 13px; }
</style>
