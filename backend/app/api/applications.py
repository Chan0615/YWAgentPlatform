from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import get_db
from app.models.application import Application
from app.models.permission import Permission
from app.models.user import User
from app.schemas.application import (
    ApplicationCreate, ApplicationUpdate, ApplicationResponse, ApplicationListResponse,
)
from app.api.deps import get_current_user, require_permissions, get_user_permissions

router = APIRouter(prefix="/applications", tags=["Applications"])


@router.get("", response_model=ApplicationListResponse)
async def list_applications(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    name: Optional[str] = Query(None),
    current_user: User = Depends(require_permissions("menu:application")),
    db: AsyncSession = Depends(get_db),
):
    """List all applications with pagination (admin view)."""
    query = select(Application)
    count_query = select(func.count(Application.id))

    if name:
        query = query.where(Application.name.contains(name))
        count_query = count_query.where(Application.name.contains(name))

    total_result = await db.execute(count_query)
    total = total_result.scalar()

    query = query.order_by(Application.sort_order.asc()).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    apps = result.scalars().all()

    return ApplicationListResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=[ApplicationResponse.model_validate(a) for a in apps],
    )


@router.get("/visible", response_model=List[ApplicationResponse])
async def list_visible_applications(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List applications visible to the current user based on app-level permissions."""
    permissions = await get_user_permissions(current_user, db)

    # Extract app permission codes (format: app:<code>)
    app_codes = [
        code.split(":", 1)[1]
        for code in permissions
        if code.startswith("app:")
    ]

    # Admin gets all active apps
    user_role_codes = [role.code for role in current_user.roles]
    if "admin" in user_role_codes:
        result = await db.execute(
            select(Application)
            .where(Application.status == 1)
            .order_by(Application.sort_order.asc())
        )
    else:
        if not app_codes:
            return []
        result = await db.execute(
            select(Application)
            .where(Application.status == 1, Application.code.in_(app_codes))
            .order_by(Application.sort_order.asc())
        )

    apps = result.scalars().all()
    return [ApplicationResponse.model_validate(a) for a in apps]


@router.get("/{app_id}", response_model=ApplicationResponse)
async def get_application(
    app_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a single application by ID."""
    result = await db.execute(select(Application).where(Application.id == app_id))
    app = result.scalar_one_or_none()
    if not app:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")

    user_role_codes = [role.code for role in current_user.roles]
    if "admin" not in user_role_codes:
        permissions = await get_user_permissions(current_user, db)
        if f"app:{app.code}" not in permissions:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")

    return ApplicationResponse.model_validate(app)


@router.post("", response_model=ApplicationResponse, status_code=status.HTTP_201_CREATED)
async def create_application(
    app_in: ApplicationCreate,
    current_user: User = Depends(require_permissions("btn:application:create")),
    db: AsyncSession = Depends(get_db),
):
    """Create a new application."""
    existing = await db.execute(select(Application).where(Application.code == app_in.code))
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Application code already exists",
        )

    app = Application(
        name=app_in.name,
        code=app_in.code,
        description=app_in.description,
        url=app_in.url,
        icon=app_in.icon,
        sort_order=app_in.sort_order,
        status=app_in.status,
    )
    db.add(app)
    await db.flush()
    await db.refresh(app)
    return ApplicationResponse.model_validate(app)


@router.put("/{app_id}", response_model=ApplicationResponse)
async def update_application(
    app_id: int,
    app_in: ApplicationUpdate,
    current_user: User = Depends(require_permissions("btn:application:edit")),
    db: AsyncSession = Depends(get_db),
):
    """Update an existing application."""
    result = await db.execute(select(Application).where(Application.id == app_id))
    app = result.scalar_one_or_none()
    if not app:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")

    if app_in.name is not None:
        app.name = app_in.name
    if app_in.code is not None:
        app.code = app_in.code
    if app_in.description is not None:
        app.description = app_in.description
    if app_in.url is not None:
        app.url = app_in.url
    if app_in.icon is not None:
        app.icon = app_in.icon
    if app_in.sort_order is not None:
        app.sort_order = app_in.sort_order
    if app_in.status is not None:
        app.status = app_in.status

    await db.flush()
    await db.refresh(app)
    return ApplicationResponse.model_validate(app)


@router.delete("/{app_id}")
async def delete_application(
    app_id: int,
    current_user: User = Depends(require_permissions("btn:application:delete")),
    db: AsyncSession = Depends(get_db),
):
    """Delete an application."""
    result = await db.execute(select(Application).where(Application.id == app_id))
    app = result.scalar_one_or_none()
    if not app:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")

    permission_result = await db.execute(
        select(Permission).where(Permission.code == f"app:{app.code}")
    )
    permission = permission_result.scalar_one_or_none()
    if permission:
        await db.delete(permission)

    await db.delete(app)
    await db.flush()
    return {"message": "Application deleted successfully"}
