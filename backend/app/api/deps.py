from typing import List, Optional
from functools import wraps

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.security import decode_token
from app.models.user import User

security_scheme = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Extract and validate the current user from the JWT access token."""
    token = credentials.credentials
    payload = decode_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )

    result = await db.execute(
        select(User).options(selectinload(User.roles)).where(User.id == int(user_id))
    )
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if user.status != 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled",
        )

    return user


def require_permissions(*required_codes: str):
    """
    Dependency factory that checks if the current user has ALL the specified permission codes.
    Usage: Depends(require_permissions("btn:user:create"))
    """

    async def permission_checker(
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
    ) -> User:
        # Super admin (role code 'admin') bypasses permission checks
        user_role_codes = [role.code for role in current_user.roles]
        if "admin" in user_role_codes:
            return current_user

        # Collect all permission codes for the user's roles
        from app.models.role import Role
        from app.models.permission import Permission
        from sqlalchemy.orm import selectinload

        user_permissions: set = set()
        for role in current_user.roles:
            # Roles are already loaded with selectinload, but permissions need explicit loading
            result = await db.execute(
                select(Role).options(selectinload(Role.permissions)).where(Role.id == role.id)
            )
            role_obj = result.scalar_one_or_none()
            if role_obj:
                for perm in role_obj.permissions:
                    if perm.status == 1:
                        user_permissions.add(perm.code)

        # Check all required permissions
        for code in required_codes:
            if code not in user_permissions:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission denied: {code} required",
                )

        return current_user

    return permission_checker


async def get_user_permissions(user: User, db: AsyncSession) -> List[str]:
    """Get all permission codes for a user across all their roles."""
    from app.models.role import Role
    from sqlalchemy.orm import selectinload

    user_role_codes = [role.code for role in user.roles]
    if "admin" in user_role_codes:
        # Admin gets all permissions
        from app.models.permission import Permission
        result = await db.execute(select(Permission).where(Permission.status == 1))
        permissions = result.scalars().all()
        return [p.code for p in permissions]

    permission_codes: set = set()
    for role in user.roles:
        result = await db.execute(
            select(Role).options(selectinload(Role.permissions)).where(Role.id == role.id)
        )
        role_obj = result.scalar_one_or_none()
        if role_obj:
            for perm in role_obj.permissions:
                if perm.status == 1:
                    permission_codes.add(perm.code)

    return list(permission_codes)
