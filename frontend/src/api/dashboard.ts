import request from './request'

export interface DashboardStats {
  totalApps: number
  totalUsers: number
  todayOperations: number
  totalRoles: number
}

export function getDashboardStatsApi() {
  return request.get<unknown, DashboardStats>('/dashboard/stats')
}
