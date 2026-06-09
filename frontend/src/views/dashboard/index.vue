<template>
  <div class="dashboard-page">
    <!-- Welcome Banner -->
    <a-card class="welcome-card" :bordered="false">
      <a-row :gutter="16" align="middle">
        <a-col :span="18">
          <h2 class="welcome-title">
            欢迎回来，{{ userStore.userInfo?.nickname || '用户' }}
          </h2>
          <p class="welcome-desc">
            YW.Ops 统一运维管理平台 - 管理您的应用、用户和权限
          </p>
        </a-col>
        <a-col :span="6" class="welcome-time">
          <p>{{ currentTime }}</p>
        </a-col>
      </a-row>
    </a-card>

    <!-- Statistics Cards -->
    <a-row :gutter="16" class="stat-row">
      <a-col :xs="24" :sm="12" :md="6">
        <a-card :bordered="false" class="stat-card">
          <a-statistic
            title="注册应用"
            :value="stats.totalApps"
            :value-style="{ color: '#1890ff' }"
          >
            <template #prefix>
              <AppstoreOutlined />
            </template>
          </a-statistic>
        </a-card>
      </a-col>
      <a-col :xs="24" :sm="12" :md="6">
        <a-card :bordered="false" class="stat-card">
          <a-statistic
            title="系统用户"
            :value="stats.totalUsers"
            :value-style="{ color: '#52c41a' }"
          >
            <template #prefix>
              <UserOutlined />
            </template>
          </a-statistic>
        </a-card>
      </a-col>
      <a-col :xs="24" :sm="12" :md="6">
        <a-card :bordered="false" class="stat-card">
          <a-statistic
            title="今日操作"
            :value="stats.todayOperations"
            :value-style="{ color: '#faad14' }"
          >
            <template #prefix>
              <ThunderboltOutlined />
            </template>
          </a-statistic>
        </a-card>
      </a-col>
      <a-col :xs="24" :sm="12" :md="6">
        <a-card :bordered="false" class="stat-card">
          <a-statistic
            title="活跃角色"
            :value="stats.totalRoles"
            :value-style="{ color: '#722ed1' }"
          >
            <template #prefix>
              <TeamOutlined />
            </template>
          </a-statistic>
        </a-card>
      </a-col>
    </a-row>

    <!-- Recent Audit Logs -->
    <a-card title="最近操作记录" :bordered="false" class="audit-card">
      <a-table
        :columns="auditColumns"
        :data-source="recentLogs"
        :loading="logsLoading"
        :pagination="false"
        size="middle"
        row-key="id"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.dataIndex === 'action'">
            <a-tag :color="getActionColor(record.action)">{{ record.action }}</a-tag>
          </template>
          <template v-if="column.dataIndex === 'created_at'">
            {{ formatTime(record.created_at) }}
          </template>
        </template>
      </a-table>
    </a-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useUserStore } from '@/store/user'
import {
  AppstoreOutlined,
  UserOutlined,
  ThunderboltOutlined,
  TeamOutlined,
} from '@ant-design/icons-vue'
import { getAuditLogListApi, type AuditLogRecord } from '@/api/audit'
import dayjs from 'dayjs'

const userStore = useUserStore()

const currentTime = ref(dayjs().format('YYYY-MM-DD HH:mm:ss'))

const stats = ref({
  totalApps: 0,
  totalUsers: 0,
  todayOperations: 0,
  totalRoles: 0,
})

const recentLogs = ref<AuditLogRecord[]>([])
const logsLoading = ref(false)

const auditColumns = [
  { title: '用户', dataIndex: 'username', width: 120 },
  { title: '操作', dataIndex: 'action', width: 120 },
  { title: '资源', dataIndex: 'resource', width: 150 },
  { title: '详情', dataIndex: 'detail', ellipsis: true },
  { title: 'IP', dataIndex: 'ip', width: 140 },
  { title: '时间', dataIndex: 'created_at', width: 180 },
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
  return dayjs(time).format('YYYY-MM-DD HH:mm:ss')
}

async function fetchRecentLogs() {
  logsLoading.value = true
  try {
    const res = await getAuditLogListApi({ page: 1, page_size: 10 })
    recentLogs.value = res.data.list || []
  } catch {
    // Silently handle error
  } finally {
    logsLoading.value = false
  }
}

onMounted(() => {
  fetchRecentLogs()
  // Update time every second
  setInterval(() => {
    currentTime.value = dayjs().format('YYYY-MM-DD HH:mm:ss')
  }, 1000)
})
</script>

<style scoped>
.dashboard-page {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.welcome-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  border-radius: 8px;
}

.welcome-card :deep(.ant-card-body) {
  padding: 24px 32px;
}

.welcome-title {
  color: #fff;
  font-size: 22px;
  margin: 0 0 8px;
}

.welcome-desc {
  color: rgba(255, 255, 255, 0.85);
  font-size: 14px;
  margin: 0;
}

.welcome-time {
  text-align: right;
  color: rgba(255, 255, 255, 0.85);
  font-size: 14px;
}

.stat-row {
  margin-top: 0;
}

.stat-card {
  border-radius: 8px;
}

.audit-card {
  border-radius: 8px;
}
</style>
