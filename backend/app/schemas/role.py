from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel


class RoleCreate(BaseModel):
    name: str
    code: str
    description: Optional[str] = None
    status: int = 1


class RoleUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    description: Optional[str] = None
    status: Optional[int] = None


class PermissionBasicInRole(BaseModel):
    id: int
    name: str
    code: str
    type: str

    class Config:
        from_attributes = True


class RoleResponse(BaseModel):
    id: int
    name: str
    code: str
    description: Optional[str] = None
    status: int
    created_at: datetime
    permissions: List[PermissionBasicInRole] = []

    class Config:
        from_attributes = True


class RoleListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[RoleResponse]


class AssignPermissionsRequest(BaseModel):
    permission_ids: List[int]
