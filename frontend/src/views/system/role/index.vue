<template>
  <div class="role-management-page">
    <a-card :bordered="false">
      <!-- Toolbar -->
      <div class="table-toolbar">
        <div class="toolbar-left">
          <a-input-search
            v-model:value="searchKeyword"
            placeholder="搜索角色名称/编码"
            style="width: 280px"
            allow-clear
            @search="handleSearch"
          />
        </div>
        <div class="toolbar-right">
          <a-button
            v-permission="'btn:role:create'"
            type="primary"
            @click="handleCreate"
          >
            <template #icon><PlusOutlined /></template>
            新增角色
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
          <template v-if="column.dataIndex === 'status'">
            <a-badge
              :status="record.status === 1 ? 'success' : 'error'"
              :text="record.status === 1 ? '启用' : '禁用'"
            />
          </template>
          <template v-if="column.dataIndex === 'actions'">
            <a-space>
              <a-button
                v-permission="'btn:role:edit'"
                type="link"
                size="small"
                @click="handleEdit(record)"
              >
                编辑
              </a-button>
              <a-button
                v-permission="'btn:role:assign'"
                type="link"
                size="small"
                @click="handleAssignPermissions(record)"
              >
                分配权限
              </a-button>
              <a-popconfirm
                title="确定删除此角色？"
                @confirm="handleDelete(record.id)"
              >
                <a-button
                  v-permission="'btn:role:delete'"
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
      :title="isEdit ? '编辑角色' : '新增角色'"
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
        <a-form-item label="角色名称" name="name">
          <a-input v-model:value="formState.name" placeholder="请输入角色名称" />
        </a-form-item>
        <a-form-item label="角色编码" name="code">
          <a-input
            v-model:value="formState.code"
            :disabled="isEdit"
            placeholder="请输入角色编码 (如: admin)"
          />
        </a-form-item>
        <a-form-item label="描述" name="description">
          <a-textarea
            v-model:value="formState.description"
            placeholder="请输入角色描述"
            :rows="3"
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

    <!-- Assign Permissions Drawer -->
    <a-drawer
      v-model:open="permDrawerVisible"
      title="分配权限"
      :width="480"
      @close="permDrawerVisible = false"
    >
      <a-spin :spinning="permLoading">
        <a-tree
          v-model:checkedKeys="checkedPermKeys"
          :tree-data="permissionTree"
          checkable
          :field-names="{ title: 'name', key: 'id', children: 'children' }"
          default-expand-all
        />
      </a-spin>
      <div class="drawer-footer">
        <a-button style="margin-right: 8px" @click="permDrawerVisible = false">
          取消
        </a-button>
        <a-button
          type="primary"
          :loading="permSubmitLoading"
          @click="handlePermSubmit"
        >
          保存
        </a-button>
      </div>
    </a-drawer>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { PlusOutlined } from '@ant-design/icons-vue'
import { message } from 'ant-design-vue'
import type { FormInstance, TablePaginationConfig } from 'ant-design-vue'
import type { Rule } from 'ant-design-vue/es/form'
import {
  getRoleListApi,
  createRoleApi,
  updateRoleApi,
  deleteRoleApi,
  assignPermissionsApi,
  type RoleRecord,
} from '@/api/role'
import { getPermissionTreeApi, type PermissionRecord } from '@/api/permission'

const loading = ref(false)
const dataList = ref<RoleRecord[]>([])
const formRef = ref<FormInstance>()
const modalVisible = ref(false)
const submitLoading = ref(false)
const isEdit = ref(false)
const searchKeyword = ref('')

// Permission assignment
const permDrawerVisible = ref(false)
const permLoading = ref(false)
const permSubmitLoading = ref(false)
const permissionTree = ref<PermissionRecord[]>([])
const checkedPermKeys = ref<number[]>([])
const currentRoleId = ref(0)

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
  status: 1,
})

const formRules: Record<string, Rule[]> = {
  name: [{ required: true, message: '请输入角色名称', trigger: 'blur' }],
  code: [{ required: true, message: '请输入角色编码', trigger: 'blur' }],
}

const columns = [
  { title: '角色名称', dataIndex: 'name', width: 150 },
  { title: '角色编码', dataIndex: 'code', width: 150 },
  { title: '描述', dataIndex: 'description', ellipsis: true },
  { title: '状态', dataIndex: 'status', width: 100 },
  { title: '创建时间', dataIndex: 'created_at', width: 180 },
  { title: '操作', dataIndex: 'actions', width: 240, fixed: 'right' as const },
]

async function fetchData() {
  loading.value = true
  try {
    const res = await getRoleListApi({
      page: pagination.current,
      page_size: pagination.pageSize,
      keyword: searchKeyword.value || undefined,
    })
    dataList.value = res.data.list || []
    pagination.total = res.data.total
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
  Object.assign(formState, { id: 0, name: '', code: '', description: '', status: 1 })
  modalVisible.value = true
}

function handleEdit(record: RoleRecord) {
  isEdit.value = true
  Object.assign(formState, {
    id: record.id,
    name: record.name,
    code: record.code,
    description: record.description,
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
      await updateRoleApi(formState)
      message.success('更新成功')
    } else {
      await createRoleApi({ ...formState, permissions: [] })
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

async function handleAssignPermissions(record: RoleRecord) {
  currentRoleId.value = record.id
  checkedPermKeys.value = record.permissions || []
  permDrawerVisible.value = true
  await fetchPermissionTree()
}

async function fetchPermissionTree() {
  permLoading.value = true
  try {
    const res = await getPermissionTreeApi()
    permissionTree.value = res.data.list || []
  } finally {
    permLoading.value = false
  }
}

async function handlePermSubmit() {
  permSubmitLoading.value = true
  try {
    await assignPermissionsApi(currentRoleId.value, checkedPermKeys.value)
    message.success('权限分配成功')
    permDrawerVisible.value = false
    fetchData()
  } finally {
    permSubmitLoading.value = false
  }
}

async function handleDelete(id: number) {
  await deleteRoleApi(id)
  message.success('删除成功')
  fetchData()
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.role-management-page {
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

.drawer-footer {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 16px 24px;
  border-top: 1px solid #f0f0f0;
  background: #fff;
  text-align: right;
}
</style>
