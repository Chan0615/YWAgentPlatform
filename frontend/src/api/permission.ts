import request from './request'

export interface PermissionRecord {
  id: number
  name: string
  code: string
  type: 'app' | 'menu' | 'button'
  parent_id: number | null
  path: string | null
  icon: string | null
  sort_order: number
  status: number
  children?: PermissionRecord[]
  created_at: string
}

export interface CreatePermissionParams {
  name: string
  code: string
  type: 'app' | 'menu' | 'button'
  parent_id?: number | null
  path?: string
  icon?: string
  sort_order?: number
  status: number
}

export interface UpdatePermissionParams {
  id: number
  name?: string
  code?: string
  type?: 'app' | 'menu' | 'button'
  parent_id?: number | null
  path?: string
  icon?: string
  sort_order?: number
  status?: number
}

export function getPermissionTreeApi() {
  return request.get<unknown, PermissionRecord[]>('/permissions/tree')
}

export function getPermissionListApi() {
  return request.get<unknown, PermissionRecord[]>('/permissions')
}

export function createPermissionApi(data: CreatePermissionParams) {
  return request.post('/permissions', data)
}

export function updatePermissionApi(data: UpdatePermissionParams) {
  return request.put(`/permissions/${data.id}`, data)
}

export function deletePermissionApi(id: number) {
  return request.delete(`/permissions/${id}`)
}
