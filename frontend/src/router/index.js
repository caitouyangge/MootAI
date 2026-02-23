import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'welcome',
      component: () => import('@/views/Welcome.vue'),
      meta: { transition: 'fade' }
    },
    {
      path: '/home',
      name: 'home',
      component: () => import('@/components/Layout.vue'),
      children: [
        {
          path: '',
          name: 'home-content',
          component: () => import('@/views/Home.vue'),
          meta: { transition: 'page' }
        }
      ]
    },
    {
      path: '/courtroom',
      name: 'courtroom',
      component: () => import('@/components/Layout.vue'),
      children: [
        {
          path: '',
          name: 'courtroom-content',
          component: () => import('@/views/Courtroom.vue'),
          meta: { transition: 'page' }
        }
      ]
    },
  ],
})

// 路由守卫
router.beforeEach((to, from, next) => {
  // 可以在这里添加认证逻辑
  next()
})

router.onError((error) => {
  console.error('路由错误:', error)
})

export default router

