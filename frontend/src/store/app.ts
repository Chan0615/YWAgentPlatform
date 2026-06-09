import { defineStore } from 'pinia'
import { ref } from 'vue'
import { getVisibleApplicationListApi } from '@/api/application'

export interface AppInfo {
  id: number
  name: string
  code: string
  icon: string | null
  description: string | null
  url: string
  status: number
  permission?: string
  sort_order: number
}

export const useAppStore = defineStore('app', () => {
  const collapsed = ref(false)
  const applications = ref<AppInfo[]>([])

  function toggleCollapsed() {
    collapsed.value = !collapsed.value
  }

  function setCollapsed(value: boolean) {
    collapsed.value = value
  }

  async function fetchApplications() {
    const res = await getVisibleApplicationListApi()
    applications.value = (res || []).map((app) => ({
      ...app,
      permission: `app:${app.code}`,
    }))
    return applications.value
  }

  return {
    collapsed,
    applications,
    toggleCollapsed,
    setCollapsed,
    fetchApplications,
  }
})
