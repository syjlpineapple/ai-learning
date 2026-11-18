import DefaultTheme from 'vitepress/theme'
import type { Theme } from 'vitepress'
import { h } from 'vue'
import CourseRun from './CourseRun.vue'
import DoneButton from './DoneButton.vue'
import LessonMeta from './LessonMeta.vue'
import Reveal from './Reveal.vue'
import './custom.css'

export default {
  extends: DefaultTheme,
  Layout: () =>
    h(DefaultTheme.Layout, null, {
      'doc-before': () => h(LessonMeta),
      'doc-footer-before': () => h(DoneButton),
    }),
  enhanceApp({ app }) {
    app.component('CourseRun', CourseRun)
    app.component('Reveal', Reveal)
  },
} satisfies Theme
