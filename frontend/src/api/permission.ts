import request from './request'

export interface PermissionRecord {
  id: number
  name: string
  code: string
  type: 'menu' | 'button' | 'api'
  parent_id: number
  path: string
  icon: string
  sort: number
  status: number
  children?: PermissionRecord[]
  created_at: string
}

export interface CreatePermissionParams {
  name: string
  code: string
  type: 'menu' | 'button' | 'api'
  parent_id: number
  path?: string
  icon?: string
  sort?: number
  status: number
}

export interface UpdatePermissionParams {
  id: number
  name?: string
  code?: string
  type?: 'menu' | 'button' | 'api'
  parent_id?: number
  path?: string
  icon?: string
  sort?: number
  status?: number
}

export function getPermissionTreeApi() {
  return request.get<unknown, { data: { list: PermissionRecord[] } }>('/permissions/tree')
}

export function getPermissionListApi() {
  return request.get<unknown, { data: { list: PermissionRecord[] } }>('/permissions')
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
