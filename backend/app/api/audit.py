from typing import Optional
from datetime import datetime, date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import get_db
from app.models.audit_log import AuditLog
from app.models.user import User
from app.schemas.audit import AuditLogResponse, AuditLogListResponse
from app.api.deps import require_permissions

router = APIRouter(prefix="/audit-logs", tags=["Audit Logs"])


@router.get("", response_model=AuditLogListResponse)
async def list_audit_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    username: Optional[str] = Query(None),
    action: Optional[str] = Query(None),
    resource_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    current_user: User = Depends(require_permissions("menu:audit")),
    db: AsyncSession = Depends(get_db),
):
    """List audit logs with filters and pagination. Admin only."""
    query = select(AuditLog)
    count_query = select(func.count(AuditLog.id))

    # Apply filters
    if username:
        query = query.where(AuditLog.username.contains(username))
        count_query = count_query.where(AuditLog.username.contains(username))
    if action:
        query = query.where(AuditLog.action == action)
        count_query = count_query.where(AuditLog.action == action)
    if resource_type:
        query = query.where(AuditLog.resource_type == resource_type)
        count_query = count_query.where(AuditLog.resource_type == resource_type)
    if status:
        query = query.where(AuditLog.status == status)
        count_query = count_query.where(AuditLog.status == status)
    if start_date:
        query = query.where(AuditLog.created_at >= datetime.combine(start_date, datetime.min.time()))
        count_query = count_query.where(AuditLog.created_at >= datetime.combine(start_date, datetime.min.time()))
    if end_date:
        query = query.where(AuditLog.created_at <= datetime.combine(end_date, datetime.max.time()))
        count_query = count_query.where(AuditLog.created_at <= datetime.combine(end_date, datetime.max.time()))

    total_result = await db.execute(count_query)
    total = total_result.scalar()

    query = query.order_by(AuditLog.id.desc()).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    logs = result.scalars().all()

    return AuditLogListResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=[AuditLogResponse.model_validate(log) for log in logs],
    )
