<template>
  <div class="permission-management-page">
    <a-card :bordered="false">
      <!-- Toolbar -->
      <div class="table-toolbar">
        <div class="toolbar-left">
          <a-button @click="handleExpandAll">
            {{ expandAll ? '收起全部' : '展开全部' }}
          </a-button>
        </div>
        <div class="toolbar-right">
          <a-button
            v-permission="'btn:permission:create'"
            type="primary"
            @click="handleCreate()"
          >
            <template #icon><PlusOutlined /></template>
            新增权限
          </a-button>
        </div>
      </div>

      <!-- Tree Table -->
      <a-table
        :columns="columns"
        :data-source="treeData"
        :loading="loading"
        :pagination="false"
        :expanded-row-keys="expandedKeys"
        row-key="id"
        :indent-size="24"
        @expand="onExpand"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.dataIndex === 'name'">
            <span>
              <FolderOutlined v-if="record.type === 'menu'" style="margin-right: 6px; color: #1890ff;" />
              <ApiOutlined v-else-if="record.type === 'api'" style="margin-right: 6px; color: #52c41a;" />
              <LockOutlined v-else style="margin-right: 6px; color: #faad14;" />
              {{ record.name }}
            </span>
          </template>
          <template v-if="column.dataIndex === 'type'">
            <a-tag :color="getTypeColor(record.type)">
              {{ getTypeLabel(record.type) }}
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
                v-if="record.type === 'menu'"
                v-permission="'btn:permission:create'"
                type="link"
                size="small"
                @click="handleCreate(record.id)"
              >
                新增子级
              </a-button>
              <a-button
                v-permission="'btn:permission:edit'"
                type="link"
                size="small"
                @click="handleEdit(record)"
              >
                编辑
              </a-button>
              <a-popconfirm
                title="确定删除此权限及其子级？"
                @confirm="handleDelete(record.id)"
              >
                <a-button
                  v-permission="'btn:permission:delete'"
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
      :title="isEdit ? '编辑权限' : '新增权限'"
      :confirm-loading="submitLoading"
      width="560px"
      @ok="handleSubmit"
      @cancel="resetForm"
    >
      <a-form
        ref="formRef"
        :model="formState"
        :rules="formRules"
        layout="vertical"
      >
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="权限名称" name="name">
              <a-input v-model:value="formState.name" placeholder="请输入权限名称" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="权限编码" name="code">
              <a-input v-model:value="formState.code" placeholder="如: system:user:list" />
            </a-form-item>
          </a-col>
        </a-row>
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="类型" name="type">
              <a-select v-model:value="formState.type" placeholder="请选择类型">
                <a-select-option value="menu">菜单</a-select-option>
                <a-select-option value="button">按钮</a-select-option>
                <a-select-option value="api">接口</a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="上级权限" name="parent_id">
              <a-tree-select
                v-model:value="formState.parent_id"
                :tree-data="parentOptions"
                :field-names="{ label: 'name', value: 'id', children: 'children' }"
                placeholder="无 (顶级)"
                allow-clear
                tree-default-expand-all
              />
            </a-form-item>
          </a-col>
        </a-row>
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="路径" name="path">
              <a-input v-model:value="formState.path" placeholder="菜单路径" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="排序" name="sort">
              <a-input-number v-model:value="formState.sort" :min="0" style="width: 100%" />
            </a-form-item>
          </a-col>
        </a-row>
        <a-form-item label="状态" name="status">
          <a-radio-group v-model:value="formState.status">
            <a-radio :value="1">启用</a-radio>
            <a-radio :value="0">禁用</a-radio>
          </a-radio-group>
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { PlusOutlined, FolderOutlined, ApiOutlined, LockOutlined } from '@ant-design/icons-vue'
import { message } from 'ant-design-vue'
import type { FormInstance } from 'ant-design-vue'
import type { Rule } from 'ant-design-vue/es/form'
import {
  getPermissionTreeApi,
  createPermissionApi,
  updatePermissionApi,
  deletePermissionApi,
  type PermissionRecord,
} from '@/api/permission'

const loading = ref(false)
const treeData = ref<PermissionRecord[]>([])
const expandedKeys = ref<number[]>([])
const expandAll = ref(false)
const formRef = ref<FormInstance>()
const modalVisible = ref(false)
const submitLoading = ref(false)
const isEdit = ref(false)
const parentOptions = ref<PermissionRecord[]>([])

const formState = reactive({
  id: 0,
  name: '',
  code: '',
  type: 'menu' as 'menu' | 'button' | 'api',
  parent_id: 0,
  path: '',
  icon: '',
  sort: 0,
  status: 1,
})

const formRules: Record<string, Rule[]> = {
  name: [{ required: true, message: '请输入权限名称', trigger: 'blur' }],
  code: [{ required: true, message: '请输入权限编码', trigger: 'blur' }],
  type: [{ required: true, message: '请选择类型', trigger: 'change' }],
}

const columns = [
  { title: '权限名称', dataIndex: 'name', width: 250 },
  { title: '权限编码', dataIndex: 'code', width: 220 },
  { title: '类型', dataIndex: 'type', width: 100 },
  { title: '路径', dataIndex: 'path', width: 180 },
  { title: '排序', dataIndex: 'sort', width: 80 },
  { title: '状态', dataIndex: 'status', width: 100 },
  { title: '操作', dataIndex: 'actions', width: 240, fixed: 'right' as const },
]

function getTypeColor(type: string): string {
  const map: Record<string, string> = { menu: 'blue', button: 'orange', api: 'green' }
  return map[type] || 'default'
}

function getTypeLabel(type: string): string {
  const map: Record<string, string> = { menu: '菜单', button: '按钮', api: '接口' }
  return map[type] || type
}

function getAllKeys(data: PermissionRecord[]): number[] {
  const keys: number[] = []
  function traverse(items: PermissionRecord[]) {
    items.forEach((item) => {
      keys.push(item.id)
      if (item.children?.length) traverse(item.children)
    })
  }
  traverse(data)
  return keys
}

function handleExpandAll() {
  if (expandAll.value) {
    expandedKeys.value = []
  } else {
    expandedKeys.value = getAllKeys(treeData.value)
  }
  expandAll.value = !expandAll.value
}

function onExpand(expanded: boolean, record: PermissionRecord) {
  if (expanded) {
    expandedKeys.value.push(record.id)
  } else {
    expandedKeys.value = expandedKeys.value.filter((k) => k !== record.id)
  }
}

async function fetchData() {
  loading.value = true
  try {
    const res = await getPermissionTreeApi()
    treeData.value = res.data.list || []
    parentOptions.value = treeData.value
  } finally {
    loading.value = false
  }
}

function handleCreate(parentId?: number) {
  isEdit.value = false
  Object.assign(formState, {
    id: 0,
    name: '',
    code: '',
    type: 'menu',
    parent_id: parentId || 0,
    path: '',
    icon: '',
    sort: 0,
    status: 1,
  })
  modalVisible.value = true
}

function handleEdit(record: PermissionRecord) {
  isEdit.value = true
  Object.assign(formState, {
    id: record.id,
    name: record.name,
    code: record.code,
    type: record.type,
    parent_id: record.parent_id,
    path: record.path,
    icon: record.icon,
    sort: record.sort,
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
      await updatePermissionApi(formState)
      message.success('更新成功')
    } else {
      await createPermissionApi(formState)
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

async function handleDelete(id: number) {
  await deletePermissionApi(id)
  message.success('删除成功')
  fetchData()
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.permission-management-page {
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
