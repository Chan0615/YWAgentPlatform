from datetime import datetime, date

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import get_db
from app.models.application import Application
from app.models.user import User
from app.models.role import Role
from app.models.audit_log import AuditLog
from app.api.deps import get_current_user

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/stats")
async def get_dashboard_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get dashboard statistics."""
    # Total applications
    apps_result = await db.execute(select(func.count(Application.id)))
    total_apps = apps_result.scalar() or 0

    # Total users (no online tracking yet, use total as placeholder)
    users_result = await db.execute(select(func.count(User.id)))
    total_users = users_result.scalar() or 0

    # Total roles
    roles_result = await db.execute(select(func.count(Role.id)))
    total_roles = roles_result.scalar() or 0

    # Today's operations (audit logs created today)
    today_start = datetime.combine(date.today(), datetime.min.time())
    today_end = datetime.combine(date.today(), datetime.max.time())
    today_ops_result = await db.execute(
        select(func.count(AuditLog.id)).where(
            AuditLog.created_at >= today_start,
            AuditLog.created_at <= today_end,
        )
    )
    today_operations = today_ops_result.scalar() or 0

    return {
        "totalApps": total_apps,
        "totalUsers": total_users,
        "todayOperations": today_operations,
        "totalRoles": total_roles,
    }
