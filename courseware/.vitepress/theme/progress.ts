// 学习进度存在浏览器的 localStorage 里，只在本机有效，不上传任何地方。
import { ref } from 'vue'

const KEY = 'pe-course-done'

function read(): Set<string> {
  if (typeof localStorage === 'undefined') return new Set()
  try {
    return new Set(JSON.parse(localStorage.getItem(KEY) ?? '[]') as string[])
  } catch {
    return new Set()
  }
}

// 所有组件共用一份，标记完成后首页进度条立刻跟着变
export const done = ref<Set<string>>(new Set())

export function loadProgress(): void {
  done.value = read()
}

export function normalize(path: string): string {
  return decodeURI(path).replace(/\.html$/, '').replace(/\/$/, '')
}

export function isDone(link: string): boolean {
  return done.value.has(normalize(link))
}

export function toggleDone(link: string): void {
  const next = new Set(done.value)
  const key = normalize(link)
  if (next.has(key)) next.delete(key)
  else next.add(key)
  done.value = next
  localStorage.setItem(KEY, JSON.stringify([...next]))
}
