import request from './request'

export interface RoleRecord {
  id: number
  name: string
  code: string
  description: string
  permissions: Array<{ id: number; name: string; code: string; type: string }>
  status: number
  created_at: string
  updated_at: string
}

export interface RoleListParams {
  page?: number
  page_size?: number
  name?: string
}

export interface CreateRoleParams {
  name: string
  code: string
  description: string
  status: number
}

export interface UpdateRoleParams {
  id: number
  name?: string
  code?: string
  description?: string
  status?: number
}

export interface RoleListResult {
  total: number
  page: number
  page_size: number
  items: RoleRecord[]
}

export function getRoleListApi(params?: RoleListParams) {
  return request.get<unknown, RoleListResult>('/roles', { params })
}

export function getRoleDetailApi(id: number) {
  return request.get<unknown, RoleRecord>(`/roles/${id}`)
}

export function createRoleApi(data: CreateRoleParams) {
  return request.post('/roles', data)
}

export function updateRoleApi(data: UpdateRoleParams) {
  return request.put(`/roles/${data.id}`, data)
}

export function deleteRoleApi(id: number) {
  return request.delete(`/roles/${id}`)
}

export function assignPermissionsApi(roleId: number, permissionIds: number[]) {
  return request.post(`/roles/${roleId}/permissions`, { permission_ids: permissionIds })
}
