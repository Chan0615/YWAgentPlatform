<template>
  <div class="dashboard-page">
    <!-- Welcome Banner -->
    <div class="welcome-card">
      <div class="welcome-info">
        <h2 class="welcome-title">{{ greeting }}，{{ userStore.userInfo?.nickname || '用户' }}</h2>
        <p class="welcome-desc">欢迎使用 YW.OPS 统一运维管理平台，祝您工作顺利</p>
      </div>
      <div class="welcome-date">
        <p class="date-text">{{ currentDate }}</p>
        <p class="time-text">{{ currentTime }}</p>
      </div>
    </div>

    <!-- Statistics Cards -->
    <a-row :gutter="16" class="stat-row">
      <a-col :xs="24" :sm="12" :md="6">
        <div class="stat-card stat-card--orange">
          <div class="stat-icon stat-icon--orange">
            <AppstoreOutlined />
          </div>
          <div class="stat-content">
            <span class="stat-value">{{ stats.totalApps }}</span>
            <span class="stat-label">注册应用</span>
          </div>
        </div>
      </a-col>
      <a-col :xs="24" :sm="12" :md="6">
        <div class="stat-card stat-card--green">
          <div class="stat-icon stat-icon--green">
            <UserOutlined />
          </div>
          <div class="stat-content">
            <span class="stat-value">{{ stats.totalUsers }}</span>
            <span class="stat-label">在线用户</span>
          </div>
        </div>
      </a-col>
      <a-col :xs="24" :sm="12" :md="6">
        <div class="stat-card stat-card--blue">
          <div class="stat-icon stat-icon--blue">
            <ThunderboltOutlined />
          </div>
          <div class="stat-content">
            <span class="stat-value">{{ stats.todayOperations }}</span>
            <span class="stat-label">今日操作</span>
          </div>
        </div>
      </a-col>
      <a-col :xs="24" :sm="12" :md="6">
        <div class="stat-card stat-card--purple">
          <div class="stat-icon stat-icon--purple">
            <TeamOutlined />
          </div>
          <div class="stat-content">
            <span class="stat-value">{{ stats.totalRoles }}</span>
            <span class="stat-label">系统角色</span>
          </div>
        </div>
      </a-col>
    </a-row>

    <!-- Bottom Section -->
    <a-row :gutter="16" class="content-row">
      <!-- Recent Operations Table -->
      <a-col :xs="24" :lg="16">
        <div class="section-card">
          <div class="section-header">
            <h3 class="section-title">最近操作</h3>
          </div>
          <a-table
            :columns="auditColumns"
            :data-source="recentLogs"
            :loading="logsLoading"
            :pagination="false"
            size="middle"
            row-key="id"
          >
            <template #bodyCell="{ column, record }">
              <template v-if="column.dataIndex === 'username'">
                <span class="cell-user">{{ record.username || '-' }}</span>
              </template>
              <template v-if="column.dataIndex === 'action'">
                <a-tag :color="getActionColor(record.action)" size="small">
                  {{ record.action }}
                </a-tag>
              </template>
              <template v-if="column.dataIndex === 'resource_type'">
                {{ record.resource_type || '-' }}
              </template>
              <template v-if="column.dataIndex === 'ip_address'">
                <span class="cell-ip">{{ record.ip_address || '-' }}</span>
              </template>
              <template v-if="column.dataIndex === 'created_at'">
                <span class="cell-time">{{ formatTime(record.created_at) }}</span>
              </template>
            </template>
          </a-table>
        </div>
      </a-col>

      <!-- Quick Access -->
      <a-col :xs="24" :lg="8">
        <div class="section-card">
          <div class="section-header">
            <h3 class="section-title">快捷入口</h3>
          </div>
          <div class="shortcut-grid">
            <div
              v-for="item in shortcuts"
              :key="item.path"
              class="shortcut-item"
              @click="router.push(item.path)"
            >
              <div class="shortcut-icon" :style="{ background: item.color }">
                <component :is="item.icon" />
              </div>
              <span class="shortcut-label">{{ item.label }}</span>
            </div>
          </div>
        </div>
      </a-col>
    </a-row>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, markRaw } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/store/user'
import {
  AppstoreOutlined,
  UserOutlined,
  ThunderboltOutlined,
  TeamOutlined,
  SettingOutlined,
  SafetyOutlined,
  FileSearchOutlined,
  DashboardOutlined,
} from '@ant-design/icons-vue'
import { getAuditLogListApi, type AuditLogRecord } from '@/api/audit'
import dayjs from 'dayjs'

const router = useRouter()
const userStore = useUserStore()

// Time-based greeting
const greeting = computed(() => {
  const hour = new Date().getHours()
  if (hour < 12) return '早上好'
  if (hour < 18) return '下午好'
  return '晚上好'
})

const currentDate = ref(dayjs().format('YYYY年MM月DD日'))
const currentTime = ref(dayjs().format('HH:mm:ss'))
let timer: ReturnType<typeof setInterval> | null = null

// Statistics
const stats = ref({
  totalApps: 12,
  totalUsers: 86,
  todayOperations: 234,
  totalRoles: 8,
})

// Audit logs
const recentLogs = ref<AuditLogRecord[]>([])
const logsLoading = ref(false)

const auditColumns = [
  { title: '用户', dataIndex: 'username', width: 100 },
  { title: '操作', dataIndex: 'action', width: 100 },
  { title: '资源', dataIndex: 'resource_type', width: 120 },
  { title: 'IP', dataIndex: 'ip_address', width: 130 },
  { title: '时间', dataIndex: 'created_at', width: 160 },
]

// Quick shortcuts
const shortcuts = [
  { label: '应用中心', path: '/app-center', icon: markRaw(AppstoreOutlined), color: 'rgba(245,130,13,0.1)' },
  { label: '用户管理', path: '/system/users', icon: markRaw(UserOutlined), color: 'rgba(82,196,26,0.1)' },
  { label: '角色管理', path: '/system/roles', icon: markRaw(TeamOutlined), color: 'rgba(114,46,209,0.1)' },
  { label: '权限管理', path: '/system/permissions', icon: markRaw(SafetyOutlined), color: 'rgba(24,144,255,0.1)' },
  { label: '审计日志', path: '/system/audit-log', icon: markRaw(FileSearchOutlined), color: 'rgba(250,173,20,0.1)' },
  { label: '系统设置', path: '/system/users', icon: markRaw(SettingOutlined), color: 'rgba(235,47,150,0.1)' },
]

function getActionColor(action: string): string {
  const map: Record<string, string> = {
    CREATE: 'green',
    UPDATE: 'blue',
    DELETE: 'red',
    LOGIN: 'purple',
    LOGOUT: 'orange',
  }
  return map[action?.toUpperCase()] || 'default'
}

function formatTime(time: string): string {
  return dayjs(time).format('MM-DD HH:mm:ss')
}

async function fetchRecentLogs() {
  logsLoading.value = true
  try {
    const res = await getAuditLogListApi({ page: 1, page_size: 8 })
    recentLogs.value = res.items || []
  } catch {
    // Error handled by interceptor
  } finally {
    logsLoading.value = false
  }
}

onMounted(() => {
  fetchRecentLogs()
  timer = setInterval(() => {
    currentTime.value = dayjs().format('HH:mm:ss')
    currentDate.value = dayjs().format('YYYY年MM月DD日')
  }, 1000)
})

onUnmounted(() => {
  if (timer) {
    clearInterval(timer)
    timer = null
  }
})
</script>

<style scoped>
.dashboard-page {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* ===== Welcome Banner ===== */
.welcome-card {
  background: #fff;
  border-radius: 10px;
  padding: 28px 32px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);
}

.welcome-title {
  font-size: 22px;
  font-weight: 600;
  color: #1a1a2e;
  margin: 0 0 8px;
}

.welcome-desc {
  font-size: 14px;
  color: #888;
  margin: 0;
}

.welcome-date {
  text-align: right;
}

.date-text {
  font-size: 14px;
  color: #666;
  margin: 0 0 4px;
}

.time-text {
  font-size: 20px;
  font-weight: 600;
  color: #1a1a2e;
  margin: 0;
  font-variant-numeric: tabular-nums;
}

/* ===== Stat Cards ===== */
.stat-row {
  margin: 0;
}

.stat-card {
  background: #fff;
  border-radius: 10px;
  padding: 20px 24px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);
  border-left: 4px solid transparent;
  transition: transform 0.2s, box-shadow 0.2s;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.stat-card--orange {
  border-left-color: #F5820D;
}

.stat-card--green {
  border-left-color: #52c41a;
}

.stat-card--blue {
  border-left-color: #1890ff;
}

.stat-card--purple {
  border-left-color: #722ed1;
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
  flex-shrink: 0;
}

.stat-icon--orange {
  background: rgba(245, 130, 13, 0.1);
  color: #F5820D;
}

.stat-icon--green {
  background: rgba(82, 196, 26, 0.1);
  color: #52c41a;
}

.stat-icon--blue {
  background: rgba(24, 144, 255, 0.1);
  color: #1890ff;
}

.stat-icon--purple {
  background: rgba(114, 46, 209, 0.1);
  color: #722ed1;
}

.stat-content {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 26px;
  font-weight: 700;
  color: #1a1a2e;
  line-height: 1.2;
  font-variant-numeric: tabular-nums;
}

.stat-label {
  font-size: 13px;
  color: #999;
  margin-top: 2px;
}

/* ===== Section Cards ===== */
.content-row {
  margin: 0;
}

.section-card {
  background: #fff;
  border-radius: 10px;
  padding: 20px 24px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);
  height: 100%;
}

.section-header {
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #f5f5f5;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: #1a1a2e;
  margin: 0;
}

/* Table cells */
.cell-user {
  font-weight: 500;
  color: #333;
}

.cell-ip {
  font-family: 'SF Mono', 'Monaco', 'Menlo', monospace;
  font-size: 12px;
  color: #666;
}

.cell-time {
  color: #999;
  font-size: 12px;
}

/* ===== Shortcut Grid ===== */
.shortcut-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.shortcut-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 16px 8px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.shortcut-item:hover {
  background: #f9f9f9;
  transform: translateY(-2px);
}

.shortcut-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  color: #F5820D;
}

.shortcut-label {
  font-size: 12px;
  color: #666;
  text-align: center;
}

/* ===== Responsive ===== */
@media (max-width: 768px) {
  .welcome-card {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .welcome-date {
    text-align: left;
  }

  .shortcut-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}
</style>
