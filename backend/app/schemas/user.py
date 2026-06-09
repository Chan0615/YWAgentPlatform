from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    username: str
    password: str
    nickname: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    avatar: Optional[str] = None
    status: int = 1
    role_ids: Optional[List[int]] = None


class UserUpdate(BaseModel):
    nickname: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    avatar: Optional[str] = None
    status: Optional[int] = None
    password: Optional[str] = None
    role_ids: Optional[List[int]] = None


class RoleBasic(BaseModel):
    id: int
    name: str
    code: str

    class Config:
        from_attributes = True


class PermissionBasic(BaseModel):
    id: int
    code: str
    name: str
    type: str

    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    id: int
    username: str
    nickname: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    avatar: Optional[str] = None
    status: int
    created_at: datetime
    updated_at: datetime
    roles: List[RoleBasic] = []

    class Config:
        from_attributes = True


class UserInfoResponse(BaseModel):
    """Used for /auth/userinfo - includes permissions."""
    id: int
    username: str
    nickname: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    avatar: Optional[str] = None
    status: int
    roles: List[RoleBasic] = []
    permissions: List[str] = []

    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[UserResponse]
