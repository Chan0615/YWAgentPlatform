<template>
  <a-layout class="main-layout">
    <!-- Sidebar -->
    <a-layout-sider
      v-model:collapsed="appStore.collapsed"
      :trigger="null"
      collapsible
      breakpoint="lg"
      :collapsed-width="64"
      :width="220"
      class="layout-sider"
      @breakpoint="onBreakpoint"
    >
      <!-- Logo -->
      <div class="sider-logo">
        <span class="logo-yw">YW</span>
        <span v-show="!appStore.collapsed" class="logo-ops">OPS</span>
      </div>

      <!-- Navigation Menu -->
      <a-menu
        v-model:selectedKeys="selectedKeys"
        v-model:openKeys="openKeys"
        theme="dark"
        mode="inline"
        class="sider-menu"
        @click="onMenuClick"
      >
        <a-menu-item key="/dashboard">
          <template #icon><DashboardOutlined /></template>
          <span>工作台</span>
        </a-menu-item>
        <a-menu-item key="/app-center">
          <template #icon><AppstoreOutlined /></template>
          <span>应用中心</span>
        </a-menu-item>
        <a-sub-menu key="/system">
          <template #icon><SettingOutlined /></template>
          <template #title>系统管理</template>
          <a-menu-item key="/system/users">
            <template #icon><UserOutlined /></template>
            <span>用户管理</span>
          </a-menu-item>
          <a-menu-item key="/system/roles">
            <template #icon><TeamOutlined /></template>
            <span>角色管理</span>
          </a-menu-item>
          <a-menu-item key="/system/permissions">
            <template #icon><SafetyOutlined /></template>
            <span>权限管理</span>
          </a-menu-item>
          <a-menu-item key="/system/audit-log">
            <template #icon><FileSearchOutlined /></template>
            <span>审计日志</span>
          </a-menu-item>
        </a-sub-menu>
      </a-menu>
    </a-layout-sider>

    <!-- Main Content Area -->
    <a-layout class="layout-main" :style="{ marginLeft: appStore.collapsed ? '64px' : '220px' }">
      <!-- Header -->
      <a-layout-header class="layout-header">
        <div class="header-left">
          <span class="collapse-trigger" @click="appStore.toggleCollapsed">
            <MenuUnfoldOutlined v-if="appStore.collapsed" />
            <MenuFoldOutlined v-else />
          </span>
          <a-breadcrumb class="header-breadcrumb">
            <a-breadcrumb-item v-for="item in breadcrumbs" :key="item.path">
              <router-link v-if="item.path" :to="item.path">{{ item.title }}</router-link>
              <span v-else>{{ item.title }}</span>
            </a-breadcrumb-item>
          </a-breadcrumb>
        </div>
        <div class="header-right">
          <a-badge :count="3" :offset="[-2, 4]" class="header-action">
            <BellOutlined class="action-icon" />
          </a-badge>
          <a-dropdown placement="bottomRight">
            <span class="user-dropdown">
              <a-avatar :size="32" class="user-avatar">
                {{ userStore.userInfo?.nickname?.charAt(0) || 'U' }}
              </a-avatar>
              <span class="user-name">{{ userStore.userInfo?.nickname || '用户' }}</span>
            </span>
            <template #overlay>
              <a-menu>
                <a-menu-item key="profile">
                  <UserOutlined />
                  <span style="margin-left: 8px">个人中心</span>
                </a-menu-item>
                <a-menu-divider />
                <a-menu-item key="logout" @click="handleLogout">
                  <LogoutOutlined />
                  <span style="margin-left: 8px">退出登录</span>
                </a-menu-item>
              </a-menu>
            </template>
          </a-dropdown>
        </div>
      </a-layout-header>

      <!-- Content -->
      <a-layout-content class="layout-content">
        <router-view />
      </a-layout-content>
    </a-layout>
  </a-layout>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/store/user'
import { useAppStore } from '@/store/app'
import {
  DashboardOutlined,
  AppstoreOutlined,
  SettingOutlined,
  UserOutlined,
  TeamOutlined,
  SafetyOutlined,
  FileSearchOutlined,
  MenuUnfoldOutlined,
  MenuFoldOutlined,
  BellOutlined,
  LogoutOutlined,
} from '@ant-design/icons-vue'
import { Modal } from 'ant-design-vue'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()
const appStore = useAppStore()

const selectedKeys = ref<string[]>([route.path])
const openKeys = ref<string[]>([])

// Menu title map for breadcrumb
const menuTitleMap: Record<string, string> = {
  '/dashboard': '工作台',
  '/app-center': '应用中心',
  '/system': '系统管理',
  '/system/users': '用户管理',
  '/system/roles': '角色管理',
  '/system/permissions': '权限管理',
  '/system/audit-log': '审计日志',
}

const breadcrumbs = computed(() => {
  const path = route.path
  const items: Array<{ title: string; path?: string }> = []

  if (path === '/dashboard') {
    items.push({ title: '工作台' })
  } else {
    const segments = path.split('/').filter(Boolean)
    let currentPath = ''
    for (const segment of segments) {
      currentPath += `/${segment}`
      const title = menuTitleMap[currentPath]
      if (title) {
        items.push({ title, path: currentPath })
      }
    }
  }
  return items
})

watch(
  () => route.path,
  (path) => {
    selectedKeys.value = [path]
    const parts = path.split('/')
    if (parts.length > 2) {
      openKeys.value = [`/${parts[1]}`]
    }
  },
  { immediate: true }
)

function onMenuClick({ key }: { key: string }) {
  router.push(key)
}

function onBreakpoint(broken: boolean) {
  appStore.setCollapsed(broken)
}

function handleLogout() {
  Modal.confirm({
    title: '确认退出',
    content: '确定要退出登录吗？',
    okButtonProps: { style: { backgroundColor: '#F5820D', borderColor: '#F5820D' } },
    onOk: async () => {
      await userStore.logout()
      router.push('/login')
    },
  })
}
</script>

<style scoped>
.main-layout {
  min-height: 100vh;
}

/* ===== Sidebar ===== */
.layout-sider {
  overflow: auto;
  height: 100vh;
  position: fixed;
  left: 0;
  top: 0;
  bottom: 0;
  z-index: 100;
  background: #1a1a2e !important;
}

.layout-sider :deep(.ant-layout-sider-children) {
  display: flex;
  flex-direction: column;
  background: #1a1a2e;
}

/* Logo */
.sider-logo {
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 0 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.logo-yw {
  font-size: 24px;
  font-weight: 800;
  color: #F5820D;
  letter-spacing: -1px;
}

.logo-ops {
  font-size: 18px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
  letter-spacing: 1px;
}

/* Menu Styling */
.sider-menu {
  flex: 1;
  border-right: none !important;
  background: #1a1a2e !important;
  padding: 8px 0;
}

.sider-menu :deep(.ant-menu-item),
.sider-menu :deep(.ant-menu-submenu-title) {
  margin: 2px 8px;
  border-radius: 6px;
  color: rgba(255, 255, 255, 0.65);
}

.sider-menu :deep(.ant-menu-item:hover),
.sider-menu :deep(.ant-menu-submenu-title:hover) {
  color: #fff;
  background: rgba(245, 130, 13, 0.1) !important;
}

.sider-menu :deep(.ant-menu-item-selected) {
  background: #F5820D !important;
  color: #fff !important;
}

.sider-menu :deep(.ant-menu-item-selected .anticon) {
  color: #fff !important;
}

.sider-menu :deep(.ant-menu-sub) {
  background: rgba(0, 0, 0, 0.15) !important;
}

.sider-menu :deep(.ant-menu-submenu-open > .ant-menu-submenu-title) {
  color: #fff;
}

/* ===== Main Layout ===== */
.layout-main {
  transition: margin-left 0.2s ease;
  min-height: 100vh;
  background: #f5f6fa;
}

/* ===== Header ===== */
.layout-header {
  background: #fff;
  padding: 0 24px;
  height: 56px;
  line-height: 56px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid #f0f0f0;
  position: sticky;
  top: 0;
  z-index: 99;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.collapse-trigger {
  font-size: 18px;
  cursor: pointer;
  color: #333;
  padding: 4px 8px;
  border-radius: 4px;
  transition: all 0.2s;
}

.collapse-trigger:hover {
  color: #F5820D;
  background: rgba(245, 130, 13, 0.06);
}

.header-breadcrumb {
  line-height: 56px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 24px;
}

.header-action {
  cursor: pointer;
}

.action-icon {
  font-size: 18px;
  color: #555;
  transition: color 0.2s;
}

.action-icon:hover {
  color: #F5820D;
}

.user-dropdown {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 6px;
  transition: background 0.2s;
}

.user-dropdown:hover {
  background: #f5f5f5;
}

.user-avatar {
  background: linear-gradient(135deg, #F5820D, #FF6B35);
  color: #fff;
  font-weight: 600;
}

.user-name {
  font-size: 14px;
  color: #333;
  font-weight: 500;
}

/* ===== Content ===== */
.layout-content {
  margin: 24px;
  min-height: calc(100vh - 56px - 48px);
}
</style>
