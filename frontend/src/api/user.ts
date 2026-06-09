import request from './request'

export interface UserRecord {
  id: number
  username: string
  nickname: string
  email: string
  phone: string
  roles: Array<{ id: number; name: string; code: string }>
  status: number
  created_at: string
  updated_at: string
}

export interface UserListParams {
  page?: number
  page_size?: number
  keyword?: string
  status?: number
}

export interface CreateUserParams {
  username: string
  nickname: string
  password: string
  email: string
  phone: string
  role_ids: number[]
  status: number
}

export interface UpdateUserParams {
  id: number
  nickname?: string
  email?: string
  phone?: string
  password?: string
  role_ids?: number[]
  status?: number
}

export interface UserListResult {
  total: number
  page: number
  page_size: number
  items: UserRecord[]
}

export function getUserListApi(params: UserListParams) {
  return request.get<unknown, UserListResult>('/users', { params })
}

export function getUserDetailApi(id: number) {
  return request.get<unknown, UserRecord>(`/users/${id}`)
}

export function createUserApi(data: CreateUserParams) {
  return request.post('/users', data)
}

export function updateUserApi(data: UpdateUserParams) {
  return request.put(`/users/${data.id}`, data)
}

export function deleteUserApi(id: number) {
  return request.delete(`/users/${id}`)
}

export function resetPasswordApi(id: number, password: string) {
  return request.put(`/users/${id}`, { password })
}
