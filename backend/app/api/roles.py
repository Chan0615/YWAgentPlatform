from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models.role import Role
from app.models.permission import Permission
from app.models.user import User
from app.schemas.role import (
    RoleCreate, RoleUpdate, RoleResponse, RoleListResponse,
    AssignPermissionsRequest, PermissionBasicInRole,
)
from app.api.deps import get_current_user, require_permissions

router = APIRouter(prefix="/roles", tags=["Roles"])


@router.get("", response_model=RoleListResponse)
async def list_roles(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    name: Optional[str] = Query(None),
    current_user: User = Depends(require_permissions("menu:role")),
    db: AsyncSession = Depends(get_db),
):
    """List roles with pagination."""
    query = select(Role).options(selectinload(Role.permissions))
    count_query = select(func.count(Role.id))

    if name:
        query = query.where(Role.name.contains(name))
        count_query = count_query.where(Role.name.contains(name))

    total_result = await db.execute(count_query)
    total = total_result.scalar()

    query = query.order_by(Role.id.asc()).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    roles = result.scalars().all()

    return RoleListResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=[
            RoleResponse(
                id=r.id,
                name=r.name,
                code=r.code,
                description=r.description,
                status=r.status,
                created_at=r.created_at,
                updated_at=r.updated_at,
                permissions=[
                    PermissionBasicInRole(id=p.id, name=p.name, code=p.code, type=p.type)
                    for p in r.permissions
                ],
            )
            for r in roles
        ],
    )


@router.get("/{role_id}", response_model=RoleResponse)
async def get_role(
    role_id: int,
    current_user: User = Depends(require_permissions("menu:role")),
    db: AsyncSession = Depends(get_db),
):
    """Get a single role by ID."""
    result = await db.execute(
        select(Role).options(selectinload(Role.permissions)).where(Role.id == role_id)
    )
    role = result.scalar_one_or_none()
    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")

    return RoleResponse(
        id=role.id,
        name=role.name,
        code=role.code,
        description=role.description,
        status=role.status,
        created_at=role.created_at,
        updated_at=role.updated_at,
        permissions=[
            PermissionBasicInRole(id=p.id, name=p.name, code=p.code, type=p.type)
            for p in role.permissions
        ],
    )


@router.post("", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
async def create_role(
    role_in: RoleCreate,
    current_user: User = Depends(require_permissions("btn:role:create")),
    db: AsyncSession = Depends(get_db),
):
    """Create a new role."""
    # Check uniqueness
    existing = await db.execute(
        select(Role).where((Role.name == role_in.name) | (Role.code == role_in.code))
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role name or code already exists",
        )

    role = Role(
        name=role_in.name,
        code=role_in.code,
        description=role_in.description,
        status=role_in.status,
    )
    db.add(role)
    await db.flush()
    await db.refresh(role)

    return RoleResponse(
        id=role.id,
        name=role.name,
        code=role.code,
        description=role.description,
        status=role.status,
        created_at=role.created_at,
        updated_at=role.updated_at,
        permissions=[],
    )


@router.put("/{role_id}", response_model=RoleResponse)
async def update_role(
    role_id: int,
    role_in: RoleUpdate,
    current_user: User = Depends(require_permissions("btn:role:edit")),
    db: AsyncSession = Depends(get_db),
):
    """Update an existing role."""
    result = await db.execute(
        select(Role).options(selectinload(Role.permissions)).where(Role.id == role_id)
    )
    role = result.scalar_one_or_none()
    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")

    if role_in.name is not None:
        role.name = role_in.name
    if role_in.code is not None:
        role.code = role_in.code
    if role_in.description is not None:
        role.description = role_in.description
    if role_in.status is not None:
        role.status = role_in.status

    await db.flush()
    await db.refresh(role)

    return RoleResponse(
        id=role.id,
        name=role.name,
        code=role.code,
        description=role.description,
        status=role.status,
        created_at=role.created_at,
        updated_at=role.updated_at,
        permissions=[
            PermissionBasicInRole(id=p.id, name=p.name, code=p.code, type=p.type)
            for p in role.permissions
        ],
    )


@router.delete("/{role_id}")
async def delete_role(
    role_id: int,
    current_user: User = Depends(require_permissions("btn:role:delete")),
    db: AsyncSession = Depends(get_db),
):
    """Delete a role by ID."""
    result = await db.execute(select(Role).where(Role.id == role_id))
    role = result.scalar_one_or_none()
    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")

    if role.code == "admin":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete the admin role",
        )

    await db.delete(role)
    await db.flush()
    return {"message": "Role deleted successfully"}


@router.post("/{role_id}/permissions", response_model=RoleResponse)
async def assign_permissions(
    role_id: int,
    body: AssignPermissionsRequest,
    current_user: User = Depends(require_permissions("btn:role:assign_perm")),
    db: AsyncSession = Depends(get_db),
):
    """Assign permissions to a role (replaces existing permissions)."""
    result = await db.execute(
        select(Role).options(selectinload(Role.permissions)).where(Role.id == role_id)
    )
    role = result.scalar_one_or_none()
    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")

    # Fetch the permissions
    perm_result = await db.execute(
        select(Permission).where(Permission.id.in_(body.permission_ids))
    )
    permissions = perm_result.scalars().all()

    role.permissions = list(permissions)
    await db.flush()
    await db.refresh(role)

    return RoleResponse(
        id=role.id,
        name=role.name,
        code=role.code,
        description=role.description,
        status=role.status,
        created_at=role.created_at,
        updated_at=role.updated_at,
        permissions=[
            PermissionBasicInRole(id=p.id, name=p.name, code=p.code, type=p.type)
            for p in role.permissions
        ],
    )
