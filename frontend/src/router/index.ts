import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
import NProgress from 'nprogress'
import { useUserStore } from '@/store/user'
import { getToken } from '@/utils/auth'

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/login/index.vue'),
    meta: { title: '登录', public: true },
  },
  {
    path: '/',
    component: () => import('@/layouts/MainLayout.vue'),
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/dashboard/index.vue'),
        meta: { title: '工作台', icon: 'DashboardOutlined' },
      },
      {
        path: 'app-center',
        name: 'AppCenter',
        component: () => import('@/views/app-center/index.vue'),
        meta: { title: '应用中心', icon: 'AppstoreOutlined' },
      },
      {
        path: 'app-container/:appId',
        name: 'AppContainer',
        component: () => import('@/views/app-container/index.vue'),
        meta: { title: '子应用', hidden: true },
      },
      {
        path: 'system',
        name: 'System',
        redirect: '/system/users',
        meta: { title: '系统管理', icon: 'SettingOutlined' },
        children: [
          {
            path: 'users',
            name: 'UserManagement',
            component: () => import('@/views/system/user/index.vue'),
            meta: { title: '用户管理', permission: 'menu:user' },
          },
          {
            path: 'roles',
            name: 'RoleManagement',
            component: () => import('@/views/system/role/index.vue'),
            meta: { title: '角色管理', permission: 'menu:role' },
          },
          {
            path: 'permissions',
            name: 'PermissionManagement',
            component: () => import('@/views/system/permission/index.vue'),
            meta: { title: '权限管理', permission: 'menu:permission' },
          },
          {
            path: 'applications',
            name: 'ApplicationManagement',
            component: () => import('@/views/system/application/index.vue'),
            meta: { title: '应用管理', permission: 'menu:application' },
          },
          {
            path: 'audit-log',
            name: 'AuditLog',
            component: () => import('@/views/system/audit-log/index.vue'),
            meta: { title: '审计日志', permission: 'menu:audit' },
          },
        ],
      },
    ],
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/not-found/index.vue'),
    meta: { title: '404', public: true },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

const whiteList = ['/login']

router.beforeEach(async (to, _from, next) => {
  NProgress.start()
  document.title = `${to.meta.title || ''} - YW.Ops 运维管理平台`

  const token = getToken()

  if (token) {
    if (to.path === '/login') {
      next({ path: '/' })
    } else {
      const userStore = useUserStore()
      if (userStore.permissions.length === 0) {
        try {
          await userStore.fetchUserInfo()
          next({ ...to, replace: true })
        } catch {
          userStore.resetState()
          next(`/login?redirect=${to.path}`)
        }
      } else {
        next()
      }
    }
  } else {
    if (whiteList.includes(to.path) || to.meta.public) {
      next()
    } else {
      next(`/login?redirect=${to.path}`)
    }
  }
})

router.afterEach(() => {
  NProgress.done()
})

export default router
