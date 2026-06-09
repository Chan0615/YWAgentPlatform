<template>
  <div class="application-management-page">
    <a-card :bordered="false">
      <div class="table-toolbar">
        <div class="toolbar-left">
          <a-input-search
            v-model:value="searchName"
            placeholder="搜索应用名称"
            style="width: 280px"
            allow-clear
            @search="handleSearch"
          />
        </div>
        <div class="toolbar-right">
          <a-button v-permission="'btn:application:create'" type="primary" @click="handleCreate">
            <template #icon><PlusOutlined /></template>
            新增应用
          </a-button>
        </div>
      </div>

      <a-table
        :columns="columns"
        :data-source="dataList"
        :loading="loading"
        :pagination="pagination"
        row-key="id"
        @change="handleTableChange"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.dataIndex === 'status'">
            <a-badge :status="record.status === 1 ? 'success' : 'error'" :text="record.status === 1 ? '启用' : '停用'" />
          </template>
          <template v-if="column.dataIndex === 'url'">
            <a-typography-paragraph :content="record.url" :ellipsis="{ rows: 1 }" style="margin-bottom: 0" />
          </template>
          <template v-if="column.dataIndex === 'actions'">
            <a-space>
              <a-button v-permission="'btn:application:edit'" type="link" size="small" @click="handleEdit(record)">编辑</a-button>
              <a-button
                v-permission="'btn:application:edit'"
                type="link"
                size="small"
                @click="handleToggleStatus(record)"
              >
                {{ record.status === 1 ? '停用' : '启用' }}
              </a-button>
              <a-popconfirm title="确定删除此应用？" @confirm="handleDelete(record.id)">
                <a-button v-permission="'btn:application:delete'" type="link" size="small" danger>删除</a-button>
              </a-popconfirm>
            </a-space>
          </template>
        </template>
      </a-table>
    </a-card>

    <a-modal
      v-model:open="modalVisible"
      :title="isEdit ? '编辑应用' : '新增应用'"
      :confirm-loading="submitLoading"
      width="560px"
      @ok="handleSubmit"
      @cancel="resetForm"
    >
      <a-form ref="formRef" :model="formState" :rules="formRules" layout="vertical">
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="应用名称" name="name">
              <a-input v-model:value="formState.name" placeholder="请输入应用名称" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="应用编码" name="code">
              <a-input v-model:value="formState.code" :disabled="isEdit" placeholder="如: opsflow" />
            </a-form-item>
          </a-col>
        </a-row>

        <a-form-item label="访问地址" name="url">
          <a-input v-model:value="formState.url" placeholder="推荐填写 /app/应用编码/，如 /app/opsflow/" />
          <div class="form-help-text">
            推荐通过 Nginx 反向代理后填写相对路径，如 <code>/app/opsflow/</code>。
            若直接填写完整地址，可能会涉及跨域和登录态传递问题。
          </div>
        </a-form-item>

        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="图标" name="icon">
              <a-select v-model:value="formState.icon" placeholder="请选择图标">
                <a-select-option v-for="item in iconOptions" :key="item.value" :value="item.value">
                  {{ item.label }}
                </a-select-option>
              </a-select>
              <div class="form-help-text">
                先使用平台内置图标，后续如需支持自定义上传图标可再扩展。
              </div>
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="排序" name="sort_order">
              <a-input-number v-model:value="formState.sort_order" :min="0" style="width: 100%" />
            </a-form-item>
          </a-col>
        </a-row>

        <a-form-item label="描述" name="description">
          <a-textarea v-model:value="formState.description" placeholder="请输入应用描述" :rows="3" />
        </a-form-item>

        <a-alert
          type="info"
          show-icon
          class="access-guide"
          message="子应用接入说明"
          description="应用代码需要单独部署在服务器其他目录并运行于独立端口，再由 YWAgentPlatform 的 Nginx 统一反向代理到 /app/xxx/。新增应用时，这里填写的是代理后的访问路径，不是代码存放路径。"
        />

        <a-form-item label="状态" name="status">
          <a-radio-group v-model:value="formState.status">
            <a-radio :value="1">启用</a-radio>
            <a-radio :value="0">停用</a-radio>
          </a-radio-group>
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { PlusOutlined } from '@ant-design/icons-vue'
import { message } from 'ant-design-vue'
import type { FormInstance, TablePaginationConfig } from 'ant-design-vue'
import type { Rule } from 'ant-design-vue/es/form'
import {
  createApplicationApi,
  deleteApplicationApi,
  getApplicationListApi,
  updateApplicationApi,
  type ApplicationRecord,
} from '@/api/application'

const loading = ref(false)
const submitLoading = ref(false)
const modalVisible = ref(false)
const isEdit = ref(false)
const formRef = ref<FormInstance>()
const dataList = ref<ApplicationRecord[]>([])
const searchName = ref('')
const iconOptions = [
  { label: '应用商店', value: 'AppstoreOutlined' },
  { label: '云服务器', value: 'CloudServerOutlined' },
  { label: '机器人', value: 'RobotOutlined' },
  { label: '数据库', value: 'DatabaseOutlined' },
  { label: '工单表单', value: 'ProfileOutlined' },
  { label: '搜索审计', value: 'FileSearchOutlined' },
  { label: '设置', value: 'SettingOutlined' },
  { label: '监控图表', value: 'AreaChartOutlined' },
]

const pagination = reactive({
  current: 1,
  pageSize: 10,
  total: 0,
  showSizeChanger: true,
  showQuickJumper: true,
  showTotal: (total: number) => `共 ${total} 条`,
})

const formState = reactive({
  id: 0,
  name: '',
  code: '',
  description: '',
  url: '',
  icon: 'AppstoreOutlined',
  sort_order: 0,
  status: 1,
})

const formRules: Record<string, Rule[]> = {
  name: [{ required: true, message: '请输入应用名称', trigger: 'blur' }],
  code: [{ required: true, message: '请输入应用编码', trigger: 'blur' }],
  url: [{ required: true, message: '请输入访问地址', trigger: 'blur' }],
}

const columns = [
  { title: '应用名称', dataIndex: 'name', width: 160 },
  { title: '应用编码', dataIndex: 'code', width: 140 },
  { title: '访问地址', dataIndex: 'url', ellipsis: true },
  { title: '图标', dataIndex: 'icon', width: 160 },
  { title: '排序', dataIndex: 'sort_order', width: 90 },
  { title: '状态', dataIndex: 'status', width: 100 },
  { title: '操作', dataIndex: 'actions', width: 220, fixed: 'right' as const },
]

async function fetchData() {
  loading.value = true
  try {
    const res = await getApplicationListApi({
      page: pagination.current,
      page_size: pagination.pageSize,
      name: searchName.value || undefined,
    } as any)
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

function handleTableChange(pag: TablePaginationConfig) {
  pagination.current = pag.current || 1
  pagination.pageSize = pag.pageSize || 10
  fetchData()
}

function handleCreate() {
  isEdit.value = false
  Object.assign(formState, {
    id: 0,
    name: '',
    code: '',
    description: '',
    url: '',
    icon: 'AppstoreOutlined',
    sort_order: 0,
    status: 1,
  })
  modalVisible.value = true
}

function handleEdit(record: ApplicationRecord) {
  isEdit.value = true
  Object.assign(formState, {
    id: record.id,
    name: record.name,
    code: record.code,
    description: record.description || '',
    url: record.url,
    icon: record.icon || 'AppstoreOutlined',
    sort_order: record.sort_order,
    status: record.status,
  })
  modalVisible.value = true
}

async function handleSubmit() {
  try {
    await formRef.value?.validateFields()
  } catch {
    return
  }

  submitLoading.value = true
  try {
    if (isEdit.value) {
      await updateApplicationApi({ ...formState })
      message.success('更新成功')
    } else {
      await createApplicationApi({ ...formState })
      message.success('创建成功')
    }
    modalVisible.value = false
    fetchData()
  } finally {
    submitLoading.value = false
  }
}

async function handleToggleStatus(record: ApplicationRecord) {
  await updateApplicationApi({ id: record.id, status: record.status === 1 ? 0 : 1 })
  message.success(record.status === 1 ? '应用已停用' : '应用已启用')
  fetchData()
}

async function handleDelete(id: number) {
  await deleteApplicationApi(id)
  message.success('删除成功')
  fetchData()
}

function resetForm() {
  formRef.value?.resetFields()
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.application-management-page {
  background: #fff;
  border-radius: 8px;
}

.table-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  flex-wrap: wrap;
  gap: 12px;
}

.toolbar-left,
.toolbar-right {
  display: flex;
  gap: 12px;
  align-items: center;
}

.form-help-text {
  margin-top: 6px;
  color: #8c8c8c;
  font-size: 12px;
  line-height: 1.5;
}

.form-help-text code {
  background: #fff7e6;
  color: #d46b08;
  padding: 2px 6px;
  border-radius: 4px;
}

.access-guide {
  margin-bottom: 16px;
}
</style>
