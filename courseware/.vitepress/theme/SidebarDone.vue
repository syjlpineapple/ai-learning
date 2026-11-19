<script setup lang="ts">
// 左边目录里，做完的课前面打勾。
// 侧边栏是 VitePress 按配置生成的静态内容，「做没做完」只有浏览器知道，
// 所以在页面加载后给对应的链接加一个 class，样式在 custom.css 里。
import { nextTick, onBeforeUnmount, onMounted, watch } from 'vue'
import { useRoute } from 'vitepress'
import { done, loadProgress, normalize } from './progress'

const route = useRoute()
let observer: MutationObserver | undefined

function paint(): void {
  document.querySelectorAll<HTMLAnchorElement>('.VPSidebar a.VPLink').forEach((a) => {
    const path = normalize(new URL(a.href, location.href).pathname)
    a.classList.toggle('pe-done', done.value.has(path))
  })
}

onMounted(() => {
  loadProgress()
  paint()
  const root = document.querySelector('.VPSidebar')
  if (root) {
    observer = new MutationObserver(() => paint())
    observer.observe(root, { childList: true, subtree: true })
  }
})
onBeforeUnmount(() => observer?.disconnect())
watch([done, () => route.path], () => nextTick(paint))
</script>

<template>
  <span hidden />
</template>
