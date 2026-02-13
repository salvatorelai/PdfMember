import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '../stores/user'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('../views/HomeView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/document/:id',
      name: 'document-detail',
      component: () => import('../views/document/Detail.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/document/:id/read',
      name: 'document-viewer',
      component: () => import('../views/document/Viewer.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/membership',
      name: 'membership',
      component: () => import('../views/user/Membership.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/login/index.vue')
    },
    {
      path: '/download-verify/:token',
      name: 'download-verify',
      component: () => import('../views/DownloadVerify.vue'),
      meta: { requiresAuth: false }
    },
    {
      path: '/admin',
      component: () => import('../views/admin/Layout.vue'),
      meta: { requiresAuth: true, roles: ['admin', 'super_admin'] },
      children: [
        {
          path: '',
          redirect: '/admin/dashboard'
        },
        {
          path: 'dashboard',
          name: 'admin-dashboard',
          component: () => import('../views/admin/Dashboard.vue'),
          meta: { title: 'Dashboard' }
        },
        {
          path: 'users',
          name: 'admin-users',
          component: () => import('../views/admin/Users.vue'),
          meta: { title: 'User Management' }
        },
        {
          path: 'documents',
          name: 'admin-documents',
          component: () => import('../views/admin/Documents.vue'),
          meta: { title: 'Document Management' }
        },
        {
          path: 'categories',
          name: 'admin-categories',
          component: () => import('../views/admin/Categories.vue'),
          meta: { title: 'Category Management' }
        },
        {
          path: 'settings',
          name: 'admin-settings',
          component: () => import('../views/admin/Settings.vue'),
          meta: { title: 'System Settings' }
        }
      ]
    },
    {
      path: '/403',
      name: '403',
      component: () => import('../views/error/403.vue')
    }
  ]
})

router.beforeEach(async (to, from, next) => {
  const userStore = useUserStore()
  const hasToken = userStore.token

  if (hasToken) {
    if (to.path === '/login') {
      next({ path: '/' })
    } else {
      // Check if user info is loaded
      if (userStore.roles && userStore.roles.length > 0) {
        // Check permission
        if (to.meta.roles) {
          const requiredRoles = to.meta.roles as string[]
          const hasRole = userStore.roles.some(role => requiredRoles.includes(role.toLowerCase()))
          if (hasRole) {
            next()
          } else {
            next({ path: '/403' }) // Redirect to 403 or home
          }
        } else {
          next()
        }
      } else {
        try {
          await userStore.getUserInfo()
          // Hack: trigger re-check
          next({ ...to, replace: true })
        } catch (error) {
          userStore.logout()
          next(`/login?redirect=${to.path}`)
        }
      }
    }
  } else {
    if (to.meta.requiresAuth) {
      next(`/login?redirect=${to.path}`)
    } else {
      next()
    }
  }
})

export default router
