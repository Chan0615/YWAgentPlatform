import request from './request'

export interface RoleRecord {
  id: number
  name: string
  code: string
  description: string
  permissions: number[]
  status: number
  created_at: string
}

export interface RoleListParams {
  page?: number
  page_size?: number
  keyword?: string
}

export interface CreateRoleParams {
  name: string
  code: string
  description: string
  permissions: number[]
  status: number
}

export interface UpdateRoleParams {
  id: number
  name?: string
  code?: string
  description?: string
  permissions?: number[]
  status?: number
}

export function getRoleListApi(params?: RoleListParams) {
  return request.get<unknown, { data: { list: RoleRecord[]; total: number } }>('/roles', { params })
}

export function getRoleDetailApi(id: number) {
  return request.get<unknown, { data: RoleRecord }>(`/roles/${id}`)
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
  return request.put(`/roles/${roleId}/permissions`, { permission_ids: permissionIds })
}
