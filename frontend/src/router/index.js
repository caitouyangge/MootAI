import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('@/views/Home.vue'),
    },
  ],
})

// 路由守卫
router.beforeEach((to, from, next) => {
  // 可以在这里添加认证逻辑
  next()
})

export default router

