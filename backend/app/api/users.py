from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.security import hash_password
from app.models.user import User
from app.models.role import Role
from app.schemas.user import UserCreate, UserUpdate, UserResponse, UserListResponse, RoleBasic
from app.api.deps import get_current_user, require_permissions

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("", response_model=UserListResponse)
async def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    username: Optional[str] = Query(None),
    status_filter: Optional[int] = Query(None, alias="status"),
    current_user: User = Depends(require_permissions("menu:user")),
    db: AsyncSession = Depends(get_db),
):
    """List users with pagination and optional filters."""
    query = select(User).options(selectinload(User.roles))
    count_query = select(func.count(User.id))

    if username:
        query = query.where(User.username.contains(username))
        count_query = count_query.where(User.username.contains(username))
    if status_filter is not None:
        query = query.where(User.status == status_filter)
        count_query = count_query.where(User.status == status_filter)

    # Get total count
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Get paginated results
    query = query.order_by(User.id.desc()).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    users = result.scalars().all()

    return UserListResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=[
            UserResponse(
                id=u.id,
                username=u.username,
                nickname=u.nickname,
                email=u.email,
                phone=u.phone,
                avatar=u.avatar,
                status=u.status,
                created_at=u.created_at,
                updated_at=u.updated_at,
                roles=[RoleBasic(id=r.id, name=r.name, code=r.code) for r in u.roles],
            )
            for u in users
        ],
    )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    current_user: User = Depends(require_permissions("menu:user")),
    db: AsyncSession = Depends(get_db),
):
    """Get a single user by ID."""
    result = await db.execute(
        select(User).options(selectinload(User.roles)).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return UserResponse(
        id=user.id,
        username=user.username,
        nickname=user.nickname,
        email=user.email,
        phone=user.phone,
        avatar=user.avatar,
        status=user.status,
        created_at=user.created_at,
        updated_at=user.updated_at,
        roles=[RoleBasic(id=r.id, name=r.name, code=r.code) for r in user.roles],
    )


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_in: UserCreate,
    current_user: User = Depends(require_permissions("btn:user:create")),
    db: AsyncSession = Depends(get_db),
):
    """Create a new user."""
    # Check if username already exists
    existing = await db.execute(select(User).where(User.username == user_in.username))
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists",
        )

    user = User(
        username=user_in.username,
        password_hash=hash_password(user_in.password),
        nickname=user_in.nickname,
        email=user_in.email,
        phone=user_in.phone,
        avatar=user_in.avatar,
        status=user_in.status,
    )

    # Assign roles if provided
    if user_in.role_ids:
        result = await db.execute(select(Role).where(Role.id.in_(user_in.role_ids)))
        roles = result.scalars().all()
        user.roles = list(roles)

    db.add(user)
    await db.flush()
    await db.refresh(user)

    return UserResponse(
        id=user.id,
        username=user.username,
        nickname=user.nickname,
        email=user.email,
        phone=user.phone,
        avatar=user.avatar,
        status=user.status,
        created_at=user.created_at,
        updated_at=user.updated_at,
        roles=[RoleBasic(id=r.id, name=r.name, code=r.code) for r in user.roles],
    )


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_in: UserUpdate,
    current_user: User = Depends(require_permissions("btn:user:edit")),
    db: AsyncSession = Depends(get_db),
):
    """Update an existing user."""
    result = await db.execute(
        select(User).options(selectinload(User.roles)).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Update fields
    if user_in.nickname is not None:
        user.nickname = user_in.nickname
    if user_in.email is not None:
        user.email = user_in.email
    if user_in.phone is not None:
        user.phone = user_in.phone
    if user_in.avatar is not None:
        user.avatar = user_in.avatar
    if user_in.status is not None:
        user.status = user_in.status
    if user_in.password is not None:
        user.password_hash = hash_password(user_in.password)

    # Update roles if provided
    if user_in.role_ids is not None:
        result = await db.execute(select(Role).where(Role.id.in_(user_in.role_ids)))
        roles = result.scalars().all()
        user.roles = list(roles)

    await db.flush()
    await db.refresh(user)

    return UserResponse(
        id=user.id,
        username=user.username,
        nickname=user.nickname,
        email=user.email,
        phone=user.phone,
        avatar=user.avatar,
        status=user.status,
        created_at=user.created_at,
        updated_at=user.updated_at,
        roles=[RoleBasic(id=r.id, name=r.name, code=r.code) for r in user.roles],
    )


@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    current_user: User = Depends(require_permissions("btn:user:delete")),
    db: AsyncSession = Depends(get_db),
):
    """Delete a user by ID."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if user.username == "admin":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete the admin user",
        )

    await db.delete(user)
    await db.flush()
    return {"message": "User deleted successfully"}
