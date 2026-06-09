import { defineStore } from 'pinia'
import { ref } from 'vue'
import { loginApi, logoutApi, getUserInfoApi } from '@/api/auth'
import { getToken, setToken, removeToken } from '@/utils/auth'

export interface UserInfo {
  id: number
  username: string
  nickname: string
  email: string
  phone: string
  avatar: string
  status: number
}

export const useUserStore = defineStore('user', () => {
  const token = ref<string>(getToken() || '')
  const userInfo = ref<UserInfo | null>(null)
  const permissions = ref<string[]>([])
  const roles = ref<string[]>([])

  async function login(username: string, password: string) {
    const res = await loginApi({ username, password })
    const accessToken = res.access_token
    token.value = accessToken
    setToken(accessToken)
    return res
  }

  async function logout() {
    try {
      await logoutApi()
    } finally {
      resetState()
    }
  }

  async function fetchUserInfo() {
    const res = await getUserInfoApi()
    userInfo.value = {
      id: res.id,
      username: res.username,
      nickname: res.nickname,
      email: res.email,
      phone: res.phone,
      avatar: res.avatar,
      status: res.status,
    }
    permissions.value = res.permissions || []
    roles.value = res.roles?.map((r: any) => r.code) || []
    return res
  }

  function resetState() {
    token.value = ''
    userInfo.value = null
    permissions.value = []
    roles.value = []
    removeToken()
  }

  function hasPermission(code: string): boolean {
    if (roles.value.includes('admin')) return true
    return permissions.value.includes(code)
  }

  return {
    token,
    userInfo,
    permissions,
    roles,
    login,
    logout,
    fetchUserInfo,
    resetState,
    hasPermission,
  }
})
