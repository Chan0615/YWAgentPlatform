from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.models.permission import Permission
from app.models.user import User
from app.schemas.permission import (
    PermissionCreate, PermissionUpdate, PermissionResponse, PermissionTreeResponse,
)
from app.api.deps import get_current_user, require_permissions

router = APIRouter(prefix="/permissions", tags=["Permissions"])


def _build_tree(permissions: List[Permission], parent_id=None) -> List[PermissionTreeResponse]:
    """Build a tree structure from a flat list of permissions."""
    tree = []
    for perm in permissions:
        if perm.parent_id == parent_id:
            children = _build_tree(permissions, perm.id)
            node = PermissionTreeResponse(
                id=perm.id,
                parent_id=perm.parent_id,
                name=perm.name,
                code=perm.code,
                type=perm.type,
                path=perm.path,
                icon=perm.icon,
                sort_order=perm.sort_order,
                status=perm.status,
                created_at=perm.created_at,
                updated_at=perm.updated_at,
                children=children,
            )
            tree.append(node)
    tree.sort(key=lambda x: x.sort_order)
    return tree


@router.get("/tree", response_model=List[PermissionTreeResponse])
async def get_permission_tree(
    current_user: User = Depends(require_permissions("menu:system:permission")),
    db: AsyncSession = Depends(get_db),
):
    """Get all permissions as a tree structure."""
    result = await db.execute(select(Permission).order_by(Permission.sort_order))
    permissions = result.scalars().all()
    return _build_tree(list(permissions), parent_id=None)


@router.get("", response_model=List[PermissionResponse])
async def list_permissions(
    current_user: User = Depends(require_permissions("menu:system:permission")),
    db: AsyncSession = Depends(get_db),
):
    """List all permissions flat."""
    result = await db.execute(select(Permission).order_by(Permission.sort_order))
    permissions = result.scalars().all()
    return [PermissionResponse.model_validate(p) for p in permissions]


@router.get("/{permission_id}", response_model=PermissionResponse)
async def get_permission(
    permission_id: int,
    current_user: User = Depends(require_permissions("menu:system:permission")),
    db: AsyncSession = Depends(get_db),
):
    """Get a single permission by ID."""
    result = await db.execute(select(Permission).where(Permission.id == permission_id))
    perm = result.scalar_one_or_none()
    if not perm:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Permission not found")
    return PermissionResponse.model_validate(perm)


@router.post("", response_model=PermissionResponse, status_code=status.HTTP_201_CREATED)
async def create_permission(
    perm_in: PermissionCreate,
    current_user: User = Depends(require_permissions("btn:permission:create")),
    db: AsyncSession = Depends(get_db),
):
    """Create a new permission."""
    # Check code uniqueness
    existing = await db.execute(select(Permission).where(Permission.code == perm_in.code))
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Permission code already exists",
        )

    # Validate parent exists if provided
    if perm_in.parent_id is not None:
        parent = await db.execute(select(Permission).where(Permission.id == perm_in.parent_id))
        if not parent.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Parent permission not found",
            )

    # Validate type
    if perm_in.type not in ("app", "menu", "button"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Permission type must be: app, menu, or button",
        )

    perm = Permission(
        parent_id=perm_in.parent_id,
        name=perm_in.name,
        code=perm_in.code,
        type=perm_in.type,
        path=perm_in.path,
        icon=perm_in.icon,
        sort_order=perm_in.sort_order,
        status=perm_in.status,
    )
    db.add(perm)
    await db.flush()
    await db.refresh(perm)
    return PermissionResponse.model_validate(perm)


@router.put("/{permission_id}", response_model=PermissionResponse)
async def update_permission(
    permission_id: int,
    perm_in: PermissionUpdate,
    current_user: User = Depends(require_permissions("btn:permission:edit")),
    db: AsyncSession = Depends(get_db),
):
    """Update an existing permission."""
    result = await db.execute(select(Permission).where(Permission.id == permission_id))
    perm = result.scalar_one_or_none()
    if not perm:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Permission not found")

    # Check code uniqueness if changing
    if perm_in.code is not None and perm_in.code != perm.code:
        existing = await db.execute(
            select(Permission).where(Permission.code == perm_in.code, Permission.id != permission_id)
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Permission code already exists",
            )

    if perm_in.parent_id is not None:
        if perm_in.parent_id == permission_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Permission cannot be its own parent",
            )
        perm.parent_id = perm_in.parent_id
    if perm_in.name is not None:
        perm.name = perm_in.name
    if perm_in.code is not None:
        perm.code = perm_in.code
    if perm_in.type is not None:
        if perm_in.type not in ("app", "menu", "button"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Permission type must be: app, menu, or button",
            )
        perm.type = perm_in.type
    if perm_in.path is not None:
        perm.path = perm_in.path
    if perm_in.icon is not None:
        perm.icon = perm_in.icon
    if perm_in.sort_order is not None:
        perm.sort_order = perm_in.sort_order
    if perm_in.status is not None:
        perm.status = perm_in.status

    await db.flush()
    await db.refresh(perm)
    return PermissionResponse.model_validate(perm)


@router.delete("/{permission_id}")
async def delete_permission(
    permission_id: int,
    current_user: User = Depends(require_permissions("btn:permission:delete")),
    db: AsyncSession = Depends(get_db),
):
    """Delete a permission. Also removes it from any role assignments."""
    result = await db.execute(select(Permission).where(Permission.id == permission_id))
    perm = result.scalar_one_or_none()
    if not perm:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Permission not found")

    # Check if it has children
    children_result = await db.execute(
        select(Permission).where(Permission.parent_id == permission_id)
    )
    if children_result.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete permission with children. Delete children first.",
        )

    await db.delete(perm)
    await db.flush()
    return {"message": "Permission deleted successfully"}
