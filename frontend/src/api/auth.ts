import request from './request'

export interface LoginParams {
  username: string
  password: string
}

export interface LoginResult {
  token: string
  expires_at: string
}

export interface UserInfoResult {
  user: {
    id: number
    username: string
    nickname: string
    email: string
    phone: string
    avatar: string
    status: number
  }
  permissions: string[]
  roles: string[]
}

export function loginApi(data: LoginParams) {
  return request.post<unknown, { data: LoginResult }>('/auth/login', data)
}

export function logoutApi() {
  return request.post('/auth/logout')
}

export function refreshTokenApi() {
  return request.post<unknown, { data: LoginResult }>('/auth/refresh-token')
}

export function getUserInfoApi() {
  return request.get<unknown, { data: UserInfoResult }>('/auth/user-info')
}
