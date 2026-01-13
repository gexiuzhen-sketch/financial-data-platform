import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('../views/Home.vue')
  },
  {
    path: '/platform',
    name: 'PlatformData',
    component: () => import('../views/PlatformData.vue')
  },
  {
    path: '/bank',
    name: 'BankData',
    component: () => import('../views/BankData.vue')
  },
  {
    path: '/admin',
    name: 'Admin',
    component: () => import('../views/Admin.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
