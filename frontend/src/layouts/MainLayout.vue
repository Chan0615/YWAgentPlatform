<template>
  <a-layout class="main-layout">
    <!-- Sidebar -->
    <a-layout-sider
      v-model:collapsed="appStore.collapsed"
      :trigger="null"
      collapsible
      breakpoint="lg"
      :collapsed-width="60"
      class="layout-sider"
      @breakpoint="onBreakpoint"
    >
      <div class="logo">
        <img src="/vite.svg" alt="logo" class="logo-img" />
        <span v-show="!appStore.collapsed" class="logo-text">YW.Ops</span>
      </div>
      <a-menu
        v-model:selectedKeys="selectedKeys"
        v-model:openKeys="openKeys"
        theme="dark"
        mode="inline"
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
            <template #icon><AuditOutlined /></template>
            <span>审计日志</span>
          </a-menu-item>
        </a-sub-menu>
      </a-menu>
    </a-layout-sider>

    <!-- Main Content -->
    <a-layout>
      <!-- Header -->
      <a-layout-header class="layout-header">
        <div class="header-left">
          <MenuUnfoldOutlined
            v-if="appStore.collapsed"
            class="trigger"
            @click="appStore.toggleCollapsed"
          />
          <MenuFoldOutlined
            v-else
            class="trigger"
            @click="appStore.toggleCollapsed"
          />
        </div>
        <div class="header-right">
          <a-badge :count="3" class="header-action">
            <BellOutlined class="action-icon" />
          </a-badge>
          <a-dropdown>
            <span class="user-dropdown">
              <a-avatar size="small" class="user-avatar">
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

      <!-- Footer -->
      <a-layout-footer class="layout-footer">
        YW.Ops 运维管理平台 &copy; {{ new Date().getFullYear() }} YW Operations Team
      </a-layout-footer>
    </a-layout>
  </a-layout>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
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
  AuditOutlined,
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

watch(
  () => route.path,
  (path) => {
    selectedKeys.value = [path]
    // Auto-open parent menu
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

.layout-sider {
  overflow: auto;
  height: 100vh;
  position: fixed;
  left: 0;
  top: 0;
  bottom: 0;
  z-index: 10;
}

.layout-sider + .ant-layout {
  margin-left: 200px;
  transition: margin-left 0.2s;
}

.layout-sider.ant-layout-sider-collapsed + .ant-layout {
  margin-left: 60px;
}

.logo {
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 16px;
  gap: 8px;
}

.logo-img {
  width: 32px;
  height: 32px;
}

.logo-text {
  color: #fff;
  font-size: 18px;
  font-weight: 700;
  white-space: nowrap;
}

.layout-header {
  background: #fff;
  padding: 0 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
  position: sticky;
  top: 0;
  z-index: 9;
}

.header-left {
  display: flex;
  align-items: center;
}

.trigger {
  font-size: 18px;
  cursor: pointer;
  transition: color 0.3s;
  padding: 0 12px;
}

.trigger:hover {
  color: #1890ff;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 20px;
}

.header-action {
  cursor: pointer;
}

.action-icon {
  font-size: 18px;
}

.user-dropdown {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 0 8px;
}

.user-avatar {
  background-color: #1890ff;
}

.user-name {
  font-size: 14px;
}

.layout-content {
  margin: 24px;
  min-height: calc(100vh - 64px - 70px - 48px);
}

.layout-footer {
  text-align: center;
  color: rgba(0, 0, 0, 0.45);
  font-size: 14px;
}
</style>
