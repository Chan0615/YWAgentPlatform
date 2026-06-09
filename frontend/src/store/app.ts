import { defineStore } from 'pinia'
import { ref } from 'vue'
import { getApplicationListApi } from '@/api/application'

export interface AppInfo {
  id: number
  name: string
  code: string
  icon: string
  description: string
  url: string
  status: number
  permission: string
  sort: number
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
    const res = await getApplicationListApi()
    applications.value = res.data.list || []
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
