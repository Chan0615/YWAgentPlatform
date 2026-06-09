import request from './request'

export interface LoginParams {
  username: string
  password: string
}

export interface LoginResult {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
}

export interface UserInfoResult {
  id: number
  username: string
  nickname: string
  email: string
  phone: string
  avatar: string
  status: number
  roles: Array<{ id: number; name: string; code: string }>
  permissions: string[]
}

export function loginApi(data: LoginParams) {
  return request.post<unknown, LoginResult>('/auth/login', data)
}

export function logoutApi() {
  return request.post('/auth/logout')
}

export function refreshTokenApi(refresh_token: string) {
  return request.post<unknown, LoginResult>('/auth/refresh', { refresh_token })
}

export function getUserInfoApi() {
  return request.get<unknown, UserInfoResult>('/auth/userinfo')
}
