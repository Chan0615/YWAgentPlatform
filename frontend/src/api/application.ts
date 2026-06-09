import request from './request'

export interface ApplicationRecord {
  id: number
  name: string
  code: string
  icon: string
  description: string
  url: string
  status: number
  permission: string
  sort: number
  created_at: string
}

export interface ApplicationListParams {
  page?: number
  page_size?: number
  keyword?: string
  status?: number
}

export interface CreateApplicationParams {
  name: string
  code: string
  icon: string
  description: string
  url: string
  permission: string
  sort: number
  status: number
}

export interface UpdateApplicationParams {
  id: number
  name?: string
  code?: string
  icon?: string
  description?: string
  url?: string
  permission?: string
  sort?: number
  status?: number
}

export function getApplicationListApi(params?: ApplicationListParams) {
  return request.get<unknown, { data: { list: ApplicationRecord[]; total: number } }>('/applications', { params })
}

export function getApplicationDetailApi(id: number) {
  return request.get<unknown, { data: ApplicationRecord }>(`/applications/${id}`)
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
