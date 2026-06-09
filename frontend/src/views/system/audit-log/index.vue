<template>
  <div class="audit-log-page">
    <a-card :bordered="false">
      <!-- Filters -->
      <div class="filter-bar">
        <a-form layout="inline" :model="searchParams">
          <a-form-item label="用户">
            <a-input
              v-model:value="searchParams.username"
              placeholder="用户名"
              allow-clear
              style="width: 150px"
            />
          </a-form-item>
          <a-form-item label="操作类型">
            <a-select
              v-model:value="searchParams.action"
              placeholder="全部"
              allow-clear
              style="width: 140px"
            >
              <a-select-option value="CREATE">创建</a-select-option>
              <a-select-option value="UPDATE">更新</a-select-option>
              <a-select-option value="DELETE">删除</a-select-option>
              <a-select-option value="LOGIN">登录</a-select-option>
              <a-select-option value="LOGOUT">登出</a-select-option>
              <a-select-option value="EXPORT">导出</a-select-option>
            </a-select>
          </a-form-item>
          <a-form-item label="资源">
            <a-input
              v-model:value="searchParams.resource"
              placeholder="资源类型"
              allow-clear
              style="width: 150px"
            />
          </a-form-item>
          <a-form-item label="时间范围">
            <a-range-picker
              v-model:value="dateRange"
              :show-time="{ format: 'HH:mm' }"
              format="YYYY-MM-DD HH:mm"
              value-format="YYYY-MM-DD HH:mm:ss"
              @change="onDateChange"
            />
          </a-form-item>
          <a-form-item>
            <a-space>
              <a-button type="primary" @click="handleSearch">
                <template #icon><SearchOutlined /></template>
                查询
              </a-button>
              <a-button @click="handleReset">重置</a-button>
            </a-space>
          </a-form-item>
        </a-form>
      </div>

      <!-- Table -->
      <a-table
        :columns="columns"
        :data-source="dataList"
        :loading="loading"
        :pagination="pagination"
        row-key="id"
        size="middle"
        :scroll="{ x: 1200 }"
        @change="handleTableChange"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.dataIndex === 'action'">
            <a-tag :color="getActionColor(record.action)">
              {{ record.action }}
            </a-tag>
          </template>
          <template v-if="column.dataIndex === 'detail'">
            <a-typography-paragraph
              :ellipsis="{ rows: 1, expandable: true }"
              :content="record.detail"
              style="margin-bottom: 0"
            />
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
import { ref, reactive, onMounted } from 'vue'
import { SearchOutlined } from '@ant-design/icons-vue'
import type { TablePaginationConfig } from 'ant-design-vue'
import type { Dayjs } from 'dayjs'
import dayjs from 'dayjs'
import { getAuditLogListApi, type AuditLogRecord } from '@/api/audit'

const loading = ref(false)
const dataList = ref<AuditLogRecord[]>([])
const dateRange = ref<[Dayjs, Dayjs] | null>(null)

const searchParams = reactive({
  username: '',
  action: undefined as string | undefined,
  resource: '',
  start_time: '',
  end_time: '',
})

const pagination = reactive({
  current: 1,
  pageSize: 20,
  total: 0,
  showSizeChanger: true,
  showQuickJumper: true,
  showTotal: (total: number) => `共 ${total} 条`,
})

const columns = [
  { title: '用户', dataIndex: 'username', width: 120 },
  { title: '操作', dataIndex: 'action', width: 100 },
  { title: '资源', dataIndex: 'resource', width: 120 },
  { title: '资源ID', dataIndex: 'resource_id', width: 100 },
  { title: '详情', dataIndex: 'detail', width: 300 },
  { title: 'IP地址', dataIndex: 'ip', width: 140 },
  { title: '时间', dataIndex: 'created_at', width: 180 },
]

function getActionColor(action: string): string {
  const map: Record<string, string> = {
    CREATE: 'green',
    UPDATE: 'blue',
    DELETE: 'red',
    LOGIN: 'purple',
    LOGOUT: 'orange',
    EXPORT: 'cyan',
  }
  return map[action?.toUpperCase()] || 'default'
}

function formatTime(time: string): string {
  return dayjs(time).format('YYYY-MM-DD HH:mm:ss')
}

function onDateChange(dates: [Dayjs, Dayjs] | null) {
  if (dates) {
    searchParams.start_time = dates[0].format('YYYY-MM-DD HH:mm:ss')
    searchParams.end_time = dates[1].format('YYYY-MM-DD HH:mm:ss')
  } else {
    searchParams.start_time = ''
    searchParams.end_time = ''
  }
}

async function fetchData() {
  loading.value = true
  try {
    const params = {
      page: pagination.current,
      page_size: pagination.pageSize,
      username: searchParams.username || undefined,
      action: searchParams.action || undefined,
      resource: searchParams.resource || undefined,
      start_time: searchParams.start_time || undefined,
      end_time: searchParams.end_time || undefined,
    }
    const res = await getAuditLogListApi(params)
    dataList.value = res.items || []
    pagination.total = res.total
  } finally {
    loading.value = false
  }
}

function handleSearch() {
  pagination.current = 1
  fetchData()
}

function handleReset() {
  searchParams.username = ''
  searchParams.action = undefined
  searchParams.resource = ''
  searchParams.start_time = ''
  searchParams.end_time = ''
  dateRange.value = null
  pagination.current = 1
  fetchData()
}

function handleTableChange(pag: TablePaginationConfig) {
  pagination.current = pag.current || 1
  pagination.pageSize = pag.pageSize || 20
  fetchData()
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.audit-log-page {
  background: #fff;
  border-radius: 8px;
}

.filter-bar {
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid #f0f0f0;
}
</style>
