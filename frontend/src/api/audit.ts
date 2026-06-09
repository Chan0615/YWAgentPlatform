import request from './request'

export interface AuditLogRecord {
  id: number
  user_id: number | null
  username: string | null
  action: string
  resource_type: string | null
  resource_id: string | null
  detail: string | null
  ip_address: string | null
  user_agent: string | null
  status: string
  created_at: string
}

export interface AuditLogParams {
  page?: number
  page_size?: number
  username?: string
  action?: string
  resource_type?: string
  status?: string
  start_date?: string
  end_date?: string
}

export interface AuditLogListResult {
  total: number
  page: number
  page_size: number
  items: AuditLogRecord[]
}

export function getAuditLogListApi(params: AuditLogParams) {
  return request.get<unknown, AuditLogListResult>('/audit-logs', { params })
}
