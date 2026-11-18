<script setup lang="ts">
// 讲评先收起来：做完题再看。这一页标记过「已完成」的话，直接展开。
import { computed, nextTick, onMounted, ref } from 'vue'
import { useRoute } from 'vitepress'
import { isDone, loadProgress } from './progress'

const route = useRoute()
const opened = ref(false)
const body = ref<HTMLElement>()

onMounted(() => {
  loadProgress()
  if (isDone(route.path)) opened.value = true
})

const shown = computed(() => opened.value)

async function open() {
  opened.value = true
  await nextTick()
  body.value?.querySelector('h2')?.scrollIntoView({ behavior: 'smooth', block: 'start' })
}
</script>

<template>
  <section class="reveal">
    <div v-if="!shown" class="gate">
      <p class="gate-title">讲评和复盘在下面</p>
      <p class="gate-text">先把题做完，跑一遍测试。卡住了就看上面的提示，提示不够再展开讲评。</p>
      <button type="button" class="gate-btn" @click="open">我做完了，看讲评</button>
    </div>
    <div v-show="shown" ref="body" class="reveal-body">
      <slot />
    </div>
  </section>
</template>

<style scoped>
.reveal { margin-top: 40px; }
.gate {
  padding: 28px 28px 26px;
  border: 1px dashed var(--vp-c-divider);
  border-radius: 10px;
  background: var(--vp-c-bg-alt);
}
.gate-title { margin: 0; font-size: 17px; font-weight: 700; color: var(--vp-c-text-1); }
.gate-text { margin: 6px 0 18px; color: var(--vp-c-text-2); line-height: 1.7; }
.gate-btn {
  padding: 9px 20px;
  border-radius: 8px;
  background: var(--vp-c-brand-1);
  color: var(--vp-c-white);
  font-weight: 600;
  font-size: 15px;
  transition: background-color 0.2s;
}
.gate-btn:hover { background: var(--vp-c-brand-2); }
.gate-btn:focus-visible { outline: 2px solid var(--vp-c-brand-1); outline-offset: 3px; }
.reveal-body { animation: unfold 0.35s ease-out; }
@keyframes unfold {
  from { opacity: 0; transform: translateY(6px); }
  to { opacity: 1; transform: none; }
}
@media (prefers-reduced-motion: reduce) {
  .reveal-body { animation: none; }
}
</style>
