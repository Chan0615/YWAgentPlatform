import request from './request'

export interface ApplicationRecord {
  id: number
  name: string
  code: string
  icon: string | null
  description: string | null
  url: string
  status: number
  sort_order: number
  created_at: string
  updated_at?: string
  visible_role_ids?: number[]
}

export interface ApplicationListParams {
  page?: number
  page_size?: number
  name?: string
  status?: number
}

export interface CreateApplicationParams {
  name: string
  code: string
  icon?: string
  description?: string
  url: string
  sort_order: number
  status: number
}

export interface UpdateApplicationParams {
  id: number
  name?: string
  code?: string
  icon?: string
  description?: string
  url?: string
  sort_order?: number
  status?: number
}

export interface ApplicationListResult {
  total: number
  page: number
  page_size: number
  items: ApplicationRecord[]
}

export function getVisibleApplicationListApi() {
  return request.get<unknown, ApplicationRecord[]>('/applications/visible')
}

export function getApplicationListApi(params?: ApplicationListParams) {
  return request.get<unknown, ApplicationListResult>('/applications', { params })
}

export function getApplicationDetailApi(id: number) {
  return request.get<unknown, ApplicationRecord>(`/applications/${id}`)
}

export function createApplicationApi(data: CreateApplicationParams) {
  return request.post('/applications', data)
}

export function updateApplicationApi(data: UpdateApplicationParams) {
  return request.put(`/applications/${data.id}`, data)
}

export function deleteApplicationApi(id: number) {
  return request.delete(`/applications/${id}`)
}

export function assignApplicationVisibleRolesApi(appId: number, roleIds: number[]) {
  return request.post<ApplicationRecord>(`/applications/${appId}/visible-roles`, { role_ids: roleIds })
}
