import request from './request'

export interface AuditLogRecord {
  id: number
  user_id: number
  username: string
  action: string
  resource: string
  resource_id: string
  detail: string
  ip: string
  user_agent: string
  created_at: string
}

export interface AuditLogParams {
  page?: number
  page_size?: number
  username?: string
  action?: string
  resource?: string
  start_time?: string
  end_time?: string
}

export function getAuditLogListApi(params: AuditLogParams) {
  return request.get<unknown, { data: { list: AuditLogRecord[]; total: number } }>('/audit-logs', { params })
}

export function getAuditLogDetailApi(id: number) {
  return request.get<unknown, { data: AuditLogRecord }>(`/audit-logs/${id}`)
}
