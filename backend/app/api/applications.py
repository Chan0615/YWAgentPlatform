from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import get_db
from app.models.application import Application
from app.models.permission import Permission
from app.models.role import Role
from app.models.user import User
from app.schemas.application import (
    ApplicationCreate, ApplicationUpdate, ApplicationResponse, ApplicationListResponse,
    AssignApplicationRolesRequest,
)
from app.api.deps import get_current_user, require_permissions, get_user_permissions

router = APIRouter(prefix="/applications", tags=["Applications"])


async def _build_application_response(app: Application, db: AsyncSession) -> ApplicationResponse:
    permission_result = await db.execute(
        select(Permission).where(Permission.code == f"app:{app.code}")
    )
    permission = permission_result.scalar_one_or_none()

    visible_role_ids: List[int] = []
    if permission:
        roles_result = await db.execute(
            select(Role.id)
            .join(Role.permissions)
            .where(Permission.id == permission.id)
        )
        visible_role_ids = list(roles_result.scalars().all())

    return ApplicationResponse(
        id=app.id,
        name=app.name,
        code=app.code,
        description=app.description,
        url=app.url,
        icon=app.icon,
        sort_order=app.sort_order,
        status=app.status,
        created_at=app.created_at,
        updated_at=app.updated_at,
        visible_role_ids=visible_role_ids,
    )


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
        items=[await _build_application_response(a, db) for a in apps],
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
    return [await _build_application_response(a, db) for a in apps]


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

    return await _build_application_response(app, db)


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

    permission = Permission(
        parent_id=None,
        name=app_in.name,
        code=f"app:{app_in.code}",
        type="app",
        path=None,
        icon=app_in.icon,
        sort_order=app_in.sort_order,
        status=app_in.status,
    )
    db.add(permission)

    await db.refresh(app)
    return await _build_application_response(app, db)


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

    # Check code uniqueness if changing
    if app_in.code is not None and app_in.code != app.code:
        existing = await db.execute(
            select(Application).where(Application.code == app_in.code, Application.id != app_id)
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Application code already exists",
            )

    permission_result = await db.execute(
        select(Permission).where(Permission.code == f"app:{app.code}")
    )
    permission = permission_result.scalar_one_or_none()

    old_code = app.code

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

    if permission:
        permission.name = app.name
        permission.code = f"app:{app.code}"
        permission.icon = app.icon
        permission.sort_order = app.sort_order
        permission.status = app.status
    elif old_code != app.code or app_in.name is not None:
        db.add(
            Permission(
                parent_id=None,
                name=app.name,
                code=f"app:{app.code}",
                type="app",
                path=None,
                icon=app.icon,
                sort_order=app.sort_order,
                status=app.status,
            )
        )

    await db.flush()
    await db.refresh(app)
    return await _build_application_response(app, db)


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


@router.post("/{app_id}/visible-roles", response_model=ApplicationResponse)
async def assign_visible_roles(
    app_id: int,
    body: AssignApplicationRolesRequest,
    current_user: User = Depends(require_permissions("btn:application:edit")),
    db: AsyncSession = Depends(get_db),
):
    app_result = await db.execute(select(Application).where(Application.id == app_id))
    app = app_result.scalar_one_or_none()
    if not app:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")

    permission_result = await db.execute(
        select(Permission).where(Permission.code == f"app:{app.code}")
    )
    permission = permission_result.scalar_one_or_none()
    if not permission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application permission not found")

    roles_result = await db.execute(
        select(Role).where(Role.id.in_(body.role_ids)).options()
    )
    roles = roles_result.scalars().all()

    current_roles_result = await db.execute(
        select(Role).join(Role.permissions).where(Permission.id == permission.id)
    )
    current_roles = current_roles_result.scalars().all()

    for role in current_roles:
        role.permissions = [p for p in role.permissions if p.id != permission.id]

    for role in roles:
        if permission not in role.permissions:
            role.permissions.append(permission)

    await db.flush()
    await db.refresh(app)
    return await _build_application_response(app, db)
