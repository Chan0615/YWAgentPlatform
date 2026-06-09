<template>
  <div class="user-management-page">
    <a-card :bordered="false">
      <!-- Search & Actions -->
      <div class="table-toolbar">
        <div class="toolbar-left">
          <a-input-search
            v-model:value="searchParams.keyword"
            placeholder="搜索用户名/昵称/邮箱"
            style="width: 280px"
            allow-clear
            @search="handleSearch"
          />
          <a-select
            v-model:value="searchParams.status"
            placeholder="状态"
            style="width: 120px"
            allow-clear
            @change="handleSearch"
          >
            <a-select-option :value="1">启用</a-select-option>
            <a-select-option :value="0">禁用</a-select-option>
          </a-select>
        </div>
        <div class="toolbar-right">
          <a-button
            v-permission="'btn:user:create'"
            type="primary"
            @click="handleCreate"
          >
            <template #icon><PlusOutlined /></template>
            新增用户
          </a-button>
        </div>
      </div>

      <!-- Table -->
      <a-table
        :columns="columns"
        :data-source="dataList"
        :loading="loading"
        :pagination="pagination"
        row-key="id"
        @change="handleTableChange"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.dataIndex === 'roles'">
            <a-tag v-for="role in record.roles" :key="role" color="blue">
              {{ role }}
            </a-tag>
          </template>
          <template v-if="column.dataIndex === 'status'">
            <a-badge
              :status="record.status === 1 ? 'success' : 'error'"
              :text="record.status === 1 ? '启用' : '禁用'"
            />
          </template>
          <template v-if="column.dataIndex === 'actions'">
            <a-space>
              <a-button
                v-permission="'btn:user:edit'"
                type="link"
                size="small"
                @click="handleEdit(record)"
              >
                编辑
              </a-button>
              <a-button
                v-permission="'btn:user:reset-pwd'"
                type="link"
                size="small"
                @click="handleResetPwd(record)"
              >
                重置密码
              </a-button>
              <a-popconfirm
                title="确定删除此用户？"
                @confirm="handleDelete(record.id)"
              >
                <a-button
                  v-permission="'btn:user:delete'"
                  type="link"
                  size="small"
                  danger
                >
                  删除
                </a-button>
              </a-popconfirm>
            </a-space>
          </template>
        </template>
      </a-table>
    </a-card>

    <!-- Create/Edit Modal -->
    <a-modal
      v-model:open="modalVisible"
      :title="isEdit ? '编辑用户' : '新增用户'"
      :confirm-loading="submitLoading"
      @ok="handleSubmit"
      @cancel="resetForm"
    >
      <a-form
        ref="formRef"
        :model="formState"
        :rules="formRules"
        layout="vertical"
      >
        <a-form-item label="用户名" name="username">
          <a-input
            v-model:value="formState.username"
            :disabled="isEdit"
            placeholder="请输入用户名"
          />
        </a-form-item>
        <a-form-item v-if="!isEdit" label="密码" name="password">
          <a-input-password
            v-model:value="formState.password"
            placeholder="请输入密码"
          />
        </a-form-item>
        <a-form-item label="昵称" name="nickname">
          <a-input v-model:value="formState.nickname" placeholder="请输入昵称" />
        </a-form-item>
        <a-form-item label="邮箱" name="email">
          <a-input v-model:value="formState.email" placeholder="请输入邮箱" />
        </a-form-item>
        <a-form-item label="手机号" name="phone">
          <a-input v-model:value="formState.phone" placeholder="请输入手机号" />
        </a-form-item>
        <a-form-item label="角色" name="roles">
          <a-select
            v-model:value="formState.roles"
            mode="multiple"
            placeholder="请选择角色"
            :options="roleOptions"
          />
        </a-form-item>
        <a-form-item label="状态" name="status">
          <a-radio-group v-model:value="formState.status">
            <a-radio :value="1">启用</a-radio>
            <a-radio :value="0">禁用</a-radio>
          </a-radio-group>
        </a-form-item>
      </a-form>
    </a-modal>

    <!-- Reset Password Modal -->
    <a-modal
      v-model:open="resetPwdVisible"
      title="重置密码"
      :confirm-loading="submitLoading"
      @ok="handleResetPwdSubmit"
    >
      <a-form layout="vertical">
        <a-form-item label="新密码">
          <a-input-password
            v-model:value="newPassword"
            placeholder="请输入新密码"
          />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { PlusOutlined } from '@ant-design/icons-vue'
import { message } from 'ant-design-vue'
import type { FormInstance, TablePaginationConfig } from 'ant-design-vue'
import type { Rule } from 'ant-design-vue/es/form'
import {
  getUserListApi,
  createUserApi,
  updateUserApi,
  deleteUserApi,
  resetPasswordApi,
  type UserRecord,
} from '@/api/user'
import { getRoleListApi } from '@/api/role'

const loading = ref(false)
const dataList = ref<UserRecord[]>([])
const formRef = ref<FormInstance>()
const modalVisible = ref(false)
const resetPwdVisible = ref(false)
const submitLoading = ref(false)
const isEdit = ref(false)
const newPassword = ref('')
const currentUserId = ref(0)

const searchParams = reactive({
  keyword: '',
  status: undefined as number | undefined,
})

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
  username: '',
  password: '',
  nickname: '',
  email: '',
  phone: '',
  roles: [] as number[],
  status: 1,
})

const formRules: Record<string, Rule[]> = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
  nickname: [{ required: true, message: '请输入昵称', trigger: 'blur' }],
  email: [{ type: 'email', message: '请输入正确的邮箱', trigger: 'blur' }],
}

const roleOptions = ref<{ label: string; value: number }[]>([])

const columns = [
  { title: '用户名', dataIndex: 'username', width: 120 },
  { title: '昵称', dataIndex: 'nickname', width: 120 },
  { title: '邮箱', dataIndex: 'email', width: 200 },
  { title: '手机号', dataIndex: 'phone', width: 140 },
  { title: '角色', dataIndex: 'roles', width: 200 },
  { title: '状态', dataIndex: 'status', width: 100 },
  { title: '操作', dataIndex: 'actions', width: 220, fixed: 'right' as const },
]

async function fetchData() {
  loading.value = true
  try {
    const res = await getUserListApi({
      page: pagination.current,
      page_size: pagination.pageSize,
      ...searchParams,
    })
    dataList.value = res.data.list || []
    pagination.total = res.data.total
  } finally {
    loading.value = false
  }
}

async function fetchRoles() {
  try {
    const res = await getRoleListApi({ page: 1, page_size: 100 })
    roleOptions.value = (res.data.list || []).map((r) => ({
      label: r.name,
      value: r.id,
    }))
  } catch {
    // ignore
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
    username: '',
    password: '',
    nickname: '',
    email: '',
    phone: '',
    roles: [],
    status: 1,
  })
  modalVisible.value = true
}

function handleEdit(record: UserRecord) {
  isEdit.value = true
  Object.assign(formState, {
    id: record.id,
    username: record.username,
    password: '',
    nickname: record.nickname,
    email: record.email,
    phone: record.phone,
    roles: [],
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
      await updateUserApi({
        id: formState.id,
        nickname: formState.nickname,
        email: formState.email,
        phone: formState.phone,
        roles: formState.roles,
        status: formState.status,
      })
      message.success('更新成功')
    } else {
      await createUserApi(formState)
      message.success('创建成功')
    }
    modalVisible.value = false
    fetchData()
  } finally {
    submitLoading.value = false
  }
}

function resetForm() {
  formRef.value?.resetFields()
}

function handleResetPwd(record: UserRecord) {
  currentUserId.value = record.id
  newPassword.value = ''
  resetPwdVisible.value = true
}

async function handleResetPwdSubmit() {
  if (!newPassword.value) {
    message.warning('请输入新密码')
    return
  }
  submitLoading.value = true
  try {
    await resetPasswordApi(currentUserId.value, newPassword.value)
    message.success('密码重置成功')
    resetPwdVisible.value = false
  } finally {
    submitLoading.value = false
  }
}

async function handleDelete(id: number) {
  await deleteUserApi(id)
  message.success('删除成功')
  fetchData()
}

onMounted(() => {
  fetchData()
  fetchRoles()
})
</script>

<style scoped>
.user-management-page {
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

.toolbar-left {
  display: flex;
  gap: 12px;
  align-items: center;
}

.toolbar-right {
  display: flex;
  gap: 8px;
}
</style>
