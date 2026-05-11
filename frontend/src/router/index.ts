import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
import PerformancePage from '@/pages/PerformancePage.vue'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    redirect: '/performance',
  },
  {
    path: '/performance',
    name: 'performance',
    component: PerformancePage,
    meta: { title: 'Performance' },
  },
  {
    path: '/live',
    name: 'live',
    component: () => import('@/pages/LivePage.vue'),
    meta: { title: 'Live Map' },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.afterEach((to) => {
  const title = to.meta?.title as string | undefined
  document.title = title ? `${title} — Via Rail Dashboard` : 'Via Rail Dashboard'
})

export default router
