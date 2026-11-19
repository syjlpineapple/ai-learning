import DefaultTheme from 'vitepress/theme'
import type { Theme } from 'vitepress'
import { h } from 'vue'
import CourseCards from './CourseCards.vue'
import CourseRun from './CourseRun.vue'
import DoneButton from './DoneButton.vue'
import LessonMeta from './LessonMeta.vue'
import Reveal from './Reveal.vue'
import SidebarDone from './SidebarDone.vue'
import Syllabus from './Syllabus.vue'
import './custom.css'

export default {
  extends: DefaultTheme,
  Layout: () =>
    h(DefaultTheme.Layout, null, {
      'doc-before': () => h(LessonMeta),
      'doc-footer-before': () => h(DoneButton),
      'sidebar-nav-after': () => h(SidebarDone),
    }),
  enhanceApp({ app }) {
    app.component('CourseCards', CourseCards)
    app.component('CourseRun', CourseRun)
    app.component('Reveal', Reveal)
    app.component('Syllabus', Syllabus)
  },
} satisfies Theme
